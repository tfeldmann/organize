from typing import Set
from pathlib import Path
from pydantic import BaseModel, Field


class Resource(BaseModel):
    path: Path
    walker_skip_files: Set[Path] = Field(default_factory=set)
