import os
from jinja2 import Environment, FileSystemLoader
from csv import DictReader, reader
from pathlib import Path
from models import ObjectRecord, Object, Image
import shadows

data_path = Path('shadowfigures.csv')
site_dir = Path("site")
image_page_dir = site_dir / Path("image_pages")


image_index = {}
for record in records:
    for filename in record.imagename.split('|'):
        image = Image(id=filename.split(".")[0], filename=filename)
        image_index[image.id] = image


types: dict = set()
object_list: list = []

for record in records:
    types.add(record.objecttype)

    object = Object(
        id=record.objectno, type=record.objecttype, description=record.description
    )

    for filename in record.imagename.split('|'):
        image_id = filename.split(".")[0]
        image: Image = image_index[image_id]
        object.images.append(image.filename)
        image_index[image.id].objects.append(object.id)
    object_list.append(object)


object_type_pages = []
for obj_type in types:
    page: str = f"{obj_type.replace(' ', '_')}.html"
    object_type_pages.append({"label": obj_type, "link": page})

environment = Environment(loader=FileSystemLoader("templates"))


template = environment.get_template("objects.html")

for obj_type in types:
    objects = [obj for obj in object_list if obj.type == obj_type]
    context = [obj.dict() for obj in objects]

    path: Path = site_dir / Path(obj_type.replace(" ", "_")).with_suffix(".html")
    with open(path, mode="w", encoding="utf-8") as f:
        f.write(template.render(objects=context, nav=object_type_pages, type=obj_type))


base_path: Path = Path("site/image_pages")

for img, oblist in image_index.items():
    objects = list(filter(lambda x: x.id in oblist, object_list))
    descriptions = [o["description"] for o in objects]

    page: Path = image_page_dir / Path(img.split(".")[0]).with_suffix(".html")
    with open(page, mode="w", encoding="utf-8") as f:
        f.write(template.render(image=img, descriptions=descriptions))
