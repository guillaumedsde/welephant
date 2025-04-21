FROM python:3-alpine AS base
RUN apk add --no-cache postgresql17-client
COPY --chmod=755 welephant.py /
WORKDIR /data
VOLUME [ "/data" ]

FROM base AS welephant
USER nobody
ENTRYPOINT [ "/welephant.py" ]

FROM base AS cron
RUN apk add --no-cache supercronic tzdata
COPY --chmod=644 <<EOF /crontab
28 14 * * * /welephant.py
EOF
USER nobody
ENTRYPOINT [ "/usr/bin/supercronic"]
CMD [ "/crontab" ]
