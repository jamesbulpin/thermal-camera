#!/bin/bash

cd /home/pi/thermal-camera

nohup python ./ir.py > /dev/null 2>&1 &



