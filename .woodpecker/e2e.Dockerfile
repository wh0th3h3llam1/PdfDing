# The frontend build image , used to create the css and js files
FROM node:22.4.1-bookworm-slim as npm-build

WORKDIR /build

COPY package.json package-lock.json tailwind.config.js ./
COPY pdfding/static .pdfding/static
# needed for poetry run
COPY pyproject.toml poetry.lock tailwind.config.js /app/

# get npm dependecies
RUN npm ci && npm run build && cp -r pdfding /app/

ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y python3 pipx libmagic1  \
    && pipx install poetry==1.8.3 \
    && poetry install --no-root \
    && poetry run playwright install-deps chromium \
    && poetry run playwright install chromium \
    && apt-get clean && rm -rf $POETRY_CACHE_DIR
