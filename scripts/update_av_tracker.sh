#!/usr/bin/env bash

source ~/.bash_profile
source /home/dm1447/miniforge3/etc/profile.d/conda.sh
conda activate jupyter

export REPO_ROOT=/home/dm1447/dev/av-pipeline-tracker
cd $REPO_ROOT

/home/dm1447/dev/av-pipeline-tracker/tracker/scripts/track_logs.py

