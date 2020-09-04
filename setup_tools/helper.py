import os
import sys
from pathlib import Path
from subprocess import DEVNULL, run


def apt_install(*packages):
    for package in packages:
        run(["sudo", "apt-get", "install", "-y", package], check=True)


def update_alternatives(name, orig_name, priority=100):
    run(
        [
            "sudo",
            "update-alternatives",
            "--install",
            "/usr/bin/" + name,
            name,
            orig_name,
            str(priority),
        ],
        check=True,
    )
    run(["sudo", "update-alternatives", "--set", name, orig_name], check=True)


def replace_with_symlink(old, new):
    run(["rm", "-f", old], check=True)
    run(["ln", "-T", "-s", new, old], check=True)


def git_clone(repository, destination, install_target=None, force=False, github=True):
    if install_target is None:
        install_target = Path(destination)
    if not install_target.exists() or force:
        if github:
            repository = "https://github.com/" + repository
        destination = Path(destination)
        if destination.exists():
            os.chdir(destination)
            run(["git", "submodule", "update", "--init"], check=True)
            run(["git", "pull"], check=True)
        else:
            run(
                ["git", "clone", "--recurse-submodules", repository, destination],
                check=True,
            )
