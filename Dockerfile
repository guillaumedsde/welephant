FROM python:3-alpine

RUN apk add --no-cache postgresql17-client

COPY --chmod=755 welephant.py /

USER nobody
WORKDIR /data
VOLUME [ "/data" ]

ENTRYPOINT [ "/welephant.py" ]
CMD [ "--dumps-directory=/data" ]
