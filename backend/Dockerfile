FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev

COPY app/ app/

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
