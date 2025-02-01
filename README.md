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

## Installing the Script
1. Make sure helm is installed on your system.
2. Install your harbor server and start it up.
3. Edit `hwsettings.py` and `helm_wrapper` to match where you've installed the helm binary, and what directory from your path that will override your helm binary.  Also, make sure that the HARBOR_HOST variable actually resolves to the IP of the harbor server.
4. Run install.sh, which will validate your settings, and install to your desired directory. 
5. Test that the script works by running a simple helm command.  If you try `helm version`, you should get output something like this:

   ```
      $ helm version
      command: /usr/bin/helm version
      version.BuildInfo{Version:"v3.15.3", GitCommit:"3bb50bbbdd9c946ba9989fbe4fb4104766302a64", GitTreeState:"clean", GoVersion:"go1.22.5"}

   ```

## Issues with the code

I'm currently using the argparser library in python, and am frankly unhappy with it.  Basic stuff works, but the emulation right now is brittle and a lot of flags will annoy the code.  This problem is mostly resolved, since I've tested against a wide range of helm commands, most of which I just have to pass through without garbling.

I've added support for remote debugging and some simple python unit tests to make the code easier to maintain. The tests should also serve to show how to use the script.

## Caveats

Approaching beta quality code, since it's getting usable for our purposes. Still, may eat your neighbor's kids or your cat,  break your legs, or vote for the wrong people, G'd forbid.

As for license: I make no claims 'bout nuttin'. Just spell my name right, Okay?  Let's say we're under an Apache compatible license and leave it there.
 
