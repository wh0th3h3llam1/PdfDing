"""Module for updating the Chart.yaml file PdfDing's helm chart after a release"""

from os import environ
from pathlib import Path

from github import Auth, Github


def update_versions_after_release(chart_yaml_path: Path, release_tag: str) -> str:
    """
    Update the chart version and app version of the helm chart after a release. The chart version's patch will
    be incremented by 1, the app version will be replaced by the 'release_tag'.
    """

    with open(chart_yaml_path, 'r') as f:
        lines = f.readlines()

    app_version_line = lines.pop()
    chart_version_line = lines.pop()

    # check if the appVersion needs to be updated
    if f'appVersion: {release_tag}' in app_version_line:
        raise ValueError('appVersion is equal to release tag')

    # update chart version
    chart_version_line_split = chart_version_line.rsplit('.', maxsplit=1)
    patch = chart_version_line.split('.')[-1]
    updated_patch = int(patch) + 1
    updated_chart_version_line = f'{chart_version_line_split[0]}.{updated_patch}\n'

    # update appVersion
    updated_app_version_line = f'appVersion: {release_tag}\n'

    # update lines
    lines.extend([updated_chart_version_line, updated_app_version_line])

    return ''.join(lines)


def gh_update_chart_yaml(
    repo: str,
    branch: str,
    file_path: str,
    chart_yaml_content: str,
    release_tag: str,
    github_token: str,
):
    """
    Update the Chart.yaml after a release, create a commit and push it to the specified branch. The chart version's
    patch will be incremented by 1, the app version will be replaced by the 'release_tag'.
    """

    auth = Auth.Token(github_token)
    g = Github(auth=auth)

    repo = g.get_repo(repo)
    contents = repo.get_contents(file_path, ref=branch)
    repo.update_file(
        contents.path,
        f'Update helm chart for release "{release_tag}"',
        chart_yaml_content,
        contents.sha,
        branch=branch,
    )


def main():
    file_path = 'helm-charts/pdfding/Chart.yaml'
    chart_yaml_path = Path(__file__).parents[3] / file_path
    release_tag = environ.get('RELEASE_TAG')
    github_token = environ.get('GITHUB_TOKEN')

    try:
        chart_yaml_content = update_versions_after_release(chart_yaml_path, release_tag)
        gh_update_chart_yaml('mrmn2/pdfding', 'master', file_path, chart_yaml_content, release_tag, github_token)
    # appVersion does not need to be updated
    except ValueError:
        pass


if __name__ == '__main__':
    main()
