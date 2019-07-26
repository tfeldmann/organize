import re
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


SRC_FOLDER = "organize"
CURRENT_FOLDER = Path(__file__).resolve().parent


def new_version(args):
    """ creates and publishes a new version
    - read and validate version number
    - update __version__.py
    - update pyproject.toml
    - Search for 'WIP' in changelog and replace with current version and date
    - create git tag
    - push to github
    - publish on pypi
    """
    assert CURRENT_FOLDER == Path.cwd().resolve()
    version = args.version

    # read version from input if not given
    if not version:
        version = input("Version number: ")

    # validate and remove 'v' if present
    version = version.lower()
    if not re.match(r"v?\d+\.\d+.*", version):
        return
    if version.startswith("v"):
        version = version[1:]

    # safety check
    if input(f"Creating version v{version}. Continue? [Y/n]").lower() not in ["", "y"]:
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
    with open(CURRENT_FOLDER / "CHANGELOG.md", "r") as f:
        changelog = f.read()

    # check if WIP section is in changelog
    wip_regex = re.compile(r"## WIP\n(.*?)(?=\n##)", re.MULTILINE | re.DOTALL)
    match = wip_regex.search(changelog)
    if not match:
        print("No '## WIP' section found in changelog")
        return

    # change WIP to version number and date
    changes = match.group(1)
    today = datetime.now().strftime("%Y-%m-%d")
    changelog = wip_regex.sub(f"## v{version} ({today})\n{changes}", changelog, count=1)

    # write changelog
    with open(CURRENT_FOLDER / "CHANGELOG.md", "w") as f:
        f.write(changelog)

    # create git tag ('vXXX')
    if input("Create tag? [Y/n]").lower() in ["", "y"]:
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"v{version}"])

    # push to github
    if input("Push to github? [Y/n]").lower() in ["", "y"]:
        print("Pushing to github")
        subprocess.run(["git", "push", "--follow-tags"], check=True)

    # upload to pypi
    if input("Publish on Pypi? [Y/n]").lower() in ["", "y"]:
        subprocess.run(["rm", "-rf", "dist"], check=True)
        subprocess.run(["poetry", "build"], check=True)
        subprocess.run(["poetry", "publish"], check=True)

    # TODO: create github release with changelog
    # TODO: trigger readthedocs?
    print("done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_new_version = subparsers.add_parser("new_version")
    parser_new_version.add_argument(
        "version", type=str, help="The version number", nargs="?", default=None
    )
    parser_new_version.set_defaults(func=new_version)

    pargs = parser.parse_args()
    pargs.func(pargs)
