"""
Module for updating the changelog and Chart.yaml files after a release. The chart.yaml will only be upgraded if the
appVersion has changed.
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
    release_header = f'##  {release_tag} ({release_date})\n'
    release_body = f'{release_body}\n'

    # construct changelog
    lines = [changelog_str, release_header, release_body] + lines[1:]

    with open(changelog_path, 'w') as f:
        f.writelines(lines)


def update_chart_yaml_after_release(chart_yaml_path: Path, release_tag: str):
    """
    Update the chart version and app version of the helm chart after a release. The chart version's patch will
    be incremented by 1, the app version will be replaced by the 'release_tag'.
    """

    with open(chart_yaml_path, 'r') as f:
        lines = f.readlines()

    app_version_line = lines.pop()
    chart_version_line = lines.pop()

    # check if the appVersion needs to be updated
    if f'appVersion: {release_tag}' != app_version_line.strip():
        # update chart version
        chart_version_line_split = chart_version_line.rsplit('.', maxsplit=1)
        patch = chart_version_line.split('.')[-1]
        updated_patch = int(patch) + 1
        updated_chart_version_line = f'{chart_version_line_split[0]}.{updated_patch}\n'

        # update appVersion
        updated_app_version_line = f'appVersion: {release_tag}\n'

        # update chart.yaml
        lines.extend([updated_chart_version_line, updated_app_version_line])

        with open(chart_yaml_path, 'w') as f:
            f.writelines(lines)


def main():
    parser = ArgumentParser()
    for argument in ['release_tag', 'release_body', 'changelog_path', 'chart_yaml_path']:
        parser.add_argument(f'--{argument}')
    args = parser.parse_args()

    root_path = Path(__file__).parents[3]
    changelog_path = root_path / args.changelog_path
    chart_yaml_path = root_path / args.chart_yaml_path

    release_tag = args.release_tag
    release_body = args.release_body

    update_chart_yaml_after_release(chart_yaml_path, release_tag)
    update_changelog(changelog_path, release_tag, release_body)


if __name__ == '__main__':
    main()
