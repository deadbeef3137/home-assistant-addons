ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer = "Jaime Quiroga <tecnico@neodomo.es>"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --update bash jq curl s6-overlay && rm -rf /var/cache/apk/*

COPY cloudflare.sh /rootfs/
RUN chmod a+x /rootfs/cloudflare.sh

#Create s6-services
RUN echo "#!/bin/bash" > /rootfs/s6-services \
    && echo "exec /rootfs/cloudflare.sh" >> /rootfs/s6-services

CMD ["/rootfs/etc/services.d"]
