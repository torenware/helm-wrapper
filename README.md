# Helm Wrapper POC

This repo is a test of how one might get around the Bitnami helm rate limiting problem. It uses a simple wrapper for helm that redirects `helm install` away from DockerHub, and substitutes a self-hosted Harbor docker repository. 

## How it works

The scripts create a wrapper script that fronts for the helm binary, rewriting the `helm install` command to redirect to the Harbor repository. The repo contains:

* helm-wrapper a shell script that needs to be installed as "helm" to a directory higher up in PATH than the real binary ("REAL_HELM"). 
* hwsettings.py a "dual use" file that has valid syntax for both bash *and* python. It needs to be edited to match the location of the various files, and to point to the domain of the Harbor repository.
helm_wrapper.py, a python script that marshals the CLI command to convert from the common form of `helm install INSTALL_NAME REPO_NAME/CHART_NAME:TAG` to the OCI version of the call pointing to the Harbor install. 
install.sh a simple install script that reads the information in hwsettings.py and installs to the /usr/local/bin directory by default. This directory needs to be higher in the path than wherever the helm binary is actually installed.

## Settings

These you'll need to edit in hwsettings.py. Everything should be compatible with the bash shell as well as python.



| Variable | Default Value |
|---       |---            |
| HARBOR_HOST | "mirror.kodekloud.com" |
| REAL_HELM | "/usr/bin/helm" |
| WRAPPER_INSTALL_DIR | "/usr/local/bin" |
| BITNAMI_HOST | "https://charts.bitnami.com/bitnami" |


## Setting up Harbor

I'm mostly following [this tutorial](https://itnext.io/are-you-affected-by-bitnami-lts-and-docker-hub-pull-rate-limits-948f3590f936).  The major difference for me is I did this on an M4 Macbook Pro, and I could not get the build to work on an ARM64 machine. So my set up is as follows:

* I'm using the stable Helm repo for Harbor, with the following edits of values.yaml:
   * I have a Let's Encrypt cert encoded as a K8s TLS secret.
   * Harbor is served via an ingress.
* I'm using colima for K8s, since it emulates AMD64 pretty well and keeps the harbor binary happy. 

## Issues with the code

I'm currently using the argparser library in python, and am frankly unhappy with it.  Basic stuff works, but the emulation right now is brittle and a lot of flags will annoy the code. I'm very open to suggestions for a better library :-) 

## Caveats

Definitely alpha quality code, if that. May eat your neighbor's kids, break your legs, or vote for the wrong people, G'd forbid.
 