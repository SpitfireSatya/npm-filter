#!/bin/bash

repo_link=$1
CPUS=$2
RAM=$3

RANDOM=$(printf "%s\n" "$SRANDOM")

if [ ! -d local_mount ]; then
        mkdir "local_mount_$RANDOM"
fi

SOURCE="`pwd`/local_mount_$RANDOM"


docker run --mount type=bind,source="$SOURCE",destination=/mount \
                   --volume `pwd`/npm_filter_parallel_docker_results:/home/npm-filter/results \
                   --cpus="$CPUS" \
                   --memory="${RAM}g" \
                   -w /home/npm-filter \
                   --rm \
                   -it npm-filter:latest \
                   bash -c "python3 src/diagnose_github_repo.py --repo_link $repo_link --config results/config.json --output_dir results"

rm -r "local_mount_$RANDOM"

