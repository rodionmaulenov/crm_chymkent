FROM python:3.9-alpine

WORKDIR crm_kazakhstan

COPY . /crm_kazakhstan

RUN apk update && \
    apk upgrade && \
    apk --no-cache add --virtual .build-deps \
    libpq-dev \
    libecpg-dev \
    openssl-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + && \
    runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" && \
    apk add --virtual .rundeps $runDeps && \
    apk del .build-deps


