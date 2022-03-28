#!/bin/bash
echo 'Rnd@2143' | sudo -S -k service mysql start
kill -9 `ps -eaf | grep cluster_service | grep -v grep | awk '{print $2}'`
python cluster_service.py 2>&1 >> web_api.log &
exit 0
