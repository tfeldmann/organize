from typing import Union, Iterable, Literal, Dict, List, Annotated
from pydantic import BaseModel as PydanticBaseModel, validator, root_validator, Field


class BaseModel(PydanticBaseModel):
    class Config:
        extra = "forbid"


# print(Filter.parse_obj("name"))


class BaseFilter(BaseModel):
    filter_type: str = Field(repr=False)
    filter_exclude: bool = False


class Name(BaseFilter):
    filter_type: Literal["name"]

    match: str = "*"
    startswith: Union[str, List[str]] = None
    contains: Union[str, List[str]] = None
    endswith: Union[str, List[str]] = None
    case_sensitive: bool = True


class Extension(BaseFilter):
    filter_type: Literal["extension", "ext"]
    meows: int


class Exif(BaseFilter):
    filter_type: Literal["exif"]
    barks: float = 0


FilterType = Annotated[Union[Name, Extension, Exif], Field(discriminator="filter_type")]


class Rule(BaseModel):
    filters: List[FilterType]

    @validator("filters", pre=True, each_item=True)
    def filter_rewriter(cls, value):
        key = list(value.keys())[0]
        val = list(value.values())[0]
        return {"filter_type": key, **val}


x = Rule.parse_obj({"filters": [{"exif": {}}, {"name": {}}]})
print(x)

# print(Filter(filter={"filter_type": "name", "match": "everything"}))


# from pydantic import BaseModel, Field


# class NameFilterSchema(BaseModel):
#     match: str = "*"
#     startswith: Union[str, List[str]] = None
#     contains: Union[str, List[str]] = None
#     endswith: Union[str, List[str]] = None
#     case_sensitive: bool = True

#     class Config:
#         allow_population_by_field_name = True
#         extra = "forbid"


# class NameFilter(NameFilterSchema):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def yeah(self):
#         print("yeah!" + self.match.upper())


# x = NameFilter(contains="asd")
# x.yeah()
# print(x)


# # class Filter(BaseModel):
# #     __root__: Union[
# #         Literal["name"], Literal["not name"], Dict[Literal["name"], NameFilter]
# #     ]

# #     @validator("__root__", pre=True)
# #     def root_validator(cls, value):
# #         if isinstance(value, str):
# #             return {value: dict()}
# #         return value
