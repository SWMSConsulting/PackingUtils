from pydantic import BaseModel, Field
from typing import List


class ColliDetailsModel(BaseModel):
    width: int = Field(description="Width of the bin", gt=0)
    length: int = Field(description="Length of the bin", gt=0)
    height: int = Field(description="Height of the bin", gt=0)


class PackageModel(BaseModel):
    width: int = Field(description="Width of the package", gt=0)
    length: int = Field(description="Length of the package", gt=0)
    height: int = Field(description="Height of the package", gt=0)

    x: int = Field(description="X position of the package", ge=0)
    y: int = Field(description="Y position of the package", ge=0)
    z: int = Field(description="Z position of the package", ge=0)


class BinImageRequestModel(BaseModel):
    packages: List[PackageModel]
    colli_details: ColliDetailsModel
