FROM node:16.16.0-alpine

WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci --no-audit --no-fund && \
    npm cache clean --force

COPY . .

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
