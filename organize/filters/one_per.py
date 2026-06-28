from pathlib import Path
from typing import ClassVar, Literal, Tuple

from arrow import Arrow
from arrow import get as arrow_get
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource

# allowable values for `period`
Period = Literal[
    "month",
    "day",
    "hour",
    "minute",
    "second",
]

# allowable values for `detect_the_one_by`
DetectionMethod = Literal[
    "first_seen",
    "-first_seen",
    "last_seen",
    "-last_seen",
    "name",
    "-name",
    "created",
    "-created",
    "lastmodified",
    "-lastmodified",
]


@dataclass(config=ConfigDict(extra="forbid"))
class OnePer:
    """Group files by modification time.

    This filter finds files that were modified in a given time period, except
    for the earliest file from the time period.

    Attributes:
        detect_the_one_by (str):
            Detection method to distinguish between original and duplicate.
            Possible values are:

            - `"first_seen"`: Whatever file is visited first is the original. This
              depends on the order of your location entries.
            - `"name"`: The first entry sorted by name is the original.
            - `"created"`: The first entry sorted by creation date is the original.
            - `"lastmodified"`: The first file sorted by date of last modification is
               the original.

        period (str):
            The period to group files into.
            Possible values are:

            - `"second"`
            - `"minute"`
            - `"hour"`
            - `"day"`
            - `"month"`
    """

    period: Period = "hour"
    detect_the_one_by: DetectionMethod = "lastmodified"

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="one_per", files=True, dirs=True
    )

    def __post_init__(self):
        """set up initial state of the filter, based on the filter options"""
        self._detect_the_one_by = self.detect_the_one_by
        self._detect_the_one_reverse = False
        if self.detect_the_one_by.startswith("-"):
            self._detect_the_one_by = self.detect_the_one_by[1:]
            self._detect_the_one_reverse = True

        # track files we have already seen before
        self._seen_files: set[Path] = set()
        # for each period, the file that is "the_one"
        self._the_one_for_period: dict[Arrow, Path] = dict()
        # does our detection method need the timestamp?
        self._track_timestamps: bool = False
        if self._detect_the_one_by in ["created", "lastmodified"]:
            # this detection method uses the file timestamp, so keep it for
            # each period
            self._ts_for_the_one: dict[Arrow, Arrow] = dict()
            self._track_timestamps = True

    def get_period(self, file: Path) -> Tuple[Arrow, Arrow]:
        """get the timestamp for the file and the period for the timestamp

        A period is the earliest possible timestamp for grouping files that are
        in the same group, regardless of whether we are looking for the oldest
        or newest files.

        Since we always have to get the timestamp in order to get the period, we
        return it here so that we don't have to get it again if we need to use
        it.

        :param file: the path to the file whose period we want
        :type file: Path

        :return: a tuple with (period, timestamp)
        :rtype: tuple
        """
        if self._detect_the_one_by == "created":
            # if detection method is file creation time, use that as timestamp
            ts = arrow_get(file.stat().st_ctime)
        else:
            # for all other detection methods, use the file modification time
            ts = arrow_get(file.stat().st_mtime)
        # period for `path`
        period = ts.floor(self.period)

        return period, ts

    def is_the_one(self, period: Arrow, path: Path, ts: Arrow) -> bool:
        """check if `path` should be the one

        :param period: - the period for `path`
        :type period: Arrow
        :param path: - the file we are checking
        :type path: Path
        :param ts: - the timestamp for `path`
        :type ts: Arrow

        :return: is `path` the new `the_one`
        :rtype: bool
        """
        it_is = ts < self._ts_for_the_one[period]
        if self._detect_the_one_reverse:
            return not it_is
        return it_is

    def update_the_one(self, period: Arrow, path: Path, ts: Arrow) -> None:
        """update our internal tracker for `the_one`

        :param period: - the period for `path`
        :type period: Arrow
        :param path: - the Path to `the_one`
        :type path: Path
        :param ts: - the timestamp for `path`
        :type ts: Arrow
        """
        self._the_one_for_period[period] = path
        if self._track_timestamps:
            self._ts_for_the_one[period] = ts

    def pipeline(self, res: Resource, output: Output) -> bool:
        """Process one file through this filter.

        Since we are looking for files that can be grouped together by their
        timestamps, this may emit:
        - `False`, stop processing this file in other filters or actions
        - `True`, process this file in other filters/actions
        - `True`, process a different file in other filters/actions

        The actual file that gets processed further down the pipeline is
        identified by this method returning `True`, and by the value of
        `res.path`. We can change which file other pipelines will process by
        updating `res`.

        :param res: the Resource for this filter to process; this might be
                    modified to force futher pipelines to use a different
                    Resource
        :type res: Resource
        :param output: not used in this filter
        :type output: Output
        :return: continue processing `res` in other filters/actions
        :rtype: bool
        """
        assert res.path is not None, "Does not support standalone mode"

        # skip if symlink
        if res.path.is_symlink():
            return False

        # skip if we have already processed this file
        if res.path in self._seen_files:
            return False
        self._seen_files.add(res.path)

        # get the period for this file
        period, ts = self.get_period(res.path)

        # get the_one, if this is the first file in period, it is the_one
        the_one = self._the_one_for_period.get(period, res.path)

        # assume we do not want to continue processing this file
        process_it: bool = False

        if the_one != res.path:
            # if the_one is different from current file, at least one of them
            # will be processed (can only be same for first file)
            process_it = True

            # compare against current one for this period
            if self.is_the_one(period, res.path, ts):
                # this file is the new the_one
                previous = the_one
                new_one = res.path

                # save the_one and its timestamp
                self.update_the_one(period, res.path, ts)

                # switch which file gets processed
                res.path = previous
                the_one = new_one
        else:
            # no files in this period yet, this one is the one
            self.update_the_one(period, the_one, ts)

        # done processing, update vars and return value
        res.vars[self.filter_config.name] = {"the_one": the_one}
        return process_it
