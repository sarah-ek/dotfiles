import os
import sys
from pathlib import Path
from subprocess import DEVNULL, run
from setup_tools.helper import apt_install, update_alternatives, git_clone


def update_llvm_alternatives(names, version=10, priority=100):
    for name in names:
        new_name = name.replace(f"-{version}", "")
        orig_name = Path("/usr/bin") / name
        run(
            [
                "sudo",
                "update-alternatives",
                "--install",
                "/usr/bin/" + new_name,
                new_name,
                orig_name,
                str(priority),
            ],
            check=True,
        )
        run(["sudo", "update-alternatives", "--set", new_name, orig_name], check=True)


def install_llvm_fn(args, llvm_script, version=11):
    apt_install("libedit-dev", "swig")

    if not args.no_z3:
        git_clone(
            "Z3Prover/z3",
            "/tmp/z3-repo",
            install_target=Path("/usr/bin/z3"),
            force=True,
        )
        os.chdir("/tmp/z3-repo")
        run(["/usr/bin/python", "scripts/mk_make.py"], check=True)
        os.chdir("build")
        run(["make", "-j4"], check=True)
        run(["sudo", "make", "install"], check=True)

    run(["sudo", "bash", llvm_script, str(version)], check=True)
    # LLVM
    apt_install(
        f"libllvm-{version}-ocaml-dev",
        f"libllvm{version}",
        f"llvm-{version}",
        f"llvm-{version}-dev",
        f"llvm-{version}-doc",
        f"llvm-{version}-examples",
        f"llvm-{version}-runtime",
    )
    # Clang and co
    apt_install(
        f"clang-{version}",
        f"clang-tools-{version}",
        f"clang-{version}-doc",
        f"libclang-common-{version}-dev",
        f"libclang-{version}-dev",
        f"libclang1-{version}",
        f"clang-format-{version}",
        f"clang-tidy-{version}",
        f"clangd-{version}",
    )
    # libfuzzer
    apt_install(f"libfuzzer-{version}-dev")
    # lldb
    apt_install(f"lldb-{version}")
    # lld (linker)
    apt_install(f"lld-{version}")
    # libc++
    apt_install(f"libc++-{version}-dev", f"libc++abi-{version}-dev")
    # OpenMP
    apt_install(f"libomp-{version}-dev")

    update_alternatives("clang", Path("/usr/bin") / f"clang-{version}", priority=100)
    update_alternatives("clang++", Path("/usr/bin") / f"clang++-{version}", priority=100)

    update_llvm_alternatives(
        [
            f"bugpoint-{version}",
            f"c-index-test-{version}",
            f"clang++-{version}",
            f"clang-{version}",
            f"clang-apply-replacements-{version}",
            f"clang-change-namespace-{version}",
            f"clang-check-{version}",
            f"clang-cl-{version}",
            f"clang-cpp-{version}",
            f"clang-doc-{version}",
            f"clang-extdef-mapping-{version}",
            f"clang-format-{version}",
            f"clang-include-fixer-{version}",
            f"clang-offload-bundler-{version}",
            f"clang-query-{version}",
            f"clang-refactor-{version}",
            f"clang-rename-{version}",
            f"clang-reorder-fields-{version}",
            f"clang-scan-deps-{version}",
            f"clang-tidy-{version}",
            f"clang-tidy-diff-{version}.py",
            f"clangd-{version}",
            f"count-{version}",
            f"diagtool-{version}",
            f"dsymutil-{version}",
            f"FileCheck-{version}",
            f"find-all-symbols-{version}",
            f"git-clang-format-{version}",
            f"hmaptool-{version}",
            f"ld.lld-{version}",
            f"ld64.lld-{version}",
            f"llc-{version}",
            f"lld-{version}",
            f"lld-link-{version}",
            f"lldb-{version}",
            f"lldb-argdumper-{version}",
            f"lldb-instr-{version}",
            f"lldb-server-{version}",
            f"lldb-vscode-{version}",
            f"lli-{version}",
            f"lli-child-target-{version}",
            f"llvm-addr2line-{version}",
            f"llvm-ar-{version}",
            f"llvm-as-{version}",
            f"llvm-bcanalyzer-{version}",
            f"llvm-c-test-{version}",
            f"llvm-cat-{version}",
            f"llvm-cfi-verify-{version}",
            f"llvm-config-{version}",
            f"llvm-cov-{version}",
            f"llvm-cvtres-{version}",
            f"llvm-cxxdump-{version}",
            f"llvm-cxxfilt-{version}",
            f"llvm-cxxmap-{version}",
            f"llvm-diff-{version}",
            f"llvm-dis-{version}",
            f"llvm-dlltool-{version}",
            f"llvm-dwarfdump-{version}",
            f"llvm-dwp-{version}",
            f"llvm-elfabi-{version}",
            f"llvm-exegesis-{version}",
            f"llvm-extract-{version}",
            f"llvm-jitlink-{version}",
            f"llvm-lib-{version}",
            f"llvm-link-{version}",
            f"llvm-lipo-{version}",
            f"llvm-lto-{version}",
            f"llvm-lto2-{version}",
            f"llvm-mc-{version}",
            f"llvm-mca-{version}",
            f"llvm-modextract-{version}",
            f"llvm-mt-{version}",
            f"llvm-nm-{version}",
            f"llvm-objcopy-{version}",
            f"llvm-objdump-{version}",
            f"llvm-opt-report-{version}",
            f"llvm-pdbutil-{version}",
            f"llvm-PerfectShuffle-{version}",
            f"llvm-profdata-{version}",
            f"llvm-ranlib-{version}",
            f"llvm-rc-{version}",
            f"llvm-readelf-{version}",
            f"llvm-readobj-{version}",
            f"llvm-rtdyld-{version}",
            f"llvm-size-{version}",
            f"llvm-split-{version}",
            f"llvm-stress-{version}",
            f"llvm-strings-{version}",
            f"llvm-strip-{version}",
            f"llvm-symbolizer-{version}",
            f"llvm-tblgen-{version}",
            f"llvm-undname-{version}",
            f"llvm-xray-{version}",
            f"modularize-{version}",
            f"not-{version}",
            f"obj2yaml-{version}",
            f"opt-{version}",
            f"run-clang-tidy-{version}",
            f"run-clang-tidy-{version}.py",
            f"sancov-{version}",
            f"sanstats-{version}",
            f"verify-uselistorder-{version}",
            f"wasm-ld-{version}",
            f"yaml-bench-{version}",
            f"yaml2obj-{version}",
        ],
        version=version,
        priority=100,
    )
