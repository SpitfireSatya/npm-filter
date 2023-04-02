import argparse
import glob
import json
import os

def intersection_list(list1, list2):
    list3 = []
    for element in list1:
        if element in list2:
            list3.append(element)
    return list3

def write_to_file(path, obj_list):
    file = open(path,'w')
    for item in obj_list:
	    file.write(item)
    file.close()

def load_json(path):
    f = open(path)
    data = json.load(f)

    return data

def dump_json(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=4)

def get_args():
    parser = argparse.ArgumentParser(description='UI Testing analyzer')
    parser.add_argument('--framework', dest='framework', type=str, help='One of the three supported frameworks; namely vue, angular or react.')
    args = parser.parse_args()

    if args.framework is None:
        args.framework = "react"

    return args

def convert_json_list_to_set(input_list): 
    return set(json.dumps(obj) for obj in input_list)

def get_json_files(args):
    json_files = []

    target_directory = args.framework+"_results"
    json_file_names = glob.glob(target_directory + "/*.json")
    for json_address in json_file_names:
        try:
            json_files.append(load_json(json_address))
        except ValueError as ve:
            print('No JSON object fount in address: ' + json_address)

    return json_files

def get_setup_erroroneous_repos(json_files):
    repo_cloning_ERROR_list = []
    pkg_json_ERROR_list = []

    for json_obj in json_files:
        if 'setup' in json_obj:
            if 'repo_cloning_ERROR' in json_obj['setup']:
                repo_cloning_ERROR_list.append(json_obj)
            elif 'pkg_json_ERROR' in json_obj['setup']:
                pkg_json_ERROR_list.append(json_obj)
    
    return repo_cloning_ERROR_list, pkg_json_ERROR_list

def get_unsuccessful_build_repos(json_files):
    build_ERROR_list = []

    for json_obj in json_files:
        if 'build' in json_obj:
            if 'ERROR' in json_obj['build'] and json_obj['build']['ERROR'] is True:
                build_ERROR_list.append(json_obj)

    return build_ERROR_list

def get_unsuccessful_installation_repos(json_files):
    installation_ERROR_list = []

    for json_obj in json_files:
        if 'installation' in json_obj:
            if 'ERROR' in json_obj['installation'] and json_obj['installation']['ERROR'] is True:
                installation_ERROR_list.append(json_obj)

    return installation_ERROR_list

def get_repos_with_no_test_suites(json_files):
    empty_test_suite_list = []

    for json_obj in json_files:
        if 'testing' in json_obj:
            if len(json_obj['testing']) == 0:
                empty_test_suite_list.append(json_obj)

    return empty_test_suite_list

def get_repos_with_unrunnable_tests(json_files):
    unrunnable_test_repos = []

    for json_obj in json_files:
        if 'testing' in json_obj:
            if 'test' in json_obj['testing']:
                if 'ERROR' in json_obj['testing']['test'] \
                and json_obj['testing']['test']['ERROR'] is True:
                    unrunnable_test_repos.append(json_obj)

    return(unrunnable_test_repos)
                    
def extract_repos_with_tests(args):
    json_files = get_json_files(args)
    repo_cloning_ERROR_list, pkg_json_ERROR_list = get_setup_erroroneous_repos(json_files)
    build_ERROR_list = get_unsuccessful_build_repos(json_files)
    installation_ERROR_list = get_unsuccessful_installation_repos(json_files)
    empty_test_suite_list = get_repos_with_no_test_suites(json_files)
    unrunnable_test_repos = get_repos_with_unrunnable_tests(json_files)

    repos_with_tests_directory = args.framework+"_repos_with_tests/"
    if not os.path.exists(repos_with_tests_directory):
        os.makedirs(repos_with_tests_directory)
    repos_with_tests = list(convert_json_list_to_set(json_files) - \
                    convert_json_list_to_set(repo_cloning_ERROR_list) - \
                    convert_json_list_to_set(pkg_json_ERROR_list) - \
                    convert_json_list_to_set(build_ERROR_list) - \
                    convert_json_list_to_set(installation_ERROR_list) - \
                    convert_json_list_to_set(empty_test_suite_list) - \
                    convert_json_list_to_set(unrunnable_test_repos))
    for obj in repos_with_tests:
        try:
            obj = json.loads(obj)
            repo_link = obj['metadata']['repo_link'].split("/")[-1]
            dump_json(repos_with_tests_directory+repo_link+"__results.json", obj)
        except AttributeError as ae:
            print(ae)

    print(len(json_files))
    print(len(repo_cloning_ERROR_list))
    print(len(pkg_json_ERROR_list))
    print(len(build_ERROR_list))
    print(len(empty_test_suite_list))
    print(len(unrunnable_test_repos))  
    print(len(repos_with_tests))


def main():
    args = get_args()
    extract_repos_with_tests(args)

if __name__ == "__main__":
    main()