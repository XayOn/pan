pan watch --config /etc/config.cfg
export pid=$!
pan serve --config test.conf --port=8080 --host=0.0.0.0 --prefix=$PREFIX
kill -9 $pid
