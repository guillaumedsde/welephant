FROM python:3.13-alpine3.21

RUN apk add --no-cache postgresql17-client supercronic tzdata
COPY --chmod=755 welephant.py /

WORKDIR /data
VOLUME [ "/data" ]
USER nobody

ENTRYPOINT [ "/welephant.py" ]
