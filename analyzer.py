import argparse
import glob
import json
import os
import itertools

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
                    
def get_repos_with_linting_test_only(json_files):
    
    repos_with_linting_test_only_list = []
    for json_obj in json_files:
        if 'testing' in json_obj:
            matched_keys = [key for key, val in json_obj['testing'].items() if 'lint' in key]
            if len(matched_keys) != 0 and 'test' not in json_obj['testing']:
                repos_with_linting_test_only_list.append(json_obj)
    return repos_with_linting_test_only_list

def get_repos_with_test_infras(json_files):
    repos_with_tests = []
    for json_obj in json_files:
        if 'testing' in json_obj:
            if 'test' in json_obj['testing']:
                if 'test_infras' in json_obj['testing']['test']:
                    repos_with_tests.append(json_obj)
    return(repos_with_tests)

def get_repos_with_available_test(json_files):
    repos_with_available_tests = []
    for json_obj in json_files:
        if 'testing' in json_obj:
            if 'test' in json_obj['testing']:
                if 'num_passing' in json_obj['testing']['test'] or \
                    'num_failing' in json_obj['testing']['test']:
                    repos_with_available_tests.append(json_obj)
    return repos_with_available_tests

def extract_repos_with_runnable_tests(args):
    json_files = get_json_files(args)
    repo_cloning_ERROR_list, pkg_json_ERROR_list = get_setup_erroroneous_repos(json_files)
    build_ERROR_list = get_unsuccessful_build_repos(json_files)
    installation_ERROR_list = get_unsuccessful_installation_repos(json_files)
    empty_test_suite_list = get_repos_with_no_test_suites(json_files)
    unrunnable_test_repos = get_repos_with_unrunnable_tests(json_files)
    repos_with_linting_test_only_list = get_repos_with_linting_test_only(json_files)
    repos_with_available_tests = get_repos_with_available_test(json_files)

    repos_with_tests_directory = args.framework+"_repos_with_runnable_tests/"
    if not os.path.exists(repos_with_tests_directory):
        os.makedirs(repos_with_tests_directory)
    repos_with_tests = list(convert_json_list_to_set(repos_with_available_tests) - \
                    convert_json_list_to_set(repo_cloning_ERROR_list) - \
                    convert_json_list_to_set(pkg_json_ERROR_list) - \
                    convert_json_list_to_set(build_ERROR_list) - \
                    convert_json_list_to_set(installation_ERROR_list) - \
                    convert_json_list_to_set(empty_test_suite_list) - \
                    convert_json_list_to_set(unrunnable_test_repos) - \
                    convert_json_list_to_set(repos_with_linting_test_only_list))
                    
    for obj in repos_with_tests:
        try:
            obj = json.loads(obj)
            repo_link = obj['metadata']['repo_link'].split("/")[-1]
            dump_json(repos_with_tests_directory+repo_link+"__results.json", obj)
        except AttributeError as ae:
            print(ae)

    print("Total number of repositories: " + str(len(json_files)))
    print("Number of repositories that couldn't been cloned: "+ str(len(repo_cloning_ERROR_list)))
    print("Number of repositories without package.json: "+ str(len(pkg_json_ERROR_list)))
    print("Number of repositories with build error: " + str(len(build_ERROR_list)))
    print("Number of repositories with installation error: " + str(len(installation_ERROR_list)))
    print("Number of repositories that we failed to run the tests for: "+str(len(unrunnable_test_repos))) 
    print("Number of repositories with an empty test suite: "+str(len(empty_test_suite_list)))
    print("Number of repositories with linters only and no test suite: "+str(len(repos_with_linting_test_only_list))) 
    print("Number of repositories with runnable test suites: "+str(len(repos_with_tests)))

def analyze_grouped_by_test_infras(args):
    json_files = get_json_files(args)
    repos_with_tests = get_repos_with_test_infras(json_files)
    print("Number of repositories with test infrastructure specified: " + str(len(repos_with_tests)))
    unique_testing_infras = []
    for json_obj in repos_with_tests:
        key = json_obj['testing']['test']['test_infras']
        if key not in unique_testing_infras:
            unique_testing_infras.append(key)
    print("\n")
    print("Reporeting for each testing infrastructure:")
    for test_infras in unique_testing_infras:
        print("Testing infrastructure: " + str(test_infras[0]))
        total_repo_counter = 0
        containing_test_counter = 0
        passing_percentage = 0
        error_count = 0
        for json_obj in repos_with_tests:
            if json_obj['testing']['test']['test_infras'] == test_infras:
                total_repo_counter += 1
                num_passing = json_obj['testing']['test']['num_passing']
                num_failing = json_obj['testing']['test']['num_failing']
                num_total = num_passing + num_failing
                try:
                    passing_percentage += num_passing/num_total
                    containing_test_counter += 1
                except ZeroDivisionError as e:
                    pass
                if 'ERROR' in json_obj['testing']['test'] and json_obj['testing']['test']['ERROR'] is True:
                    error_count += 1
        try:
            containing_test_percentage = float(containing_test_counter)/total_repo_counter
        except:
            pass
        print("The percentage of repositories that are recognized to have this infrastructure and actually have test suites: "+str(containing_test_percentage))

        try:
            passing_percentage = float(passing_percentage)/containing_test_counter
        except:
            pass
        print("The proportion of available test suites that pass: "+str(passing_percentage)+"\n")
    #The two following intersections are not empty
    #print(intersection_list(repos_with_tests, unrunnable_test_repos))
    #print(intersection_list(repos_with_tests, build_ERROR_list))
    
def main():
    args = get_args()
    extract_repos_with_runnable_tests(args)
    analyze_grouped_by_test_infras(args)

if __name__ == "__main__":
    main()