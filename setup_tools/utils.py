import os
from pathlib import Path
from subprocess import DEVNULL, run
from setup_tools.helper import apt_install, update_alternatives, git_clone


def install_utils_fn(args, local_home, zdotdir):
    local_bin = local_home / ".local/bin"
    git_clone(
        "BurntSushi/ripgrep.git",
        "/tmp/rg",
        install_target=local_bin / "rg",
        force=args.upgrade,
    )
    git_clone(
        "sharkdp/fd.git", "/tmp/fd", install_target=local_bin / "fd", force=args.upgrade
    )
    git_clone(
        "cgag/loc.git", "/tmp/loc", install_target=local_bin / "loc", force=args.upgrade
    )
    git_clone(
        "Peltoche/lsd.git",
        "/tmp/lsd",
        install_target=local_bin / "lsd",
        force=args.upgrade,
    )
    git_clone(
        "sharkdp/hyperfine.git",
        "/tmp/hyperfine",
        install_target=local_bin / "hyperfine",
        force=args.upgrade,
    )
    git_clone(
        "sharkdp/bat.git",
        "/tmp/bat",
        install_target=local_bin / "bat",
        force=args.upgrade,
    )
    git_clone(
        "Kethku/neovide",
        "/tmp/neovide",
        install_target=local_bin / "neovide",
        force=args.upgrade,
    )
    git_clone(
        "rust-analyzer/rust-analyzer.git",
        "/tmp/rust-analyzer-repo",
        install_target=local_home / ".cargo/bin/ra_lsp_server",
        force=args.upgrade,
    )
    docs_completions_cmd = {
        "rg": f'cp $(find . -name rg.1 -print0 | xargs -0 ls -t | head -n1) \
                "{local_home}/.local/share/man/man1"; \
                cp $(find . -name _rg -print0 | xargs -0 ls -t | head -n1) \
                "{zdotdir}/completions"',
        "fd": f'cp $(find . -name fd.1 -print0 | xargs -0 ls -t | head -n1) \
                "{local_home}/.local/share/man/man1"; \
                cp $(find . -name _fd -print0 | xargs -0 ls -t | head -n1) \
                "{zdotdir}/completions"',
        "lsd": f'cp $(find . -name _lsd -print0 | xargs -0 ls -t | head -n1) \
                "{zdotdir}/completions"',
    }

    for util in ["rg", "fd", "loc", "lsd", "hyperfine", "bat"]:
        os.chdir(f"/tmp/{util}")
        # run([local_home / ".cargo/bin/cargo", "install", "--force", "--path", "."], check=True)
        os.system(docs_completions_cmd.get(util, ""))
    os.chdir("/tmp/rust-analyzer-repo")
    # run([local_home / ".cargo/bin/cargo", "install-ra", "--server"], check=True)

    # os.chdir("/tmp/neovide")
    # run([local_home / ".cargo/bin/cargo", "build", "--release"], check=True)
    # run(["cp", "-f", "target/release/neovide", local_bin], check=True)


def install_fonts_fn():
    apt_install("libotf0")
    tmp_dir = Path("/tmp/firacode-nerd")
    tmp_dir.mkdir(exist_ok=True)
    os.chdir(tmp_dir)
    run(
        [
            "wget",
            "https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/FiraCode.zip",
            "-O",
            tmp_dir / "firacode.zip",
        ],
        check=True,
    )
    run(
        ["sudo", "mkdir", "--parents", "/usr/share/fonts/opentype/firacode-nerd"],
        check=True,
    )
    run(
        [
            "sudo",
            "unzip",
            "-u",
            "-d",
            "/usr/share/fonts/opentype/firacode-nerd",
            tmp_dir / "firacode.zip",
        ],
        check=True,
    )
    run(["rm", tmp_dir / "firacode.zip"], check=True)
    run(["sudo", "fc-cache", "-f", "-v"], check=True)
