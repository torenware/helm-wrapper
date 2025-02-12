#! /usr/bin/env python3

import sys
import os
from subprocess import run
from hwrap_settings import REAL_HELM, HARBOR_HOST

# Dictionary of repository URLs and their corresponding substitution values
SUBSTITUTION_HOSTS = {
    "https://charts.bitnami.com/bitnami": "bitnami"
}

def get_handles():
    """Retrieve Helm repository handles"""
    cmd = f"{REAL_HELM} repo list"
    data = run(cmd, capture_output=True, shell=True, text=True)
    if data.returncode != 0:
        return {}
    lines = data.stdout.splitlines()[1:]  # Skip header
    return {line.split()[0]: line.split()[1] for line in lines}

def parse_repo_spec(repo_spec):
    """Parses repository spec (e.g., 'google-test/tomcat') and extracts repository handle and chart name."""
    parts = repo_spec.split("/")
    return (parts[0], parts[1]) if len(parts) >= 2 else ("", "")

def uses_help(arg_list):
    """Check if help is requested"""
    return any(token in arg_list for token in ["-h", "--help", "help"])

def build_help_cmd(arg_list):
    """Ensure Helm help commands are properly handled"""
    arg_list[0] = REAL_HELM
    arg_list = [arg for arg in arg_list if arg not in ["-h", "--help", "help"]]
    arg_list.append("--help")
    return " ".join(arg_list)

def strip_flags(arg_list):
    """Removes flags and their values from positional arguments but ensures they are not lost."""
    stripped, flags = [], []
    skip_next = False

    for i, item in enumerate(arg_list):
        if skip_next:
            skip_next = False
            continue

        if item.startswith("-"):
            if "=" in item:  # Handle flags with `=` (e.g., --version=1.1.1.1)
                key, value = item.split("=", 1)  # Split into flag and value
                flags.append(key)
                flags.append(value)
            else:
                flags.append(item)
                if i + 1 < len(arg_list) and not arg_list[i + 1].startswith("-"):
                    flags.append(arg_list[i + 1])
                    skip_next = True
            continue  # Don't add the flag itself

        stripped.append(item)

    return stripped, flags

def build_command(arg_list):
    """Construct the correct Helm command, transforming chart references when necessary."""
    
    if len(arg_list) < 2:
        return " ".join([REAL_HELM] + arg_list[1:])  # Pass through if too few arguments

    if uses_help(arg_list):
        return build_help_cmd(arg_list)  # Handle help commands

    repos = get_handles()
    cmd_parts = [REAL_HELM]
    stripped_args, flags = strip_flags(arg_list)

    command = stripped_args[1]
    if command not in ["install", "pull", "upgrade"]:
        return " ".join([REAL_HELM] + arg_list[1:])  # Pass non-install, non-pull, and non-upgrade commands through unchanged

    cmd_parts.append(command)

    if command in ["install", "upgrade"]:
        release_name = stripped_args[2] if len(stripped_args) > 2 else None
        chart_name = stripped_args[3] if len(stripped_args) > 3 else None

        if chart_name:
            handle, repo = parse_repo_spec(chart_name)
            if handle in repos and repos[handle] in SUBSTITUTION_HOSTS:
                chart_name = f"oci://{HARBOR_HOST}/{SUBSTITUTION_HOSTS[repos[handle]]}/{repo}"

        if release_name and chart_name:
            cmd_parts.extend([release_name, chart_name])
        elif chart_name:
            cmd_parts.append(chart_name)

    elif command == "pull":
        chart_name = stripped_args[2] if len(stripped_args) > 2 else None

        if chart_name:
            handle, repo = parse_repo_spec(chart_name)
            if handle in repos and repos[handle] in SUBSTITUTION_HOSTS:
                chart_name = f"oci://{HARBOR_HOST}/{SUBSTITUTION_HOSTS[repos[handle]]}/{repo}"
            cmd_parts.append(chart_name)

    cmd_parts.extend(flags)  # Append flags at the end
    return " ".join(cmd_parts)

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    if 'DEBUG_WRAPPER' in os.environ:
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        print("Waiting for debugger attach", file=sys.stderr)
        debugpy.wait_for_client()

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

    cmd = build_command(sys.argv)

    # print("arglist: ", sys.argv)
    print(cmd)
