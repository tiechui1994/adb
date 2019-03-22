#!/bin/bash

### BEGIN INIT INFO
# Provides:          signd
# Required-Start:    $local_fs
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: signd service
# Description:       signd service daemon
### END INIT INFO


check_env(){
    adb shell ls > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        bash /home/user/workspace/linux-tools/android/adb_connect.sh
    fi
}

do_start(){
    check_env

    export PYTHONPATH=/home/user/workspace/picture-search
    python3 /home/user/workspace/picture-search/service/signin.py > /dev/null 2>&1 &
}

do_stop() {
    pid=$(ps aux | grep 'picture-search/service/signin.py' | grep -v grep | awk '{ print $2 }')
    kill -9 ${pid}
}

case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_stop
        do_start
        ;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac

