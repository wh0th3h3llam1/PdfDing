# The frontend build image , used to create the css and js files
FROM node:22.4.1-bookworm-slim AS npm-build

ARG PDFJS_VERSION=4.4.168

WORKDIR /build

COPY package.json package-lock.json tailwind.config.js ./
# pdfding is needed as tailwind creates the css files based on pdfding's html files
COPY pdfding ./pdfding

RUN apt-get update && apt-get install curl unzip -y
# get pdfjs
RUN curl -L https://github.com/mozilla/pdf.js/releases/download/v$PDFJS_VERSION/pdfjs-$PDFJS_VERSION-dist.zip > pdfjs.zip
RUN unzip pdfjs.zip -d pdfding/static/pdfjs
RUN rm -rf pdfding/static/pdfjs/web/locale \
    pdfding/static/pdfjs/web/standard_fonts \
    pdfding/static/pdfjs/web/compressed.tracemonkey-pldi-09.pdf
# get other dependecies
RUN npm ci && npm run build
RUN npx tailwindcss -i pdfding/static/css/input.css -o pdfding/static/css/tailwind.css -c tailwind.config.js --minify
# minify pdfjs js files
RUN for i in build/pdf.mjs build/pdf.sandbox.mjs build/pdf.worker.mjs web/viewer.mjs; \
    do npx terser pdfding/static/pdfjs/$i --compress -o pdfding/static/pdfjs/$i; done
RUN rm pdfding/static/css/input.css

# The build image, used to build the virtual python environment
FROM python:3.12.4-slim AS python-build

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# install python packages and clean up
RUN poetry install --without dev --without e2e --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && apt-get update \
    && apt-get install --no-install-recommends -y rename \
    && for i in pip setuptools wheel; do rm -rf /app/.venv/lib/python3.12/site-packages/$i*; done \
    && for i in pip pip-3.12 pip3 pip3.12; do rm /app/.venv/bin/$i; done

COPY --from=npm-build /build/pdfding pdfding
# prepare the static files for production
RUN poetry run pdfding/manage.py collectstatic

# remove django md5 hash from filenames of pdfjs as it will mess up the relative imports because of the whitenoise setup
RUN export PDFJS_PATH='/app/pdfding/staticfiles/pdfjs' \
    && for file_name in $(find $PDFJS_PATH -type f  -not -path "$PDFJS_PATH/web/images/*"); do rename 's/\.[a-zA-Z0-9]{12}\./\./' $file_name; done \
    && rename 's/LICENSE\.[a-zA-Z0-9]{12}$/LICENSE/' /app/pdfding/staticfiles/pdfjs/*

# remove the static files in another location
RUN rm -r pdfding/static/*

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12.4-slim AS runtime

# add user for running the container as non-root
ARG USERNAME=nonroot
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get update \
    && apt-get install --no-install-recommends -y libmagic1 netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/home/$USERNAME/.venv  PATH="/home/$USERNAME/.venv/bin:$PATH"

COPY --from=python-build /app/.venv ${VIRTUAL_ENV}
COPY --chown=$USERNAME --from=python-build /app/pdfding /home/$USERNAME/pdfding

WORKDIR /home/$USERNAME
COPY supervisord.conf ./
COPY --chmod=0555 bootstrap.sh ./

USER $USERNAME

CMD ["./bootstrap.sh"]
