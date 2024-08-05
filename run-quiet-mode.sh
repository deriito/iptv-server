#!/bin/bash

source .venv/bin/activate

python3 app.py > /dev/null 2>&1 &

echo $! > app.pid
