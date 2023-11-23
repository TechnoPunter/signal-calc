#!/bin/sh
BASE_DIR=/var/www/signal-calc/
cd "$BASE_DIR"
. "$BASE_DIR"/.venv/bin/activate

export GENERATED_PATH="$BASE_DIR"/generated
export RESOURCE_PATH="$BASE_DIR"/resources/config
export LOG_PATH="$BASE_DIR"/logs

python /var/www/signal-calc/run-calc-engine.py 1> logs/run-calc-engine.log 2> logs/run-calc-engine.err

# Backup the files now
today="$(date -I)"
mkdir logs/archive/${today} 2> /dev/null

cp -r generated logs/archive/${today}/

mv logs/calc-signal.log logs/archive/${today}/calc-signal.log.${today}
mv logs/run-calc-engine.* logs/archive/${today}/
