#!/bin/bash
export BASE_URL=$PREFIX
[[ $BASE_URL ]] && { cd /app/pan/static && npm install && npm run build; cd /app; }
pan watch --config /etc/pan/config.cfg &
export pid=$!
pan serve --config /etc/pan/config.cfg --port=8080 --host=0.0.0.0 --prefix=$BASE_URL -vvv
kill -9 $pid
