import re
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


LIB_NAME = "organize"
CURRENT_FOLDER = Path(__file__).resolve().parent


def new_version(args):
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
    versionfile = CURRENT_FOLDER / LIB_NAME / "__version__.py"
    with open(versionfile, "w") as f:
        print(f"Updating {versionfile}")
        f.write(f'__version__ = "{version}"\n')

    # update poetry version
    print("Updating pyproject.toml")
    subprocess.run(["poetry", "version", version], check=True)

    with open(CURRENT_FOLDER / "CHANGELOG.md", "r") as f:
        changelog = f.read()

        # check if WIP section is in changelog
        if "## WIP" not in changelog:
            print("No work in progress found in changelog")
            return

        # change WIP to version number and date
        changelog = changelog.replace(
            "## WIP",
            f"## v{version} (" + datetime.now().strftime("%Y-%m-%d") + ")",
            1,
        )
    with open(CURRENT_FOLDER / "CHANGELOG.md", "w") as f:
        f.write(changelog)

    # create git tag ('vXXX')
    # push to origin
    # create github release with changelog
    # upload to pypi
    # trigger readthedocs
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
