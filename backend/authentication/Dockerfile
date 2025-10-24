FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app
COPY . .

RUN useradd --user-group user
RUN chown -R user:user /app && chmod -R 75 /app

EXPOSE 8000