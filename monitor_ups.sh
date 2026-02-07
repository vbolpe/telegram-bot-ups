#!/bin/bash

STATE_FILE="/tmp/ups_state"
SNMP_OPTS="-v3 -l authPriv -u readuser -a SHA -A $AUTH_PASS -x AES -X $PRIV_PASS"

# Get the current UPS status using snmpget
STATUS=$(snmpget $SNMP_OPTS "$UPS_IP" upsBasicBatteryStatus.0 -Ovq 2>/dev/null)

[ -z "$STATUS" ] && exit 0

PREV=$(cat "$STATE_FILE" 2>/dev/null)

if [ "$STATUS" != "$PREV" ]; then
    echo "$STATUS" > "$STATE_FILE"

    case "$STATUS" in
        2)
            echo "$(date) - UPS en estado NORMAL (línea)"
            ;;
        3)
            echo "$(date) - UPS en estado BATERÍA (sin corriente)"
            ;;
        4)
            echo "$(date) - UPS en estado BATERIA BAJA"
            ;;
        *)
            echo "$(date) - UPS en estado DESCONOCIDO: $STATUS"
            ;;

    esac
fi