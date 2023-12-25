#!/usr/bin/env bash

source activate /home/dm2637/miniforge3/envs/jupyter

export REPO_ROOT=/home/dm2637/dev/av-pipeline-tracker
cd $REPO_ROOT

/home/dm2637/dev/av-pipeline-tracker/tracker/scripts/track_logs.py

