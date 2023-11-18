#!/bin/sh
cd /var/www/signal-calc/
mkdir "logs"
cd logs
ln -sf /root/Dropbox/Trader/signal-calc-V1/logs/archive

cd /var/www/signal-calc/

. /var/www/signal-calc/.venv/bin/activate

python /var/www/signal-calc/run-calc-engine.py 1> logs/run-calc-engine.log 2> logs/run-calc-engine.err

# Backup the files now
today="$(date -I)"
mkdir logs/archive/${today} 2> /dev/null

cp -r generated logs/archive/${today}/

mv logs/calc-signal.log logs/archive/${today}/calc-signal.log.${today}
mv logs/run-calc-engine.* logs/archive/${today}/
