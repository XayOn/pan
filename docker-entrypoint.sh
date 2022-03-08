#!/bin/bash
pan serve --config /etc/pan/config.cfg --port=8080 --host=0.0.0.0 --prefix=$PREFIX
export pid=$!
pan watch --config /etc/pan/config.cfg &
kill -9 $pid
