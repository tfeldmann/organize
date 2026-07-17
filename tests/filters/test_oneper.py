import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Generator, List, Optional, Union

import pytest
from arrow import Arrow
from arrow import get as arrow_get
from pydantic_core import ValidationError
from pyfakefs.fake_filesystem import FakeFilesystem
from pyfakefs.fake_filesystem_unittest import Patcher

from organize import Config
from organize.filters import OnePer
from organize.filters.one_per import DetectionMethod, Period
from organize.output import Default as Output
from organize.resource import Resource

FakeOrTmpFileSystem = Union[FakeFilesystem, Path]


@pytest.fixture(params=["month", "day", "hour", "minute", "second"])
def period(request) -> Period:
    """fixture to loop over valid periods"""
    return request.param


def make_fake_path(
    fs: FakeOrTmpFileSystem,
    file: str,
    mtime: Optional[Arrow] = None,
    ctime: Optional[Arrow] = None,
    _last: bool = False,
) -> Path:
    """create a fake file with optional timestamps

    :param fs: pyfakefs FakeFilesystem (from fixture)
    :param file: the path the the file to create
    :type file: str
    :param mtime: optional Arrow time to use for the last modified
        time of the file
    :type mtime: Arrow
    :param ctime: optional Arrow time to use for the creation
        time of the file
    :type ctime: Arrow
    :return: the Path to the new file
    :rtype: Path
    """
    assert isinstance(fs, FakeFilesystem)
    fake_file = fs.create_file(file)
    path = Path(file)
    if mtime:
        fake_file.st_mtime = mtime.timestamp()
    if ctime:
        fake_file.st_ctime = ctime.timestamp()

    if mtime:
        mts = arrow_get(path.stat().st_mtime)
        assert mts == mtime
    if ctime:
        mts = arrow_get(path.stat().st_ctime)
        assert mts == ctime

    return path


def make_tmp_path(
    tmp_path: FakeOrTmpFileSystem,
    file: str,
    mtime: Optional[Arrow] = None,
    ctime: Optional[Arrow] = None,
    last: bool = False,
) -> Path:
    """Create a real file in a temporary location.

    If the caller cares about the order of file creation, and this is NOT the
    last file being created for this test case, then this function will sleep
    for 1 second before returning, to ensure that each file has a separate
    creation time, and that the ordering of the file creation times matches
    what the test case expects.

    :param tmp_path: a safe location for tmp files for this test execution
    :param file: the path to the file we want to create
    :param mtime: an optional Arrow timestamp to use for the lastmodified time
    :param ctime: an optional Arrow timestamp to use for the file creation time;
        it is actually impossible to change or specify this, so we mainly use
        this to indicate that we care about the creation order
    :param last: is this the last file for this test case, or will there be more
    """
    assert isinstance(tmp_path, Path)
    tmp_file = tmp_path / file.lstrip("/")
    tmp_file.touch()

    if ctime:
        os.utime(tmp_file, (ctime.timestamp(), ctime.timestamp()))
    elif mtime:
        os.utime(tmp_file, (mtime.timestamp(), mtime.timestamp()))

    # It is impossible to modify the file creation timestamp on real files. If
    # a test needs to validate that files are created in a specific order, then
    # we need to do two things:
    # - have at least one second delay between creating each file
    # - make sure that the "hour" is the same for each file -- this is very
    #   specific to these tests, but since we have to delay between each file,
    #   we want to make sure that we do not end up creating files that are
    #   in different "hour" periods.
    #
    # Here, we will sleep 1 second in between each file creation. If this is the
    # last file, we will not sleep. If no ctime was provided, we won't sleep,
    # either, but there is currently no use case for creating real files outside
    # of controlling the order of creation.
    if ctime and not last:
        time.sleep(1)
    return tmp_file


def make_files_with_relative_ts(
    my_fs: Union[FakeFilesystem, Path],
    offsets: List[int],
    order: Optional[List[int]],
    maker: Callable[
        [FakeOrTmpFileSystem, str, Optional[Arrow], Optional[Arrow], bool],
        Path,
    ] = make_fake_path,
) -> list[Path]:
    """function that implements the `files_with_relative_ts` fixture.

    Create all the files expected by a test case, either fake, using pyfakefs,
    or real temporary files.

    :param my_fs: either the FakeFilesystem instance, or a safe path for tmp files
    :param offsets: an array of offsets in seconds for the timestamp for each file
         there should always be one offset for each file desired
    :param order: an array of offsets for the creation timestamp; these are
         treated as seconds to add to the creation time when using pyfakefs,
         but as the order of creation when using real tmp files; e.g., an order
         of `[1, 0, 2]` will create `file_1` first, then `file_0`, and finally
         `file_2` last.
    :param maker: a function used to create the files; one version uses
         pyfakefs, and the other version uses real tmp files
    """
    ctime: Optional[Arrow] = None
    now = Arrow(2026, 7, 12, 15)
    paths: List[Path] = list()
    count = len(offsets)
    for idx in range(count):
        i = order[idx] if order else idx
        mtime = now.shift(seconds=offsets[i])
        if order:
            ctime = now.shift(seconds=order[i])
        paths.append(maker(my_fs, f"/file_{i}", mtime, ctime, (idx + 1) >= count))
    return sorted(paths)


@pytest.fixture
def files_with_relative_ts(
    fs, offsets: List[int], order: Optional[List[int]]
) -> list[Path]:
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
    return make_files_with_relative_ts(fs, offsets, order)


@pytest.fixture
def may_need_real_files(
    tmp_path,
    offsets: list[int],
    order: Optional[list[int]],
) -> Generator[list[Path], None, None]:
    """create files where we care about the creation timestamp

    Create all the files expected by a test case, either fake, using pyfakefs,
    or real temporary files.

    On Windows, we can use pyfakefs, since the Windows implementation uses
    pure python to get the file creation time.

    On Linux or MacOS, we use an external command to get the file birthtime, and
    it won't work with pyfakefs. On those OSes, we have to create real files,
    and we have to be careful to ensure that the files have creation timestamps
    in the order that the test case expects.

    This function calls `make_files_with_relative_ts()`.

    On Windows, the default behavior of `make_files_with_relative_ts()` is
    expected.

    On non-Windows systems, we first ensure that the real files will all be
    created within the same clock hour, and then call
    `make_files_with_relative_ts()` with the `tmp_path` value, and specify it
    should create real files in that location.

    :param tmp_path: safe location for tmp file creation, from a pytest fixture
    :param offsets: list of modification timestamp offsets for each file; this
        also controls how many files are created
    :param order: optional list of creation timestamp offsets
    """
    if sys.platform == "win32":
        with Patcher() as patcher:
            # When creating pyfakefs files, we need to take care of the patching
            # to ensure the fake filesystem gets used. This is handled
            # automatically when using the `fs` fixture, but since we don't want
            # to patch if we are testing on non-Windows systems, we have to
            # do the patching manually
            assert patcher.fs is not None
            yield make_files_with_relative_ts(patcher.fs, offsets, order)
    else:
        # It is impossible to modify the file creation timestamp on real files. If
        # a test needs to validate that files are created in a specific order, then
        # we need to do two things:
        # - have at least one second delay between creating each file
        # - make sure that the "hour" is the same for each file -- this is very
        #   specific to these tests, but since we have to delay between each file,
        #   we want to make sure that we do not end up creating files that are
        #   in different "hour" periods.
        #
        # Here, we want to make sure that we have enough time to create all the
        # files, plus the delays between each file, and keep them all with
        # creation times in the same hour
        now = Arrow.now()
        count = len(offsets)
        later = now.shift(seconds=count)
        if now.hour != later.hour:
            time.sleep(count)
        yield make_files_with_relative_ts(tmp_path, offsets, order, maker=make_tmp_path)


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


def test_tracks_seen_files(fs):
    """our filter should keep track of files that it processes"""
    ## organize
    # create a single file
    op = OnePer()
    a = make_fake_path(fs, "/a")
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
    real_file = make_fake_path(fs, "/real_file")
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
    f = make_fake_path(fs, "/f", now)

    ## act
    processed = op.pipeline(Resource(f), Output())

    ## assert
    # one file should not find extras to process
    assert not processed

    # the period for the file should be known
    assert file_period in op._the_one_for_period

    # with only one file, it should be the one for its period
    assert op._the_one_for_period[file_period] is f


def check_selects_one_with_method(
    method: DetectionMethod,
    paths: List[Path],
    acted: List[Union[bool, int]],
):
    """test the OnePer::pipeline() for one set of files

    This performs the actual validation of `OnePer::pipeline()`.

    :param method: How OnePer should choose "the one" file
    :type method: DetectionMethod
    :param paths: list of file Paths to process, in the order to process them
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
def test_detects_by_created(may_need_real_files, acted):
    """test `OnePer::pipeline()` with the `created` method

    This test uses different orders of file creation to alter which files
    are filtered.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("created", may_need_real_files, acted)


@pytest.mark.parametrize(
    ["offsets", "order", "acted"],
    [
        ([1, 2, 3], None, [False, 0, 1]),
        ([5, 5, 5], [0, 2, 1], [False, 0, 2]),
    ],
)
def test_reverses_created(may_need_real_files, acted):
    """test `OnePer::pipeline()` with the `created` method, reversed

    This test uses different orders of file creation to alter which files
    are filtered.

    :param files_with_relative_ts: a test fixture that generates files with
        relative modification timestamps, and optionally in a specified order
        of file creation
    :param acted: the expected results (see `check_selects_one_with_method`)
    """
    check_selects_one_with_method("-created", may_need_real_files, acted)


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


#####
# tests that execute an actual Config

# the config
# this uses the default values for `one_per`:
# - period: hour
# - detect_the_one_by: lastmodified
CONFIG_ONE_PER_DELETE = """
rules:
  - locations: "."
    filters:
      - one_per
    actions:
      - delete
"""

# files and lastmodified timestamps for the first period
# period is 2026-July-8@15:00:00
period_one = Arrow(2026, 7, 8, 15)
period_one_files = {
    # path to file: lastmodified timestamp of file
    "/q": period_one.shift(minutes=1),
    "/w": period_one.shift(minutes=3),
    "/e": period_one.shift(minutes=21),
    "/r": period_one.shift(minutes=37),
    "/t": period_one.shift(minutes=59),
    "/y": period_one.shift(minutes=1, seconds=1),
}

# files and lastmodified timestamps for the first period
# period is 2026-July-8@16:00:00
period_two = period_one.shift(hours=1)
period_two_files = {
    # path to file: lastmodified timestamp of file
    "/z": period_two.shift(minutes=1),
    "/x": period_two.shift(minutes=3),
    "/c": period_two.shift(minutes=21),
    "/v": period_two.shift(minutes=37),
    "/b": period_two.shift(minutes=59),
    "/n": period_two.shift(minutes=1, seconds=1),
}


def test_one_period(fs):
    """test with all files in the same period - remove all except earliest"""
    for file in sorted(period_one_files):
        make_fake_path(fs, file, period_one_files[file])

    for file in sorted(period_one_files):
        assert Path(file).exists()

    Config.from_string(CONFIG_ONE_PER_DELETE).execute(simulate=False)

    # the earliest file in the period should exist ("/q")
    assert Path("/q").exists()
    for file in period_one_files:
        if file == "/q":
            assert Path(file).exists()
        else:
            # files other than "/q" should not exist
            assert not Path(file).exists()


def test_two_periods(fs):
    """test with two different periods - keep earliest file from each period"""
    both_periods = period_one_files | period_two_files
    for file in sorted(both_periods):
        make_fake_path(fs, file, both_periods[file])

    Config.from_string(CONFIG_ONE_PER_DELETE).execute(simulate=False)

    # the earliest file in period one should exist ("/q")
    assert Path("/q").exists()
    # the earliest file in period two should exist ("/z")
    assert Path("/z").exists()
    for file in both_periods:
        if (file == "/q") or (file == "/z"):
            assert Path(file).exists()
        else:
            # files other than "/q" or "/z" should not exist
            assert not Path(file).exists()


CONFIG_WITH_COMPLICATED_PYTHON = """
rules:
  - name: "0"
    locations: "."
    filters:
      - python: |
          import arrow
          ts = arrow.get(path.stat().st_mtime)
          earliest = ts.floor("hour")
          latest = earliest.shift(minutes=30)
          return (ts >= earliest) and (ts < latest)
      - one_per
    actions:
      - delete
  - name: "30"
    locations: "."
    filters:
      - python: |
          import arrow
          ts = arrow.get(path.stat().st_mtime)
          earliest = ts.floor("hour").shift(minutes=30)
          latest = earliest.shift(minutes=30)
          return (ts >= earliest) and (ts < latest)
      - one_per
    actions:
      - delete
"""


def test_with_python_and_arrow(fs):
    """test with a complicated config that uses python and arrow

    This tests a config that restricts a time range to a portion of an hour. For
    each hour, keep the earliest file with a timestamp between 0 and 30 minutes,
    and the earliest file with a timestamp between 30 and 60 minutes.
    """
    both_periods = period_one_files | period_two_files
    for file in sorted(both_periods):
        make_fake_path(fs, file, both_periods[file])

    Config.from_string(CONFIG_WITH_COMPLICATED_PYTHON).execute(simulate=False)

    expected: List[str] = list()
    # period_one: 00-30
    expected.append("/q")
    # period_one: 30-00
    expected.append("/r")
    # period_two: 00-30
    expected.append("/z")
    # period_two: 30-00
    expected.append("/v")

    # "/q", "/r", "/z", and "/v" should all exist
    for file in expected:
        assert Path(file).exists()

    for file in both_periods:
        if file in expected:
            assert Path(file).exists()
        else:
            # files other than "/q", "/r", "/z", and "/v" should not exist
            assert not Path(file).exists()
