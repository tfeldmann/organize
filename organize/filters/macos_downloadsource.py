import sys
import json
from typing import ClassVar, List

from pydantic import Field, field_validator
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import glob_match


def list_download_urls(path) -> List[str]:
    import osxmetadata
    urls = json.loads(osxmetadata.OSXMetaData(path).to_json())["kMDItemWhereFroms"]
    return urls


def convert_to_list(v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def match_urls(filter_urls, file_urls) -> bool:
    if file_urls is None:
        return False
    if not filter_urls:
        return True
    urls = [url.replace("blob:", "") for url in file_urls]
    for url in urls:
        if any(glob_match(filter_url, url) for filter_url in filter_urls):
            return True
    return False


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MacOSDownloadSource:
    """Filter files using the "kMDItemWhereFroms" metadata present in macOS files. 
    This allows us to check where the file originated from (if such metadata exists)
 
    Attributes:
        urls (list(str) or str):
            The source URLs to filter by
    """

    urls: List[str] = Field(default_factory=list)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="macos_downloadsource",
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        if sys.platform != "darwin":
            raise EnvironmentError("The macos_downloadsource filter is only available on macOS")

    @field_validator("urls", mode="before")
    def normalise_urls(cls, v):
        as_list = convert_to_list(v)
        return set(list(as_list))

    def pipeline(self, res: Resource, output: Output) -> bool:
        if res.is_dir():
            raise ValueError("Directories are not supported")

        file_urls = list_download_urls(res.path)

        res.vars[self.filter_config.name] = file_urls
        return match_urls(filter_urls=self.urls, file_urls=file_urls)
