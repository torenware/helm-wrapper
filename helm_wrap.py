#! /usr/bin/env python3

import sys
import argparse
import re 
from urllib.parse import urlparse
from subprocess import run
from hwrap_settings import REAL_HELM, BITNAMI_HOST, HARBOR_HOST

def get_handles():
    cmd = f"{REAL_HELM} repo list"
    data = run(cmd, capture_output=True, shell=True, text=True)
    if data.returncode != 0:
        raise Exception(data.stderr)
    lines = data.stdout.splitlines()
    first = True
    is_bitnamy = []
    for line in lines:
        if first:
            first = False
        else:
            keyword, repo = line.split()
            if repo == BITNAMI_HOST:
                is_bitnamy.append(keyword)
    return is_bitnamy

def parse_repo_spec(repo_spec):
    parts = urlparse(repo_spec)
    scheme = parts.scheme
    host = parts.netloc
    path_re =  r"/?([^/]+)/?(.+)?"
    match = re.match(path_re, parts.path)
    handle = match[1]
    repo = ""
    if match.lastindex > 1:
        repo = match[2]

    # print("For spec " + repo_spec)
    # print(f"scheme = {scheme} host = {host} handle = {handle} repo = {repo}")
    # print()

    return scheme, host, handle, repo

def uses_help(arg_list):
    help_tokens = ["-h", "--help", "help"]
    for token in help_tokens:
        if token in arg_list:
            return True
    return False


def build_help_cmd(arg_list: list):
    arg_list[0] = REAL_HELM
    help_tokens = ["-h", "--help", "help"]
    for token in help_tokens:
        if token in arg_list:
          arg_list.remove(token)
    arg_list.append("--help")
    cmd = " ".join(arg_list)
    return cmd, ""

def strip_flags(arg_list):
    stripped = []
    for item in arg_list:
        if len(item) and item[0] == "-":
            next
        stripped.append(item)
    return stripped

def build_command(arg_list):
    """
    Parse out the images name and rebuild command to
    access "real" helm binary

    Relevant commands are:

    helm repo add REPO_HANDLE REGISTRY_PATH

    helm install INSTALL_NAME REPO_SPEC [-n NS]
    
    """

    if uses_help(arg_list):
        return build_help_cmd(arg_list)

    parser = argparse.ArgumentParser(add_help=False)

    
    parser.add_argument("-n", "--namespace", help="K8s namespace",
                        type=str, default="default")
    parser.add_argument('command', type=str)
    # parser.add_argument('verb', type=str)

    args, items = parser.parse_known_args(arg_list)
    items = strip_flags(items)
    

    repos = get_handles()

    if len(items) > 2 and items[0] == "install":
        if items[2] == "":
            raise Exception("repo spec is required")
        arg3 = items[2]
        scheme, host, handle, repo = parse_repo_spec(arg3)

        # print(scheme, host, handle, repo)
        if handle in repos:
            arg3 = f"oci://{HARBOR_HOST}/bitnami/{repo}"
            # print("full repo: ", arg3)

        cmd = f"{REAL_HELM} install {items[1]} {arg3}"


    else:
        arg_list[0] = REAL_HELM 
        cmd = " ".join(arg_list)

    


    #print(f"varb {ns.verb} arg1 {ns.arg1} -n {ns.namespace}")
    # print(rest)

    return (cmd, "")


if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.

    # input = [
    #     "helm repo list",
    #     "helm list",
    #     "helm --help",
    #     "helm install test1 somerepo/mariadb",
    #     "helm install test2 bitnamy/mariadb",
    #     "helm install test3 oci://torensys.com/bitnami/mariadb:10",
    #     "helm repo myrepo https://charts.bitnami.com/bitnami",
    # ]

    # for test in input:
    #     print();
    #     args = test.split()
    #     print("Running: ", test)
    #     cmd, img = build_command(args)
    #     print("CMD: ", cmd)

    cmd, img = build_command(sys.argv)

    # print("arglist: ", sys.argv)
    print(cmd)
    

