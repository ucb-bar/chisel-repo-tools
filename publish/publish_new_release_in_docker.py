#!/usr/bin/env python3
"""Example use: ./publish/publish_new_release_in_docker.py -- -m 3.4 -bt minor"""

import os
from os.path import expandvars
import sys
from argparse import ArgumentParser
import subprocess
import shutil
from pathlib import Path
import publish_new_release as pnr

def gitConfigGet(value):
    cmd = ["git", "config", "--get", value]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        msg = f"Could not determine git config value for '{value}', please provide one via CLI"
        raise Exception(msg)
    value = proc.stdout.decode().strip()
    return value

def platform():
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    else:
        raise Exception(f"Unsupported platform {sys.platform}")


def platformSpecific(key):
    lookup = {
        "macos": {
            "sshagent": "/run/host-services/ssh-auth.sock"
        },
        "linux": {
            "sshagent": "$SSH_AUTH_SOCK" # TODO may need to do env lookup
        }
    }
    return lookup[platform()][key]


def sshAgent():
    return platformSpecific("sshagent")


def prettifyCommand(cmd):
    def escape(l):
        return l.replace("\"", "\\\"")
    def quote(l):
        if " " in l or "\"" in l :
            return "\"" + escape(l) + "\""
        else:
            return l
    quoted = [quote(x) for x in cmd]
    return " ".join(quoted)


def flatten(l):
    return [item for sublist in l for item in sublist]


def formatValues(d):
    return { k: v.format(**d) for k, v in d.items() }


def makeParser():
    # TODO expose and propagate options from 'publish_new_release.py'
    parser = ArgumentParser()
    parser.add_argument("-e", "--email", action="store", default=gitConfigGet("user.email"),
                        help="Git config user.email, defaults to 'git config --get user.email'")
    parser.add_argument("-n", "--name", action="store", default=gitConfigGet("user.name"),
                        help="Git config user.name, defaults to 'git config --get user.name'")
    parser.add_argument("--ssh-agent", action="store", default=sshAgent(),
                        help=f"Git config user.name, defaults to '{sshAgent()}'")
    parser.add_argument("args", type=str, nargs="+",
                        help="Arguments for publish_new_release.py that will be run in Docker container")
    return parser


def find_container(image_name):
    cmd = ["docker", "ps", "--filter", f"ancestor={image_name}", "-q"]
    proc = subprocess.run(cmd, capture_output=True)
    lines = proc.stdout.decode().strip().split("\n")

    res = [x for x in lines if x != ""]

    if len(res) > 1:
        raise SystemExit(f"There needs to be 1 or fewer {image_name} containers, got {res}!")
    if len(res) == 0:
        return None
    else:
        return res[0]


def launch_container(args, image_name):
    container_home = "/root"
    host_home = expandvars("$HOME")

    # SSH Agent forwarding
    ssh_agent = ["-v", f"{args.ssh_agent}:/ssh-agent", "-e", "SSH_AUTH_SOCK=/ssh-agent"]
    # Known hosts mapping
    known_hosts = ["-v", f"{host_home}/.ssh/known_hosts:{container_home}/.ssh/known_hosts"]

    base_cmd = ["docker", "run", "-t", "-d"]
    cmd =  base_cmd + ssh_agent + known_hosts + [image_name]

    proc = subprocess.run(cmd, capture_output=True)

    return proc.stdout.decode().strip()


def run_commands(args, container, environment, lines):
    all_lines = [
        f"git config --global user.email {args.email}",
        f"git config --global user.name {args.name}",
    ] + lines
    joined = "; ".join(all_lines)
    script = f"bash -c '{joined}'"
    base_cmd = ["docker", "exec"]
    env = flatten([["-e", f"{name}={value}"] for name, value in environment.items()])
    cmd = base_cmd + env + [container] + ["bash", "-c", joined]
    print(prettifyCommand(cmd))
    proc = subprocess.run(cmd)


def main():
    parser = makeParser()
    args = parser.parse_args()
    print(args)

    # Check forwarded args
    forwarded_args = args.args
    pnr_parser = pnr.make_parser()
    pnr_parser.parse_args(forwarded_args)

    image_name = "chiselrelease:latest"

    # Step 1 - Build Docker Image
    # TODO actually do this
    # Run from root of the repo
    # docker build -f resources/Dockerfile -t chiselrelease:latest .

    # Environment needed to run publish commands
    environment = formatValues({
        "PYTHONPATH": "/work/chisel-repo-tools/src",
        "VERSIONING": "{PYTHONPATH}/versioning/versioning.py",
    })

    # Find or launch container
    container = find_container(image_name)

    if container is None:
        print("No container running, starting...")
        container = launch_container(args, image_name)
        cmd = ["git clone git@github.com:ucb-bar/chisel-release.git"]
        run_commands(args, container, environment, cmd)

    print(f"Running in container {container}")


    # Step 2 - Run release
    # TODO figure out how to have the Docker container stick around if it fails or go away if it passes

    splat_args = " ".join(forwarded_args)

    lines = [
        "cd chisel-release",
        f"python3 ../chisel-repo-tools/publish/publish_new_release.py {splat_args}"
    ]

    run_commands(args, container, environment, lines)


if __name__ == "__main__":
    main()
