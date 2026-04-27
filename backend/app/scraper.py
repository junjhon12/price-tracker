import json
import logging
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

PRICE_RE = re.compile(r"\$\s*(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Site-specific CSS selectors: (price, title, image)
SITE_SELECTORS: dict[str, tuple[str, str, str]] = {
    "amazon.com": (
        "#corePrice_feature_div .a-offscreen, #price_inside_buybox, "
        "#priceblock_ourprice, #priceblock_dealprice, .a-price .a-offscreen",
        "#productTitle",
        "#landingImage, #imgTagWrappingLink img",
    ),
    "bestbuy.com": (
        ".priceView-customer-price span[aria-hidden='true'], "
        ".priceView-hero-price span:first-child",
        ".sku-title h1",
        ".primary-image-container img",
    ),
}

SKIP_TAGS = {"nav", "footer", "header", "script", "style", "noscript"}


@dataclass
class ScrapeResult:
    url: str
    title: str | None
    image_url: str | None
    price: float | None
    error: str | None


def _parse_price(raw: str) -> float | None:
    m = PRICE_RE.search(raw)
    if m:
        return float(m.group(1).replace(",", ""))
    try:
        v = float(raw.strip().replace(",", ""))
        if 0 < v < 1_000_000:
            return v
    except ValueError:
        pass
    return None


def _match_domain(url: str) -> str | None:
    for domain in SITE_SELECTORS:
        if domain in url:
            return domain
    return None


def _extract_jsonld(soup: BeautifulSoup) -> tuple[float | None, str | None, str | None]:
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type", "")
                if t == "Product" or (isinstance(t, list) and "Product" in t):
                    offers = item.get("offers")
                    price = None
                    if offers:
                        offer = offers[0] if isinstance(offers, list) else offers
                        raw = offer.get("price") or offer.get("lowPrice")
                        if raw is not None:
                            price = _parse_price(str(raw))
                    name = item.get("name")
                    img = item.get("image")
                    if isinstance(img, list):
                        img = img[0]
                    return price, name, img
        except Exception:
            continue
    return None, None, None


def _extract_site_price(soup: BeautifulSoup, selector: str) -> float | None:
    for sel in selector.split(","):
        el = soup.select_one(sel.strip())
        if el:
            v = _parse_price(el.get_text())
            if v:
                return v
    return None


def _extract_meta_price(soup: BeautifulSoup) -> float | None:
    for prop in ("og:price:amount", "product:price:amount"):
        tag = soup.find("meta", attrs={"property": prop})
        if tag and isinstance(tag, Tag):
            v = _parse_price(tag.get("content", ""))
            if v:
                return v
    return None


def _extract_regex_price(soup: BeautifulSoup) -> float | None:
    # Priority 1: elements whose class/id name hints at price
    hints = ["price", "cost", "amount", "our-price", "sale-price", "current-price", "product-price"]
    for hint in hints:
        for el in soup.find_all(class_=re.compile(hint, re.I)):
            if el.find_parent(SKIP_TAGS):
                continue
            v = _parse_price(el.get_text())
            if v and v >= 5:
                return v

    # Priority 2: full text scan, skip nav/header/footer, ignore <$5 (shipping thresholds)
    for el in soup.find_all(string=PRICE_RE):
        if el.find_parent(SKIP_TAGS):
            continue
        v = _parse_price(str(el))
        if v and v >= 5:
            return v
    return None


def _extract_title(soup: BeautifulSoup, selector: str | None) -> str | None:
    if selector:
        for sel in selector.split(","):
            el = soup.select_one(sel.strip())
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
    og = soup.find("meta", attrs={"property": "og:title"})
    if og and isinstance(og, Tag):
        return og.get("content", "").strip() or None
    return soup.title.string.strip() if soup.title and soup.title.string else None


def _extract_image(soup: BeautifulSoup, selector: str | None) -> str | None:
    if selector:
        for sel in selector.split(","):
            el = soup.select_one(sel.strip())
            if el and isinstance(el, Tag):
                src = el.get("src", "")
                if isinstance(src, str) and src.startswith("http"):
                    return src
    og = soup.find("meta", attrs={"property": "og:image"})
    if og and isinstance(og, Tag):
        return og.get("content", "").strip() or None
    return None


async def _fetch(url: str) -> str:
    """Fetch URL, falling back to verify=False if TLS verification fails (e.g. corporate proxies)."""
    for verify in (True, False):
        try:
            async with httpx.AsyncClient(
                headers=HEADERS,
                follow_redirects=True,
                timeout=20.0,
                verify=verify,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.text
        except httpx.ConnectError:
            if not verify:
                raise
            logger.debug("TLS verify failed for %s, retrying without verification", url)
        except (httpx.TimeoutException, httpx.HTTPStatusError):
            raise


async def scrape_product(url: str) -> ScrapeResult:
    try:
        html = await _fetch(url)
    except httpx.TimeoutException:
        return ScrapeResult(url=url, title=None, image_url=None, price=None, error=f"Page load timed out: {url}")
    except httpx.HTTPStatusError as e:
        return ScrapeResult(url=url, title=None, image_url=None, price=None, error=f"HTTP {e.response.status_code}: {url}")
    except Exception as e:
        logger.exception("fetch failed for %s", url)
        return ScrapeResult(url=url, title=None, image_url=None, price=None, error=str(e))

    soup = BeautifulSoup(html, "lxml")
    domain = _match_domain(url)
    price_sel, title_sel, image_sel = SITE_SELECTORS[domain] if domain else (None, None, None)

    # Strategy 0: JSON-LD
    price, jsonld_title, jsonld_image = _extract_jsonld(soup)
    if price:
        logger.info("price via JSON-LD: %s → %s", url, price)

    # Strategy 1: site-specific selectors
    if price is None and price_sel:
        price = _extract_site_price(soup, price_sel)
        if price:
            logger.info("price via site selector: %s → %s", url, price)

    # Strategy 2: meta tags
    if price is None:
        price = _extract_meta_price(soup)
        if price:
            logger.info("price via meta tag: %s → %s", url, price)

    # Strategy 3: regex scan
    if price is None:
        price = _extract_regex_price(soup)
        if price:
            logger.info("price via regex: %s → %s", url, price)

    title = jsonld_title or _extract_title(soup, title_sel)
    image_url = jsonld_image or _extract_image(soup, image_sel)

    if price is None:
        return ScrapeResult(url=url, title=title, image_url=image_url, price=None, error="Could not extract a price from this page")

    return ScrapeResult(url=url, title=title, image_url=image_url, price=price, error=None)
