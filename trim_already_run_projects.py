import json
import sys
import os

args = sys.argv
dir_path = "./npm_filter_parallel_docker_results"
already_run_projects = []
updated_repo_list = []

for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
        already_run_projects.append(path.split("__")[0])


file1 = open(args[1], 'r')
file2 = open('filtered_'+args[1], 'w')
while True:
    line = file1.readline()
    if not line:
        break
    if(line.split("/")[-1].split("\n")[0] not in already_run_projects):
        updated_repo_list.append(line)

file2.writelines((updated_repo_list))

file2.close()
file1.close()

