#!/bin/bash

repo_link=$1
CPUS=$2
RAM=$3

RANDOM_NUM=$(printf "%s\n" "$SRANDOM")

if [ ! -d local_mount ]; then
        mkdir "local_mount_$RANDOM_NUM"
fi

SOURCE="`pwd`/local_mount_$RANDOM_NUM"


docker run -v type=bind,source="$SOURCE",destination=/mount \
                   --volume `pwd`/npm_filter_parallel_docker_results:/home/npm-filter/results \
                   --cpus="$CPUS" \
                   --memory="${RAM}g" \
                   -w /home/npm-filter \
                   --rm \
                   -t npm-filter:latest \
                   bash -ic "python3 src/diagnose_github_repo.py --repo_link $repo_link --config results/config.json --output_dir results"

rm -rf "local_mount_$RANDOM_NUM"

