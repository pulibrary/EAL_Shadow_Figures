from csv import DictReader, reader
from pathlib import Path
from pydantic import BaseModel
from typing import Optional


class ObjectRecord(BaseModel):
    objectno: str
    envelope: str
    oldobjectno: str
    objecttype: str
    description: str
    notes: str
    dimensions: str
    imagenotes: str
    imagename: str
    imagecomments: str
    imageexists: str
    imagetype: str
    imagedesc: str


class Object(BaseModel):
    id: str
    type: str
    description: str
    images: list["Image"] = []


class Image(BaseModel):
    id: str
    filename: str
    objects: list[Object] = []
