ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer="Jaime Quiroga tecnico@neodomo.es"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV LANG C.UTF-8

RUN apk update && \
apk add --no-cache bash jq iw hostapd s6-overlay networkmanager net-tools sudo dnsmasq && \
rm -rf /var/cache/apk/*

COPY hostapd.conf /rootfs/hostapd.conf
COPY dnsmasq.conf /rootfs/dnsmasq.conf
COPY config.json /rootfs/config.json
COPY haosap.sh /rootfs/haosap.sh

RUN chmod a+x /rootfs/haosap.sh


# create s6-services directory
RUN mkdir -p /rootfs/etc/services.d/haosap

# Create s6-services run file
RUN echo "#!/bin/bash" > /rootfs/etc/services.d/haosap/run \
    && echo "exec /rootfs/haosap.sh" >> /rootfs/etc/services.d/haosap/run

RUN chmod +x /rootfs/etc/services.d/haosap/run

# Add Tini to handle signals and reap zombies
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-armhf /tini
RUN chmod +x /tini

# Run s6-svscan with Tini
ENTRYPOINT ["/tini", "-s", "--", "/usr/bin/s6-svscan", "/rootfs/etc/services.d"]
