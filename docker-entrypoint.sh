#!/bin/bash
pan watch --config /etc/pan/config.cfg &
export pid=$!
pan serve --config /etc/pan/config.cfg --port=8080 --host=0.0.0.0 --prefix=$PREFIX -vvv
kill -9 $pid
