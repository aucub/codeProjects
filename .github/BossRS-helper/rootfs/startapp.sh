#!/bin/sh

cd /default/BossRS-helper/tool
python3 createdb.py
cd /default/BossRS-helper
exec python3 BossRS.py
