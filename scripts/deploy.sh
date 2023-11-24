#!/usr/bin/env sh
cd /var/www/signal-calc
. .venv/bin/activate
pip install --upgrade pip
pip uninstall -y TechnoPunter-Commons
pip install -r requirements.txt