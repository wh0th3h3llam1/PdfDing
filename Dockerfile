# The frontend build image , used to create the css and js files
FROM node:22.3.0-bookworm-slim as npm-build

WORKDIR /build

COPY package.json package-lock.json tailwind.config.js ./
COPY pdfding ./pdfding

RUN mkdir ./js && mkdir ./css
RUN npm ci
RUN npm run build
RUN npx tailwindcss -i pdfding/static/css/input.css -o css/tailwind.css -c tailwind.config.js --minify
RUN rm pdfding/static/css/input.css && mv -t pdfding/static js css

# The build image, used to build the virtual python environment
FROM python:3.12.4-slim as python-build

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12.4-slim as runtime

# add user for running the container as non-root
ARG USERNAME=nonroot
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/home/$USERNAME/.venv  PATH="/home/$USERNAME/.venv/bin:$PATH"

COPY --from=python-build /app/.venv ${VIRTUAL_ENV}
COPY --from=npm-build /build/pdfding /home/$USERNAME/pdfding

WORKDIR /home/$USERNAME/pdfding

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:5000"]

