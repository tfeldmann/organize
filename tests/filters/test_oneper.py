import os
from pathlib import Path

import pytest
from arrow import Arrow
from pydantic_core import ValidationError

from organize.filters import OnePer
from organize.filters.one_per import Period
from organize.output import Default as Output
from organize.resource import Resource


@pytest.fixture(params=["month", "day", "hour", "minute", "second"])
def period(request) -> Period:
    """fixture to loop over valid periods"""
    return request.param


def make_a_path(file: Path | str, timestamp: Arrow | None = None) -> Path:
    """make sure file exists and has a specific timestamp"""
    # make sure file exists
    path = Path(file)
    path.touch()

    # set timestamp
    if timestamp is not None:
        ts = timestamp.timestamp()
        os.utime(path, (ts, ts))

    return path


def test_tracks_seen_files(fs):
    """our filter should keep track of files that it processes"""
    ## organize
    # create a single file
    op = OnePer()
    a = make_a_path("/a")
    r = Resource(a)

    ## act
    processed = op.pipeline(r, Output())

    ## assert
    # with only one file handled, no files are found to process
    assert not processed
    # our file should be tracked
    assert a in op._seen_files


def test_skips_symlinks(fs):
    """our filter should ignore symlink files"""
    ## organize
    # create a file and a symlink to it
    op = OnePer()
    real_file = make_a_path("/real_file")
    link_file = Path("/link_file")
    link_file.symlink_to(real_file)

    ## act
    # filter our symlink
    processed = op.pipeline(Resource(link_file), Output())

    ## assert
    # no files should be found to process
    assert not processed
    # the symlink should not be tracked, it should just be skipped
    assert link_file not in op._seen_files


def test_valid_periods(period):
    """our filter should allow valid periods"""
    # can we set up the filter with this period?
    # this will raise an exception if not, and the test will fail
    OnePer(period=period)


def test_invalid_period():
    """an invalid period should raise an exception"""
    try:
        OnePer(period="fortnight")
        assert False, "Unexpected period allowed"
    except ValidationError:
        assert True


def test_tracks_file_period(fs, period):
    """filtering a file should track the file's period"""
    op = OnePer(period=period)

    ## organize
    # possible time stamps
    now = Arrow(2026, 6, 26, 17, 8, 32, 123)
    # expected period for the file
    file_period = now.floor(period)
    f = make_a_path("/f", now)

    ## act
    processed = op.pipeline(Resource(f), Output())

    ## assert
    # one file should not find extras to process
    assert not processed

    # the period for the file should be known
    assert file_period in op._the_one_for_period

    # with only one file, it should be the one for its period
    assert op._the_one_for_period[file_period] is f
