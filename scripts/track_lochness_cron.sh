#!/usr/bin/env bash

source ~/.bash_profile
source /PHShome/dm1447/mambaforge/etc/profile.d/conda.sh
conda activate jupyter

export REPO_ROOT=/PHShome/dm1447/dev/av-pipeline-tracker
cd $REPO_ROOT

$REPO_ROOT/tracker/scripts/track_lochness.py --network Prescient
$REPO_ROOT/tracker/scripts/track_lochness.py --network ProNET
