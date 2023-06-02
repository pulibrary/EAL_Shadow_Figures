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
