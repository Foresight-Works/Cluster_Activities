#!/bin/bash

cd /home/rnd/Work/Analysis/Graphs_code
echo `pwd`
kill -9 `ps -eaf | grep cluster_service002 | grep -v grep | awk '{print $2}'`

python cluster_service.py 2>&1 >> web_api.log &

exit 0
