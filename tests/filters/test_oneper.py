import os
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Union

import pytest
from arrow import Arrow
from pydantic_core import ValidationError

from organize.filters import OnePer
from organize.filters.one_per import DetectionMethod, Period
from organize.output import Default as Output
from organize.resource import Resource


@pytest.fixture(params=["month", "day", "hour", "minute", "second"])
def period(request) -> Period:
    """fixture to loop over valid periods"""
    return request.param


def make_a_path(
    file: str,
    timestamp: Optional[Arrow] = None,
) -> Path:
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
        OnePer(period="fortnight")  # type: ignore[assignment]
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


@pytest.fixture
def files_with_relative_ts(
    fs, offsets: List[int], order: Optional[List[int]]
) -> Generator[List[Path], None, None]:
    """fixture to create several files with timestamps

    Parameters:
    - `offsets`: an array of offsets in seconds for the modified timestamp;
      the value of the offset is added to the time when the function is called
    - `order`: (optional) the order to create the files in; by default, they
      will be created in the natural order provided by the offsets; the value of
      order will be used as the index into the `offsets` list

    Example explaining `offsets` and `order`:
    - `offsets = [2, 0, 1]`
    - `order = None`:
    - Three files will be created:
      - index 0: `/file_0` will be created with its mtime with 2 seconds
        (from `offsets[0] = 2`)
      - index 1: `/file_1`, mtime is +0 (`offsets[1] = 0`)
      - index 2: `/file_2`, mtime is +1 (`offsets[2] = 1`)

    Example 2:
    - `offsets = [5, 5, 5]`
    - `order = [2, 0, 1]`
    - Three files will be created, in the following order:
      - order[0] -> 2 -> offsets[2]: `/file_2`, mtime is +5
      - order[1] -> 0 -> offsets[0]: `/file_0`, mtime is +5
      - order[2] -> 1 -> offsets[1]: `/file_1`, mtime is +5
    """
    now = Arrow.now()

    paths: List[Path] = list()
    for i in range(len(offsets)):
        idx = order[i] if order else i
        offset = offsets[idx]
        mtime = now.shift(seconds=offset)
        paths.append(make_a_path(f"/file_{idx}", mtime))
    yield sorted(paths)


@pytest.fixture
def method_and_expect(
    files_with_relative_ts, method: DetectionMethod, expected: int
) -> Generator[Tuple[DetectionMethod, List[Path], Path], None, None]:
    """"""
    paths = files_with_relative_ts
    yield method, paths, (paths[expected])


@pytest.mark.parametrize(
    ["method", "expected", "offsets", "order", "acted"],
    [
        ("lastmodified", 1, [2, 0, 1], None, [False, 0, 2]),
        ("lastmodified", 2, [1, 2, 0], None, [False, 1, 0]),
        ("-lastmodified", 1, [0, 2, 1], None, [False, 0, 2]),
        ("-lastmodified", 2, [0, 1, 2], None, [False, 0, 1]),
        ("created", 1, [5, 5, 5], [1, 0, 2], [False, 0, 2]),
        ("-created", 1, [5, 5, 5], [0, 2, 1], [False, 0, 2]),
    ],
)
def test_selects_one_with_method(method_and_expect, acted: List[Union[bool, int]]):
    ## arrange
    method, paths, expected = method_and_expect
    op = OnePer(detect_the_one_by=method)

    ## act
    a: List[bool] = list()
    r: List[Resource] = list()
    for path in paths:
        res = Resource(path)
        act = op.pipeline(res, Output())
        a.append(act)
        r.append(res)

    ## assert
    expected_one = paths[0]
    for i, act in enumerate(a):
        res = r[i]
        expected_act = acted[i]
        expected_a = not isinstance(expected_act, bool)

        # pipeline call return expected True|False
        assert act is expected_a

        # the value of res.path is correct
        expected_res_path: Path
        if not expected_a:
            # value of res.path should equal the path the pipeline processed
            expected_res_path = paths[i]
        else:
            # value of res.path should be updated with the previous `the_one`
            expected_res_path = paths[expected_act]
        assert expected_res_path == res.path

        # the vars for our filter should be updated
        if expected_act != i:
            expected_one = paths[i]
        assert expected_one == res.vars[op.filter_config.name]["the_one"]
