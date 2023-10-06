import collections
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, DefaultDict, Dict, Mapping, Optional, Union


from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from .filter import Filter, FilterResult
from .utils import deep_search

QtffValue = Union[datetime, date, timedelta, str]
QtffDict = Mapping[str, Union[QtffValue, Mapping[str, QtffValue]]]


def to_datetime(key: str, value: str) -> QtffValue:
    """
    Converts qtff date fields to datetime objects
        the value will convert to datetime if the key contains date
        unless the lenth of value is less then 19, then it will convert to date
        
    Args:
        key (str): Key of entry in ExifDict
        value (str): Value of entry in ExifDict

    Returns:
        value (datetime | date | timedelta | str) :
            Value of entry in ExifDict converted to datetime, date or timedelta
            if applicable
    """
    try:
        converted_value: QtffValue = value
        # `Creation date` in quick time is actually a datetime;
        # but date is enough for me, and inline with exif interface.

        if "date" in key and len(value) >= 19:
            # value = "YYYY:MM:DD HH:MM:SS" --> convert to 'datetime.datetime'
            converted_value = datetime.strptime(value[:19], "%Y:%m:%d %H:%M:%S")
        elif "date" in key:
            # value = "YYYY:MM:DD" --> convert to datetime.date
            converted_value = datetime.strptime(value[:10], "%Y:%m:%d").date()
        else:
            pass
        return converted_value
    except ValueError:
        return value


class Qtff(Filter):
    """Filter by media metadate, mainly for qtff

    The `qtff` filter can be used as a filter as well as a way to get qucik time tags information
    into your actions.

    Examples of metadata and it's fields can be found here:
    https://hachoir.readthedocs.io/en/latest/metadata.html#metadata-examples

    Similar to Exif; Qtff fields which contain "datetime", "date" or "offsettime" in their fieldname
    will have their value converted to 'datetime.datetime', 'datetime.date' and
    'datetime.timedelta' respectivly.
    - `datetime.date` : qtff.Metadata."Creation date", ...

    Returns:
        ``{qtff}``:
            a dict of all the collected exif inforamtion available in the
            file. Typically it consists of the following (if present in the file):
            - `{qtff.Metadata}: a dict of all the collected exif inforamtion available in the file.
    """

    name = "qtff"
    arg_schema = None
    schema_support_instance_without_args = True

    def __init__(self, *required_tags: str, **tag_filters: str) -> None:
        self.args = required_tags  # expected exif keys
        self.kwargs = tag_filters  # exif keys with expected values
    
    def category_dict(self, tags: Mapping[str, str|dict], depth=0) -> QtffDict:
        """
        Converts qtff tags to a nested dict. 
        recursively calls itself to search for subcategories.

        Args:
            tags (Mapping[str, str|dict]): qtff tags
            depth (int): current depth of recursion
        Returns:
            result (QtffDict): nested dict of qtff tags
        """
        MAX_DEPTH = 5 # Max Subcategory depth
        if depth > MAX_DEPTH:
            return tags
        result = collections.defaultdict(dict)  # type: DefaultDict
        
        for key, value in tags.items():
            if value is dict:
                result[key] = self.category_dict(value, depth+1)
            else:
                result[key] = to_datetime(key, value)
        return dict(result)


    # def category_dict(self, tags: Mapping[str, str]) -> QtffDict:
    # 
    #     result = collections.defaultdict(dict)  # type: DefaultDict
    #     for key, value in tags.items():
    #         if " " in key:
    #             category, field = key.split(" ", maxsplit=1)
    #             result[category][field] = to_datetime(field, value)
    #         else:
    #             result[key] = to_datetime(key, value)
    #     return dict(result)

    
    def matches(self, qtffTags: dict) -> bool:
        if not qtffTags:
            return False
        for arg in self.args:
            qLayers = arg.split(".")
            qValue = deep_search(qtffTags, qLayers)
            if not qValue:
                return False
            if not isinstance(qValue, str):
                return False
        return True

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]
        fs_path = args["fs_path"]
        filePath = fs.getsyspath(fs_path)
        parser = createParser(str(filePath))
        if not parser:
            print(f"qtff: Unable to parse file {filePath}")
            
        with parser:
            try:
                qtffTags = extractMetadata(parser).exportDictionary()
            except Exception as err:
                print("Metadata extraction error: %s" % err)
                qtffTags = None
                
        matches = self.matches(qtffTags)

        # fs = args["fs"]
        # fs_path = args["fs_path"]
        # with fs.openbin(fs_path) as f:
        #     exiftags = exifread.process_file(f, details=False)

        # tags = {k.lower(): v.printable for k, v in exiftags.items()}
        # matches = self.matches(tags)
        # exif_result = self.category_dict(tags)

        # return FilterResult(
        #     matches=matches,
        #     updates={self.get_name(): exif_result},
        # )

    def __str__(self) -> str:
        return "QTFF(%s)" % ", ".join("%s=%s" % (k, v) for k, v in self.kwargs.items())
