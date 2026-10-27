"""In-memory Git Version Control Simulator for DevOpsHeroCLI."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class GitCommit:
    hash_id: str
    message: str
    author: str
    timestamp: str
    branch: str
    files: List[str]


class GitSimulator:
    """Simulates local Git repository state in memory."""

    def __init__(self):
        self.is_repo: bool = False
        self.branches: Set[str] = {"main"}
        self.current_branch: str = "main"
        self.staged_files: Set[str] = set()
        self.unstaged_files: Set[str] = set()
        self.untracked_files: Set[str] = set()
        self.commits: List[GitCommit] = []
        self.remotes: Dict[str, str] = {}
        self.stash: List[str] = []
        self.tags: Set[str] = set()
        self.config: Dict[str, str] = {
            "user.name": "DevOps Hero",
            "user.email": "hero@devopshero.local",
            "init.defaultBranch": "main",
        }
        self.reset_default_state()

    def reset_default_state(self):
        self.is_repo = False
        self.branches = {"main"}
        self.current_branch = "main"
        self.staged_files.clear()
        self.unstaged_files.clear()
        self.untracked_files.clear()
        self.commits.clear()
        self.remotes.clear()
        self.stash.clear()
        self.tags.clear()

    def init(self, args: List[str]) -> str:
        branch = "main"
        if "-b" in args:
            idx = args.index("-b")
            if idx + 1 < len(args):
                branch = args[idx + 1]
        elif "--initial-branch" in args:
            idx = args.index("--initial-branch")
            if idx + 1 < len(args):
                branch = args[idx + 1]

        self.is_repo = True
        self.branches = {branch}
        self.current_branch = branch
        return f"Initialized empty Git repository in /home/devops/app/.git/ (default branch: {branch})"

    def status(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"

        lines = [f"On branch {self.current_branch}"]
        if not self.commits:
            lines.append("\nNo commits yet\n")
        else:
            lines.append("Your branch is up to date with 'origin/main'.\n" if "origin" in self.remotes else "")

        if self.staged_files:
            lines.append("Changes to be committed:")
            lines.append('  (use "git restore --staged <file>..." to unstage)')
            for f in sorted(self.staged_files):
                lines.append(f"\t\033[32mnew file:   {f}\033[0m")
            lines.append("")

        if self.unstaged_files:
            lines.append("Changes not staged for commit:")
            lines.append('  (use "git add <file>..." to update what will be committed)')
            for f in sorted(self.unstaged_files):
                lines.append(f"\t\033[31mmodified:   {f}\033[0m")
            lines.append("")

        if self.untracked_files:
            lines.append("Untracked files:")
            lines.append('  (use "git add <file>..." to include in what will be committed)')
            for f in sorted(self.untracked_files):
                lines.append(f"\t\033[31m{f}\033[0m")
            lines.append("")

        if not self.staged_files and not self.unstaged_files and not self.untracked_files:
            lines.append("nothing to commit, working tree clean")

        return "\n".join(lines).strip()

    def add(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not args:
            return "Nothing specified, nothing added.\nMaybe you wanted to say 'git add .'?"

        for target in args:
            if target in [".", "-A", "--all"]:
                self.staged_files.update(self.untracked_files)
                self.staged_files.update(self.unstaged_files)
                self.untracked_files.clear()
                self.unstaged_files.clear()
            else:
                self.untracked_files.discard(target)
                self.unstaged_files.discard(target)
                self.staged_files.add(target)
        return ""

    def commit(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"

        # Check message
        message = ""
        if "-m" in args:
            idx = args.index("-m")
            if idx + 1 < len(args):
                message = args[idx + 1]

        if not message:
            return "error: switch `m' requires a value"

        if not self.staged_files and not ("-a" in args or "-am" in args):
            return "nothing to commit, working tree clean"

        if "-a" in args or "-am" in args:
            self.staged_files.update(self.unstaged_files)
            self.unstaged_files.clear()

        # Generate fake commit hash
        import hashlib
        short_hash = hashlib.sha1(f"{message}{time.time()}".encode(), usedforsecurity=False).hexdigest()[:7]
        committed_files = list(self.staged_files)
        commit_obj = GitCommit(
            hash_id=short_hash,
            message=message,
            author=f"{self.config['user.name']} <{self.config['user.email']}>",
            timestamp=time.strftime("%a %b %d %H:%M:%S %Y +0000"),
            branch=self.current_branch,
            files=committed_files,
        )
        self.commits.insert(0, commit_obj)
        self.staged_files.clear()

        count = len(committed_files) or 1
        return f"[{self.current_branch} {short_hash}] {message}\n {count} file changed, {count * 12} insertions(+)"

    def branch(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"

        if not args:
            lines = []
            for b in sorted(self.branches):
                prefix = "* " if b == self.current_branch else "  "
                color = "\033[32m" if b == self.current_branch else ""
                reset = "\033[0m" if color else ""
                lines.append(f"{prefix}{color}{b}{reset}")
            return "\n".join(lines)

        if "-d" in args or "-D" in args:
            flag = "-d" if "-d" in args else "-D"
            target = args[args.index(flag) + 1]
            if target == self.current_branch:
                return f"error: Cannot delete branch '{target}' checked out at '/home/devops/app'"
            if target in self.branches:
                self.branches.remove(target)
                return f"Deleted branch {target} (was 4a2b1c0)."
            return f"error: branch '{target}' not found."

        if "-M" in args or "-m" in args:
            flag = "-M" if "-M" in args else "-m"
            new_name = args[args.index(flag) + 1]
            self.branches.discard(self.current_branch)
            self.branches.add(new_name)
            self.current_branch = new_name
            return ""

        new_branch = args[0]
        self.branches.add(new_branch)
        return ""

    def checkout(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not args:
            return "usage: git checkout [<branch>]"

        if "-b" in args:
            idx = args.index("-b")
            if idx + 1 < len(args):
                name = args[idx + 1]
                self.branches.add(name)
                self.current_branch = name
                return f"Switched to a new branch '{name}'"

        target = args[0]
        if target in self.branches:
            self.current_branch = target
            return f"Switched to branch '{target}'"
        return f"error: pathspec '{target}' did not match any file(s) known to git"

    def switch(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if "-c" in args or "-C" in args:
            flag = "-c" if "-c" in args else "-C"
            idx = args.index(flag)
            if idx + 1 < len(args):
                name = args[idx + 1]
                self.branches.add(name)
                self.current_branch = name
                return f"Switched to a new branch '{name}'"

        if args and args[0] in self.branches:
            self.current_branch = args[0]
            return f"Switched to branch '{args[0]}'"
        return f"fatal: invalid reference: {args[0] if args else ''}"

    def merge(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not args:
            return "fatal: No commit specified and merge.default not set."

        target = args[0]
        if target not in self.branches:
            return f"merge: {target} - not something we can merge"

        return (
            "Updating 3d2f1a0..7c8e9b1\n"
            "Fast-forward\n"
            " app.py | 14 +++++++++++++-\n"
            " 1 file changed, 13 insertions(+), 1 deletion(-)"
        )

    def log(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not self.commits:
            return "fatal: your current branch 'main' does not have any commits yet"

        oneline = "--oneline" in args
        max_count = 10
        for a in args:
            if a.startswith("-n"):
                try:
                    max_count = int(a[2:])
                except ValueError:
                    pass

        lines = []
        for c in self.commits[:max_count]:
            if oneline:
                lines.append(f"\033[33m{c.hash_id}\033[0m {c.message}")
            else:
                lines.append(f"\033[33mcommit {c.hash_id}09f872398471209384712093847\033[0m")
                lines.append(f"Author: {c.author}")
                lines.append(f"Date:   {c.timestamp}\n")
                lines.append(f"    {c.message}\n")
        return "\n".join(lines).strip()

    def diff(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        return (
            "diff --git a/app.py b/app.py\n"
            "index 83a21b..4c71ef 100644\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -10,3 +10,4 @@ def main():\n"
            "-    print('Hello World')\n"
            "+    print('Hello DevOpsHero')\n"
            "+    return 0"
        )

    def remote(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not args:
            return "\n".join(self.remotes.keys())

        if args[0] in ["-v", "--verbose"]:
            lines = []
            for name, url in self.remotes.items():
                lines.append(f"{name}\t{url} (fetch)")
                lines.append(f"{name}\t{url} (push)")
            return "\n".join(lines)

        if args[0] == "add" and len(args) >= 3:
            name, url = args[1], args[2]
            self.remotes[name] = url
            return ""

        if args[0] in ["remove", "rm"] and len(args) >= 2:
            self.remotes.pop(args[1], None)
            return ""

        return "usage: git remote [-v | --verbose] | add <name> <url> | rm <name>"

    def push(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not self.remotes:
            return "fatal: No configured push destination."
        remote_name = "origin"
        branch_name = self.current_branch
        return (
            f"Enumerating objects: 5, done.\n"
            f"Counting objects: 100% (5/5), done.\n"
            f"Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.\n"
            f"To {self.remotes.get(remote_name, 'https://github.com/org/repo.git')}\n"
            f" * [new branch]      {branch_name} -> {branch_name}\n"
            f"Branch '{branch_name}' set up to track remote branch '{branch_name}' from '{remote_name}'."
        )

    def stash_cmd(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        sub = args[0] if args else "push"
        if sub in ["push", "save"] or not args:
            self.stash.append("WIP on main: changes saved")
            return f"Saved working directory and index state WIP on {self.current_branch}: commit message"
        elif sub == "pop":
            if self.stash:
                self.stash.pop()
                return "On branch main\nChanges not staged for commit:\n  modified:   app.py\ndropped refs/stash@{0}"
            return "error: No stash entries found."
        elif sub == "list":
            return "\n".join([f"stash@{{{i}}}: {s}" for i, s in enumerate(self.stash)])
        return "usage: git stash [push|pop|list|clear]"

    def tag(self, args: List[str]) -> str:
        if not self.is_repo:
            return "fatal: not a git repository (or any of the parent directories): .git"
        if not args:
            return "\n".join(sorted(self.tags))
        tag_name = args[0]
        self.tags.add(tag_name)
        return ""

    def execute(self, args: List[str]) -> str:
        if not args:
            return (
                "usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]\n"
                "           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]\n"
                "           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]\n"
                "           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]\n"
                "           [--super-prefix=<path>] [--config-env=<name>=<envvar>]\n"
                "           <command> [<args>]"
            )

        sub = args[0]
        sub_args = args[1:]

        if sub == "--version":
            return "git version 2.44.0"
        elif sub == "init":
            return self.init(sub_args)
        elif sub == "status":
            return self.status(sub_args)
        elif sub == "add":
            return self.add(sub_args)
        elif sub == "commit":
            return self.commit(sub_args)
        elif sub == "branch":
            return self.branch(sub_args)
        elif sub == "checkout":
            return self.checkout(sub_args)
        elif sub == "switch":
            return self.switch(sub_args)
        elif sub == "merge":
            return self.merge(sub_args)
        elif sub == "log":
            return self.log(sub_args)
        elif sub == "diff":
            return self.diff(sub_args)
        elif sub == "remote":
            return self.remote(sub_args)
        elif sub == "push":
            return self.push(sub_args)
        elif sub == "stash":
            return self.stash_cmd(sub_args)
        elif sub == "tag":
            return self.tag(sub_args)

        return f"git: '{sub}' is not a git command. See 'git --help'."
