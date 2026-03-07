#!/bin/bash
TIMEOUT=60
while [ $TIMEOUT -gt 0 ]; do
    curl -sf http://localhost:3000/signalk > /dev/null && exit 0
    sleep 2
    TIMEOUT=$((TIMEOUT - 2))
done
exit 1
