FROM alpine:3.19

RUN apk add --no-cache net-snmp-tools tzdata

WORKDIR /app
COPY  monitor_ups.sh ./app/monitor_ups.sh

RUN chmod +x ./app/monitor_ups.sh

CMD ["sh", "-c", "while true; do ./app/monitor_ups.sh; sleep 60; done"]