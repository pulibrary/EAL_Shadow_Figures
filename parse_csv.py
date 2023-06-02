from csv import DictReader, reader
from pathlib import Path
from models import ObjectRecord

data_path = Path('shadowfigures_test.csv')

with open(data_path, mode='r', encoding='utf-8') as f:
    reader = DictReader(f)
    records = [ObjectRecord(**row) for row in reader]

image_index = {}
object_index = {}
type_index = {}

for record in records:
    images = record.imagename.split('|')
    for image in images:
        if image in image_index:
            image_index[image].append(record.objectno)
        else:
            image_index[image] = [record.objectno]

    metadata = {
        "objectno": record.objectno,
        "objecttype": record.objecttype,
        "images": images,
        "description": record.description,
    }

    if record.notes:
        metadata["notes"] = record.notes

    if record.dimensions:
        metadata["dimensions"] = record.dimensions

    object_index[record.objectno] = metadata

    if record.objecttype not in type_index:
        type_index[record.objecttype] = []

    type_index[record.objecttype].append(record.objectno)
