#!/bin/sh

STATE_FILE="/tmp/ups_state"
LOG_FILE="/tmp/ups.log"
OID_BATTERY_STATUS="1.3.6.1.2.1.33.1.2.1.0"
SNMP_OPTS="-v3 -l authPriv -u $SNMP_USER -a MD5 -A $AUTH_PASS -x DES -X $PRIV_PASS -r 2 -t 2"

STATUS=$(snmpget $SNMP_OPTS "$UPS_IP" "$OID_BATTERY_STATUS" -Ovq 2>/dev/null)

[-z "$STATUS" ] && exit 0

snmpget -Ovq -v3 -l authPriv \
-u $SNMP_USER \
-a MD5 -A "$AUTH_PASS" \
-x DES -X "$PRIV_PASS" \
$UPS_IP 1.3.6.1.2.1.33.1.2.1.0


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