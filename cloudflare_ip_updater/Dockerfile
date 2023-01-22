ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer = "Jaime Quiroga <tecnico@neodomo.es>"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --update bash jq curl s6-overlay && rm -rf /var/cache/apk/*

# Copy cloudflare script
COPY cloudflare.sh /rootfs/
RUN chmod a+x /rootfs/cloudflare.sh

# Copy config file
COPY config.json /rootfs/

# Create s6 service
RUN echo "#!/bin/bash" > /rootfs/s6-services \
    && echo "exec /rootfs/cloudflare.sh" >> /rootfs/s6-services

# Download and set Tini as entrypoint
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-armhf /tini
RUN chmod +x /tini

# Set s6-svscan as command
ENTRYPOINT ["/tini", "--", "/usr/bin/s6-svscan", "/rootfs/etc/services.d"]
