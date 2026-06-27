ARG BUILD_ARCH=aarch64
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base:latest

ARG BUILD_ARCH=aarch64
ARG BUILD_VERSION=0.1.0

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="Family Menu" \
    org.opencontainers.image.description="Local-first weekly dinner planning, grocery, and prep app" \
    org.opencontainers.image.source="https://github.com/kmcrandom/family-menu-ha" \
    org.opencontainers.image.licenses="MIT"

WORKDIR /app

RUN apk add --no-cache python3 py3-pip nodejs npm

COPY requirements.txt /app/requirements.txt
COPY frontend/package.json frontend/package-lock.json /app/frontend/
COPY frontend /app/frontend
COPY src /app/src
COPY data /app/data
COPY run.sh /run.sh

RUN python3 -m venv /opt/family-menu \
    && /opt/family-menu/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/family-menu/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && cd /app/frontend \
    && npm ci \
    && npm run build \
    && rm -rf /app/frontend/node_modules /root/.npm \
    && chmod a+x /run.sh

ENV FAMILY_MENU_HOST=0.0.0.0
ENV FAMILY_MENU_PORT=8081
ENV FAMILY_MENU_STATIC=/app/src/family_menu/static
ENV PATH=/opt/family-menu/bin:$PATH

CMD ["/run.sh"]
