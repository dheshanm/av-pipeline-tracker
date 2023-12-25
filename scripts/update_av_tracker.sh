#!/usr/bin/env bash

source activate jupyter

export REPO_ROOT=/home/dm1447/dev/av-pipeline-tracker
cd $REPO_ROOT

/home/dm1447/dev/av-pipeline-tracker/tracker/scripts/track_logs.py

