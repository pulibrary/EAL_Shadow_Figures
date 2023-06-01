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


data_path = Path('shadowfigures.csv')

with open(data_path, mode='r', encoding='utf-8') as f:
    reader = DictReader(f)
    records = [ObjectRecord(**row) for row in reader]

image_index = {}
object_index = {}

for record in records:
    images = record.imagename.split('|')
    for image in images:
        if image in image_index:
            image_index[image].append(record.objectno)
        else:
            image_index[image] = [record.objectno]

    if record.objecttype not in object_index:
        object_index[record.objecttype] = {}

    object_index[record.objecttype][record.objectno] = {
        "images": images,
        "description": record.description,
    }

    if record.notes:
        object_index[record.objecttype][record.objectno]["notes"] = record.notes

    if record.dimensions:
        object_index[record.objecttype][record.objectno][
            "dimensions"
        ] = record.dimensions

    # metadata = {
    #     "envelope": record.envelope,
    #     "oldobjno": record.oldobjectno,
    #     "objecttype": record.objecttype,
    #     "description": record.description,
    #     "notes": record.notes,
    #     "dimensions": record.dimensions,
    # }
    # object_index[record.objectno] = record


def object_desc(objid):
    obj_rec = object_index[objid]
    desc = {
        "type": obj_rec.objecttype,
        "description": obj_rec.description,
        "notes": obj_rec.notes,
    }
    return desc
