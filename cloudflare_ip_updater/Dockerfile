ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer = "Jaime Quiroga <tecnico@neodomo.es>"

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --update bash jq curl s6-overlay && rm -rf /var/cache/apk/*
    
COPY cloudflare.sh /
RUN chmod a+x /cloudflare.sh

#Create s6-services
RUN echo "#!/bin/bash" > s6-services \
    && echo "exec /cloudflare.sh" >> s6-services
RUN ln -s /s6-services /etc/services.d/cloudflare

CMD ["s6-svscan", "/etc/services.d"]
