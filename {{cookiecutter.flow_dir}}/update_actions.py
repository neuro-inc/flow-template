"""Scans directories for files that satisfy a specific mask and updates
version tags of all actions.

Example:
    python3 update_actions.py live.yml action.y*ml folder/*.y*ml
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional

from github import Github

ACTION_PATTERN = r"\s+action:\s*(?P<svc>gh|github):(?P<org>[\w-]+)/(?P<repo>[\w-]+)@(?P<cur_tag>[\w.]+)"  # noqa: E501


def main():
    args = parse_args()
    patterns: List[str] = args.patterns
    token: Optional[str] = args.token
    if args.root:
        root = Path(args.root).resolve()
    else:
        root = Path(__file__).parent.resolve()
    update_actions(patterns, root, token)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "patterns",
        metavar="PATTERN",
        nargs="+",
        help="Apolo-flow workflow file, which should be scanned for action updates.",
    )
    parser.add_argument("--token", nargs="?", help="GitHub token to use.")
    parser.add_argument(
        "--root",
        nargs="?",
        help="Directory, where to start searching for workflow files",
    )
    return parser.parse_args()


def update_actions(patterns: List[str], root_dir: Path, gh_token: Optional[str]):
    github_client = Github(gh_token)
    action_string_pattern = re.compile(ACTION_PATTERN)

    # action_file_rel_path: [found_actions, updated_actions]
    update_stats: Dict[str, List[int, int]] = {}

    for pattern in patterns:
        for file_path in root_dir.rglob(pattern):
            found_actions = 0
            updated_actions = 0
            new_file_content = []
            rel_path = str(file_path.relative_to(root_dir))
            for line in file_path.read_text().splitlines(keepends=True):
                match = action_string_pattern.match(line)
                if match:
                    found_actions += 1
                    gh_repo = github_client.get_repo(f"{match['org']}/{match['repo']}")
                    current_tag = match["cur_tag"]
                    release_tags = [rel.tag_name for rel in gh_repo.get_releases()]
                    if not release_tags:
                        print(f"No releases found for '{gh_repo.full_name}' action")
                    elif current_tag not in release_tags:
                        print(
                            f"Ignoring '{gh_repo.full_name}' action in '{rel_path}',"
                            " since it is not refferenced by the release tag,"
                            f" but by '{current_tag}'."
                        )
                    else:
                        latest_tag = release_tags[0]
                        if latest_tag != current_tag:
                            updated_actions += 1
                            line = line.replace(current_tag, latest_tag)
                new_file_content.append(line)
            file_path.write_text("".join(new_file_content))
            update_stats[rel_path] = [found_actions, updated_actions]
    pr_body_lines = [
        "::set-output name=updated_files::",
    ]
    for filename in update_stats:
        pr_body_lines.append(
            f"{filename}: found {update_stats[filename][0]} "
            f"updated {update_stats[filename][1]} actions; "
        )
    # The output afterwards will be used by GH CI to submit a PR.
    print("".join(pr_body_lines))


if __name__ == "__main__":
    main()
