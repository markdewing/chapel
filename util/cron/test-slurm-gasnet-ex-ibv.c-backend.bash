#!/usr/bin/env bash
#
# Multi-node, multi-locale testing on a cray-cs with slurm-gasnetrun_ibv
# launcher:
# test gasnet-ex configuration with CHPL_LLVM=none & CHPL_TARGET_COMPILER=gnu
# test against "examples"

CWD=$(cd $(dirname ${BASH_SOURCE[0]}) ; pwd)
source $CWD/common-slurm-gasnet-cray-cs.bash
source $CWD/common-c-backend.bash

export CHPL_NIGHTLY_TEST_CONFIG_NAME="slurm-gasnet-ex-ibv.c-backend"

export CHPL_COMM_SUBSTRATE=ibv

# Test GASNet EX
export CHPL_GASNET_VERSION=ex

$CWD/nightly -cron -examples ${nightly_args} < /dev/null
