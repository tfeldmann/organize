import argparse
import getpass
import re
import subprocess
from datetime import datetime
from pathlib import Path

import requests

SRC_FOLDER = "organize"
CURRENT_FOLDER = Path(__file__).resolve().parent
GITHUB_API_ENDPOINT = "https://api.github.com/repos/tfeldmann/organize"


def ask_confirm(text):
    while True:
        answer = input(f"{text} [y/n]: ").lower()
        if answer in ("j", "y", "ja", "yes"):
            return True
        if answer in ("n", "no", "nein"):
            return False


def set_version(args):
    """
    - reads and validates version number
    - updates __version__.py
    - updates pyproject.toml
    - Searches for 'WIP' in changelog and replaces it with current version and date
    """
    from organize.__version__ import __version__ as current_version

    print(f"Current version is {current_version}.")

    # read version from input if not given
    version = args.version

    if not version:
        version = input("Version number: ")

    # validate and remove 'v' if present
    version = version.lower()
    if not re.match(r"v?\d+\.\d+.*", version):
        return
    if version.startswith("v"):
        version = version[1:]

    # safety check
    if not ask_confirm(f"Creating version v{version}. Continue?"):
        return

    # update library version
    versionfile = CURRENT_FOLDER / SRC_FOLDER / "__version__.py"
    with open(versionfile, "w") as f:
        print(f"Updating {versionfile}")
        f.write(f'__version__ = "{version}"\n')

    # update poetry version
    print("Updating pyproject.toml")
    subprocess.run(["poetry", "version", version], check=True)

    # read changelog
    print("Updating CHANGELOG.md")
    with open(CURRENT_FOLDER / "CHANGELOG.md", "r") as f:
        changelog = f.read()

    # check if WIP section is in changelog
    wip_regex = re.compile(r"## WIP\n(.*?)(?=\n##)", re.MULTILINE | re.DOTALL)
    match = wip_regex.search(changelog)
    if not match:
        print('No "## WIP" section found in changelog')
        return

    # change WIP to version number and date
    changes = match.group(1)
    today = datetime.now().strftime("%Y-%m-%d")
    changelog = wip_regex.sub(f"## v{version} ({today})\n{changes}", changelog, count=1)

    # write changelog
    with open(CURRENT_FOLDER / "CHANGELOG.md", "w") as f:
        f.write(changelog)

    if ask_confirm("Commit changes?"):
        subprocess.run(
            ["git", "add", "pyproject.toml", "__version__.py", "CHANGELOG.md"]
        )
        subprocess.run(["git", "commit", "-m", f"bump version to v{version}"])

    print("Please push to github and wait for CI to pass.")
    print("Success.")


def publish(args):
    """
    - reads version
    - reads changes from changelog
    - creates git tag
    - pushes to github
    - publishes on pypi
    - creates github release
    """
    from organize.__version__ import __version__ as version

    if not ask_confirm(f"Publishing version {version}. Is this correct?"):
        return

    # extract changes from changelog
    with open(CURRENT_FOLDER / "CHANGELOG.md", "r") as f:
        changelog = f.read()
    wip_regex = re.compile(
        "## v{}".format(version.replace(".", r"\.")) + r".*?\n(.*?)(?=\n##)",
        re.MULTILINE | re.DOTALL,
    )
    match = wip_regex.search(changelog)
    if not match:
        print("Failed to extract changes from changelog. Do the versions match?")
        return
    changes = match.group(1).strip()
    print(f"Changes:\n{changes}")

    # create git tag ('vXXX')
    if ask_confirm("Create tag?"):
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"v{version}"])

    # push to github
    if ask_confirm("Push to github?"):
        print("Pushing to github")
        subprocess.run(["git", "push", "--follow-tags"], check=True)

    # upload to pypi
    if ask_confirm("Publish on Pypi?"):
        subprocess.run(["rm", "-rf", "dist"], check=True)
        subprocess.run(["poetry", "build"], check=True)
        subprocess.run(["poetry", "publish"], check=True)

    # create github release
    if ask_confirm("Create github release?"):
        response = requests.post(
            f"{GITHUB_API_ENDPOINT}/releases",
            auth=(input("Benutzer: "), getpass.getpass()),
            json={
                "tag_name": f"v{version}",
                "target_commitish": "master",
                "name": f"v{version}",
                "body": changes,
                "draft": False,
                "prerelease": False,
            },
        )
        response.raise_for_status()

    print("Success.")


def main():
    assert CURRENT_FOLDER == Path.cwd().resolve()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_version = subparsers.add_parser("version", help="Set the version number")
    parser_version.add_argument(
        "version", type=str, help="The version number", nargs="?", default=None
    )
    parser_version.set_defaults(func=set_version)

    parser_publish = subparsers.add_parser("publish", help="Publish the project")
    parser_publish.set_defaults(func=publish)

    args = parser.parse_args()
    if not vars(args):
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
