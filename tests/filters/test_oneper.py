import os
from pathlib import Path
from time import sleep
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
    # try to avoid issues with file creation close to the end of the hour
    if now.minute == 59 and now.second == 59:
        sleep(1)
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
) -> Generator[Tuple[DetectionMethod, List[Path]], None, None]:
    """"""
    paths = files_with_relative_ts
    yield method, paths  # , (paths[expected])


def check_selects_one_with_method(
    method: DetectionMethod,
    paths: List[Path],
    acted: List[Union[bool, int]],
):
    """test the OnePer::pipeline() for one set of files

    :param method: How OnePer should choose "the one" file
    :type method: DetectionMethod
    :param paths: list of file Paths to process
    :type paths: List[Path]
    :param acted: the expected results for each call of the pipeline; the call
            either return `False`, or it will return `True`, and the value of
            `res.path` will be set to a file which is specified by its index
            in the `paths` param;
            e.g., `acted=[False, 1, 2]` indicates: the first call returns
            `False`, the second call returns `True` with `res.path` set to
            `paths[1]`, and the third call returns `True` with `res.path` set
            to `paths[2]`
    :type acted: List[Union[bool, int]]
    """
    ## arrange
    # method, paths, expected = method_and_expect
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


@pytest.mark.parametrize(
    ["offsets", "order", "acted"],
    [
        ([2, 0, 1], None, [False, 0, 2]),
        ([1, 2, 0], None, [False, 1, 0]),
    ],
)
def test_detects_by_lastmodified(files_with_relative_ts, acted):
    """test `OnePer::pipeline()` with the `lastmodified` method

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("lastmodified", files_with_relative_ts, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted"],
    [
        ([0, 2, 1], None, [False, 0, 2]),
        ([0, 1, 2], None, [False, 0, 1]),
    ],
)
def test_reverses_lastmodified(files_with_relative_ts, acted):
    """test `OnePer::pipeline()` with the `lastmodified` method, reversed

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("-lastmodified", files_with_relative_ts, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted"],
    [
        ([3, 2, 1], None, [False, 1, 2]),
        ([5, 5, 5], [1, 0, 2], [False, 0, 2]),
    ],
)
def test_detects_by_created(files_with_relative_ts, acted):
    """test `OnePer::pipeline()` with the `created` method

    This test uses different orders of file creation to alter which files
    are filtered.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("created", files_with_relative_ts, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted"],
    [
        ([1, 2, 3], None, [False, 0, 1]),
        ([5, 5, 5], [0, 2, 1], [False, 0, 2]),
    ],
)
def test_reverses_created(files_with_relative_ts, acted):
    """test `OnePer::pipeline()` with the `created` method, reversed

    This test uses different orders of file creation to alter which files
    are filtered.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("-created", files_with_relative_ts, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted", "seen"],
    [
        # The file indexes for `acted` are based on the `seen` order,
        # not `order` or `offsets`
        ([1, 2, 3], None, [False, 1, 2], [2, 1, 0]),
        ([1, 2, 3], None, [False, 1, 2], [1, 0, 2]),
        ([3, 2, 1], [2, 1, 0], [False, 1, 2], [2, 1, 0]),
    ],
)
def test_detects_by_first_seen(files_with_relative_ts, acted, seen):
    """test `OnePer::pipeline()` with the `first seen` method

    This test changes the order of the paths get processed in when calling
    the pipeline.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    # we want to process the files in different order
    seen_paths: List[Path] = list()
    for i in seen:
        seen_paths.append(files_with_relative_ts[i])

    check_selects_one_with_method("first_seen", seen_paths, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted", "seen"],
    [
        # The file indexes for `acted` are based on the `seen` order,
        # not `order` or `offsets`
        ([3, 2, 1], None, [False, 0, 1], [2, 1, 0]),
        ([3, 2, 1], None, [False, 0, 1], [1, 0, 2]),
        ([3, 2, 1], [2, 1, 0], [False, 0, 1], [0, 1, 2]),
        ([3, 2, 1], [2, 1, 0], [False, 0, 1], [2, 1, 0]),
    ],
)
def test_reverse_first_seen(files_with_relative_ts, acted, seen):
    """test `OnePer::pipeline()` with the `first seen` method, reversed

    This test changes the order of the paths get processed in when calling
    the pipeline.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    # we want to process the files in different order
    seen_paths: List[Path] = list()
    for i in seen:
        seen_paths.append(files_with_relative_ts[i])

    check_selects_one_with_method("-first_seen", seen_paths, acted)


def rename_paths(paths: List[Path], names: List[str]) -> List[Path]:
    """rename a list of files to a list of new file names
    
    :param paths: list of Paths to files that exist
    :type paths: List[Path]
    :param names: list of strings to be used to rename files in `paths`
    :type names: List[str]

    :return: the new list of Paths to the renamed files
    :rtype: List[Path]
    """
    named_paths: List[Path] = list()
    for i in range(len(names)):
        named = paths[i]
        # create a new Path that points to the new name
        new_name = named.with_name(names[i])
        assert not new_name.exists()
        # rename existing file to the new_name
        named.rename(new_name)
        # new_name is now an existing Path, add it to list of files
        named_paths.append(new_name)
        assert not (named).exists()
        assert new_name.exists()

    return named_paths


@pytest.mark.parametrize(
    ["offsets", "order", "names", "acted"],
    [
        ## "a" is expected to be the alphabetical choice of these
        # "b" - oldest file, "c" - youngest file; seen: c, a, b
        ([2, 1, 0], [2, 1, 0], ["c", "a", "b"], [False, 0, 2]),
        # "c" - oldest file, "a" - youngest file; seen: a, b, c
        ([2, 1, 0], [2, 1, 0], ["a", "b", "c"], [False, 1, 2]),
        # "c" - oldest file, "b" - youngest file; seen: c, b, a
        ([0, 2, 1], None, ["c", "b", "a"], [False, 0, 1]),
    ],
)
def test_detects_by_name(files_with_relative_ts, acted, names):
    """test `OnePer::pipeline()` with the `name` method
    
    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    :param names: a list of new file names; the files from 
        `files_with_relative_ts` will be renamed to these names, so we can
        control which files are alpabetically first or last
    """
    # name the files

    named_paths: List[Path] = rename_paths(
        files_with_relative_ts,
        names,
    )

    check_selects_one_with_method("name", named_paths, acted)

@pytest.mark.parametrize(
    ["offsets", "order", "names", "acted"],
    [
        ## "c" is the choice of these, in reverse alphabetical order
        # "b" - oldest file, "c" - youngest file; seen: c, a, b
        ([2, 1, 0], [2, 1, 0], ["c", "a", "b"], [False, 1, 2]),
        # "c" - oldest file, "a" - youngest file; seen: a, b, c
        ([2, 1, 0], [2, 1, 0], ["a", "b", "c"], [False, 0, 1]),
        # "c" - oldest file, "a" - youngest file; seen: c, b, a
        ([0, 1, 2], None, ["c", "b", "a"], [False, 1, 2]),
    ],
)
def test_reverses_name(files_with_relative_ts, acted, names):
    """test `OnePer::pipeline()` with the `name` method, reversed
    
    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    :param names: a list of new file names; the files from 
        `files_with_relative_ts` will be renamed to these names, so we can
        control which files are alpabetically first or last
    """
    # name the files

    named_paths: List[Path] = rename_paths(
        files_with_relative_ts,
        names,
    )

    check_selects_one_with_method("-name", named_paths, acted)
