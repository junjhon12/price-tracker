import logging
import re
from dataclasses import dataclass

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# Currency pattern: matches $1,234.56 or 1,234.56 USD etc.
PRICE_RE = re.compile(r"\$\s*(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)")

# ── Site-specific selector maps ───────────────────────────────────────────────
# Each entry: (price_selector, title_selector, image_selector)
SITE_SELECTORS: dict[str, tuple[str, str, str]] = {
    "amazon.com": (
        # price: try the featured offer block, then the core price widget
        "#corePrice_feature_div .a-price .a-offscreen, "
        "#price_inside_buybox, "
        "#priceblock_ourprice, "
        "#priceblock_dealprice, "
        ".a-price .a-offscreen",
        "#productTitle",
        "#imgTagWrappingLink img, #landingImage",
    ),
    "bestbuy.com": (
        ".priceView-customer-price span[aria-hidden='true'], "
        ".priceView-hero-price span:first-child",
        ".sku-title h1",
        ".primary-image-container img, .picture-container img",
    ),
}


@dataclass
class ScrapeResult:
    url: str
    title: str | None
    image_url: str | None
    price: float | None
    error: str | None


def _match_domain(url: str) -> str | None:
    for domain in SITE_SELECTORS:
        if domain in url:
            return domain
    return None


def _parse_price(raw: str) -> float | None:
    m = PRICE_RE.search(raw)
    if m:
        return float(m.group(1).replace(",", ""))
    # bare number like "229.97"
    try:
        v = float(raw.strip().replace(",", ""))
        if 0 < v < 1_000_000:
            return v
    except ValueError:
        pass
    return None


async def _extract_price_site_specific(page: Page, price_selector: str) -> float | None:
    try:
        el = page.locator(price_selector).first
        raw = await el.text_content(timeout=3000)
        if raw:
            return _parse_price(raw)
    except Exception:
        pass
    return None


async def _extract_price_jsonld(page: Page) -> tuple[float | None, str | None, str | None]:
    """Parse JSON-LD Product schema for price, name, and image."""
    try:
        results = await page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
            for (const s of scripts) {
                try {
                    const data = JSON.parse(s.textContent);
                    const items = Array.isArray(data) ? data : [data];
                    for (const item of items) {
                        const t = item['@type'];
                        if (t === 'Product' || (Array.isArray(t) && t.includes('Product'))) {
                            const offers = item.offers;
                            let price = null;
                            if (offers) {
                                const offer = Array.isArray(offers) ? offers[0] : offers;
                                price = offer.price ?? offer.lowPrice ?? null;
                            }
                            return {
                                price: price !== null ? parseFloat(String(price)) : null,
                                name: item.name ?? null,
                                image: Array.isArray(item.image) ? item.image[0] : (item.image ?? null),
                            };
                        }
                    }
                } catch(e) {}
            }
            return null;
        }""")
        if results and results.get("price") is not None:
            p = float(results["price"])
            name = results.get("name")
            img = results.get("image")
            return p, name, img
    except Exception:
        pass
    return None, None, None


async def _extract_price_meta(page: Page) -> float | None:
    for prop in ("og:price:amount", "product:price:amount"):
        try:
            content = await page.get_attribute(f'meta[property="{prop}"]', "content", timeout=2000)
            if content:
                v = _parse_price(content)
                if v:
                    return v
        except Exception:
            pass
    return None


async def _extract_price_regex(page: Page) -> float | None:
    """Look for price in price-labelled elements first, then scan full text."""
    try:
        result: float | None = await page.evaluate(r"""() => {
            const re = /\$\s*(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)/;
            const parse = t => {
                const m = re.exec(t);
                return m ? parseFloat(m[1].replace(',', '')) : null;
            };

            // Priority 1: elements whose class/id name contains price/cost/amount
            const hints = ['price', 'cost', 'amount', 'our-price', 'sale-price', 'current-price', 'product-price'];
            for (const hint of hints) {
                for (const el of document.querySelectorAll(`[class*="${hint}"], [id*="${hint}"]`)) {
                    // skip nav/footer to avoid shipping-threshold noise
                    if (el.closest('nav, footer, header')) continue;
                    const v = parse(el.textContent);
                    if (v !== null && v >= 5) return v;
                }
            }

            // Priority 2: full-text scan but ignore prices under $5
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                { acceptNode: n => n.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT }
            );
            let node;
            while ((node = walker.nextNode())) {
                // skip nav/footer
                if (node.parentElement && node.parentElement.closest('nav, footer, header')) continue;
                const v = parse(node.textContent);
                if (v !== null && v >= 5) return v;
            }
            return null;
        }""")
        return result
    except Exception:
        pass
    return None


async def _extract_title(page: Page, title_selector: str | None) -> str | None:
    if title_selector:
        try:
            el = page.locator(title_selector).first
            raw = await el.text_content(timeout=3000)
            if raw and raw.strip():
                return raw.strip()
        except Exception:
            pass
    # Fallback: og:title or document title
    try:
        og = await page.get_attribute('meta[property="og:title"]', "content", timeout=2000)
        if og:
            return og.strip()
    except Exception:
        pass
    return (await page.title()).strip() or None


async def _extract_image(page: Page, image_selector: str | None) -> str | None:
    if image_selector:
        try:
            el = page.locator(image_selector).first
            src = await el.get_attribute("src", timeout=3000)
            if src and src.startswith("http"):
                return src
        except Exception:
            pass
    # Fallback: og:image
    try:
        og = await page.get_attribute('meta[property="og:image"]', "content", timeout=2000)
        if og:
            return og.strip()
    except Exception:
        pass
    return None


async def scrape_product(url: str) -> ScrapeResult:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Let JS render
            await page.wait_for_timeout(2500)

            domain = _match_domain(url)
            price_sel, title_sel, image_sel = SITE_SELECTORS[domain] if domain else (None, None, None)

            price: float | None = None
            jsonld_title: str | None = None
            jsonld_image: str | None = None

            # Strategy 0: JSON-LD Product schema (most reliable for e-commerce)
            price, jsonld_title, jsonld_image = await _extract_price_jsonld(page)
            if price:
                logger.info("price via JSON-LD: %s → %s", url, price)

            # Strategy 1: site-specific selectors
            if price is None and price_sel:
                price = await _extract_price_site_specific(page, price_sel)
                if price:
                    logger.info("price via site selector: %s → %s", url, price)

            # Strategy 2: meta tags
            if price is None:
                price = await _extract_price_meta(page)
                if price:
                    logger.info("price via meta tag: %s → %s", url, price)

            # Strategy 3: currency regex scan
            if price is None:
                price = await _extract_price_regex(page)
                if price:
                    logger.info("price via regex: %s → %s", url, price)

            title = jsonld_title or await _extract_title(page, title_sel)
            image_url = jsonld_image or await _extract_image(page, image_sel)

            if price is None:
                return ScrapeResult(
                    url=url,
                    title=title,
                    image_url=image_url,
                    price=None,
                    error="Could not extract a price from this page",
                )

            return ScrapeResult(url=url, title=title, image_url=image_url, price=price, error=None)

        except PlaywrightTimeoutError as e:
            logger.error("timeout scraping %s: %s", url, e)
            return ScrapeResult(url=url, title=None, image_url=None, price=None, error=f"Page load timed out: {url}")
        except Exception as e:
            logger.exception("unexpected error scraping %s", url)
            return ScrapeResult(url=url, title=None, image_url=None, price=None, error=str(e))
        finally:
            await browser.close()
