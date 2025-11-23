"""
Module for updating the changelog after a release.
"""

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


def update_changelog(changelog_path: Path, release_tag: str, release_body: str):
    """Update the changelog based on the release tag and the release_body."""

    with open(changelog_path, 'r') as f:
        lines = f.readlines()

    now = datetime.now()
    release_date = now.strftime('%b %d, %Y')

    # construct new changelog entry
    changelog_str = '# Changelog\n\n'
    release_header = f'## {release_tag} ({release_date})\n'
    release_body = f'{release_body}\n'
    release_body = release_body.replace(
        "## What's Changed", "### What's Changed"
    )  # make sure release body headers have the right size

    # construct changelog
    lines = [changelog_str, release_header, release_body] + lines[1:]

    with open(changelog_path, 'w') as f:
        f.writelines(lines)


def main():
    parser = ArgumentParser()
    for argument in ['release_tag', 'release_body', 'changelog_path']:
        parser.add_argument(f'--{argument}')
    args = parser.parse_args()

    root_path = Path(__file__).parents[3]
    changelog_path = root_path / args.changelog_path

    release_tag = args.release_tag
    release_body = args.release_body

    update_changelog(changelog_path, release_tag, release_body)


if __name__ == '__main__':
    main()
