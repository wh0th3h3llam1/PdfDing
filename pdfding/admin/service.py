import requests


def get_latest_version() -> str:  # pragma: no cover
    """
    Gets the tag of the latest release of pdfding via the codeberg rest api.
    """

    try:
        latest_release = requests.get('https://codeberg.org/api/v1/repos/mrmn/PdfDing/releases/latest', timeout=1)
        latest_release_json = latest_release.json()

        return latest_release_json['tag_name']
    except Exception:  # pragma: no cover
        return ''
