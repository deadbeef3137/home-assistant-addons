ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer="Jaime Quiroga <tecnico@neodomo.es>"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --update bash jq curl s6-overlay && \
    rm -rf /var/cache/apk/*

# Copy script and config file
COPY cloudflare.sh config.json /
RUN chmod a+x /cloudflare.sh

# Create s6-services
RUN echo "#!/bin/bash" > /rootfs/etc/services.d/cloudflare/run && \
    echo "exec /cloudflare.sh" >> /rootfs/etc/services.d/cloudflare/run

# Add Tini as entrypoint
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-armhf /tini
RUN chmod +x /tini

# Use Tini as entrypoint
ENTRYPOINT ["/tini", "--", "/usr/bin/s6-svscan", "/rootfs/etc/services.d"]
