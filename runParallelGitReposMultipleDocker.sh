#!/bin/bash

min_number() {
    printf "%s\n" "$@" | sort -g | head -n1
}


repo_link_file=$1
config_file=$2

if [ ! -f $config_file ] || [ ! $config_file ]; then 
	config_file="configs/QL_output_config.json"
fi

# copy config files to a shared volume with the container
if [ ! -d npm_filter_parallel_docker_results ]; then
	mkdir npm_filter_parallel_docker_results
fi
cp $config_file npm_filter_parallel_docker_results/config.json


DOCKER_CPUS=4
DOCKER_RAM=4

TOTAL_CPUS=$(grep ^cpu\\scores /proc/cpuinfo | uniq |  awk '{print $4}')
TOTAL_RAM=$(grep MemTotal /proc/meminfo | awk '{print $2}' | xargs -I {} echo "scale=0; {}/1024^2" | bc)

MAX_CONTAINERS_CPUS=$(echo "scale=0; $TOTAL_CPUS/$DOCKER_CPUS" | bc)
MAX_CONTAINERS_RAM=$(echo "scale=0; $TOTAL_RAM/$DOCKER_RAM" | bc)

MIN_VALUE=$(min_number $MAX_CONTAINERS_CPUS $MAX_CONTAINERS_RAM)
NUM_CONTAINERS=$(echo "scale=0; $MIN_VALUE-1" | bc)


nohup parallel -j $NUM_CONTAINERS -a $repo_link_file --timeout 600 --joblog job.log ./runSingleGitRepoResourceConstrainedDocker.sh {} $DOCKER_CPUS $DOCKER_RAM

rm npm_filter_parallel_docker_results/config.json