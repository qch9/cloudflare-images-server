FROM python:3.10.8-alpine3.16

RUN mkdir -p /var/www/images

WORKDIR /opt/code/cloudflare-images-server

RUN apk update
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --update --no-cache libwebp-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ .
