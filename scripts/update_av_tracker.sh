#!/usr/bin/env bash

source /home/dm2637/miniforge3/etc/profile.d/conda.sh

conda activate /home/dm2637/miniforge3/envs/jupyter

export HOME=/root
export REPO_ROOT=/home/dm2637/dev/av-pipeline-tracker
cd $REPO_ROOT

git config --global --add safe.directory $REPO_ROOT

echo 'Starting Logs tracker...'
$REPO_ROOT/tracker/scripts/track_logs.py

