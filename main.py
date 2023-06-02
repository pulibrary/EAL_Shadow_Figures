from jinja2 import Environment, FileSystemLoader
from csv import DictReader, reader
from pathlib import Path
from models import ObjectRecord

data_path = Path('shadowfigures.csv')

with open(data_path, mode='r', encoding='utf-8') as f:
    reader = DictReader(f)
    records = [ObjectRecord(**row) for row in reader]

image_index = {}
object_index = []
# type_index = {}
types = set()

for record in records:
    types.add(record.objecttype)
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

    object_index.append(metadata)

environment = Environment(loader=FileSystemLoader("templates"))


template = environment.get_template("objects.html")

base_path: Path = Path("site")
paths = []
for obj_type in types:
    page: str = f"{obj_type.replace(' ', '_')}.html"
    paths.append({"label": obj_type, "link": page})

for obj_type in types:
    path: Path = base_path / Path(obj_type.replace(" ", "_"))
    context = [obj for obj in object_index if obj['objecttype'] == obj_type]
    with open(path.with_suffix(".html"), mode="w", encoding="utf-8") as f:
        f.write(template.render(objects=context, nav=paths, type=obj_type))
