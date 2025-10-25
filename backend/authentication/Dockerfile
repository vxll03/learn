FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app
COPY . .
RUN uv sync --frozen

RUN addgroup -S user && adduser -D user -G user
RUN chown -R user:user /app && chmod -R 750 /app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--port", "8000", "--host", "0.0.0.0"]