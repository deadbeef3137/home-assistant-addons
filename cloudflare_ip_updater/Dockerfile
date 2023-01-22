ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer = "Jaime Quiroga <tecnico@neodomo.es>"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --update bash jq curl s6-overlay && rm -rf /var/cache/apk/*

# copy cloudflare.sh and config.json
COPY cloudflare.sh /rootfs/cloudflare.sh
COPY config.json /rootfs/config.json

RUN chmod a+x /rootfs/cloudflare.sh

# create s6-services directory
RUN mkdir -p /rootfs/etc/services.d/cloudflare

# Create s6-services run file
RUN echo "#!/bin/bash" > /rootfs/etc/services.d/cloudflare/run \
    && echo "exec /rootfs/cloudflare.sh" >> /rootfs/etc/services.d/cloudflare/run

RUN chmod +x /rootfs/etc/services.d/cloudflare/run

# Add Tini to handle signals and reap zombies
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-armhf /tini
RUN chmod +x /tini

# Run s6-svscan with Tini
ENTRYPOINT ["/tini", "-s", "--", "/usr/bin/s6-svscan", "/rootfs/etc/services.d"]
