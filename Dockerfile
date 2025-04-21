FROM python:3.13-alpine3.21

RUN apk add --no-cache postgresql17-client

COPY --chmod=755 welephant.py /

ENTRYPOINT [ "/welephant.py" ]
