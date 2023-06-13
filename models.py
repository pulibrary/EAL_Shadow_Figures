from csv import DictReader, reader
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ObjectType(str, Enum):
    brush_pen = "Brush pen"
    child_body = "Child body"
    chou_head = "Chou head"
    creature = "Creature"
    creature_head = "Creature head"
    dan_head = "Dan head"
    female_body = "Female body"
    figure = "Figure"
    figures = "Figures"
    jing_head = "Jing head"
    male_body = "Male body"
    property_type = "Property"
    sheng_head = "Sheng head"
    text = "Text"


class ObjectRecord(BaseModel):
    objectno: str
    envelope: str
    oldobjectno: str
    objecttype: ObjectType
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


def type_to_label(object_type: ObjectType) -> str:
    label: str = ""
    match object_type:
        case ObjectType.brush_pen:
            label = "Brush Pen"
        case ObjectType.child_body:
            label = "Child Body"
        case ObjectType.chou_head:
            label = "Chou Head"
        case ObjectType.creature:
            label = "Creature"
        case ObjectType.creature_head:
            label = "Creature Head"
        case ObjectType.dan_head:
            label = "Dan Head"
        case ObjectType.female_body:
            label = "Female Body"
        case ObjectType.figure:
            label = "Figure"
        case ObjectType.figures:
            label = "Figures"
        case ObjectType.jing_head:
            label = "Jing Head"
        case ObjectType.male_body:
            label = "Male Body"
        case ObjectType.property_type:
            label = "Property"
        case ObjectType.sheng_head:
            label = "Sheng Head"
        case ObjectType.text:
            label = "Text"

    return label
