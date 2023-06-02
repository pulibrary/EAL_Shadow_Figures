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

    # if record.objecttype not in type_index:
    #     type_index[record.objecttype] = []

    # type_index[record.objecttype].append(record.objectno)

environment = Environment(loader=FileSystemLoader("templates"))


test_objects = [
    {
        'objectno': '1',
        'objecttype': 'Dan head',
        'images': ['DSCN4746.JPG'],
        'description': 'Dan head. Wu. Dan. Woman warrior. Black, open cut face, small earring. Large red central pompom; blue tone diadem, ezi 額子, with red pompom at ear; red tassel hangs in front of neck. Black hair bound in figure eight by twin meifa 美髮 sticks. Filigree cut ornament hangs below.',
        'dimensions': 'H:',
    },
    {
        'objectno': '2',
        'objecttype': 'Dan head',
        'images': ['DSCN4746.JPG'],
        'description': 'Dan head. Wu. Dan. Woman warrior. Black, open cut face, small earring. Large red central pompom; blue tone diadem, ezi 額子, with red pompom at ear; red tassel hangs in front of neck. Black hair bound in figure eight by twin meifa 美髮 sticks. Filigree cut ornament hangs below.',
        'dimensions': 'H:',
    },
]

template = environment.get_template("objects.html")

base_path: Path = Path("site")
for obj_type in types:
    path: Path = base_path / Path(obj_type.replace(" ", "_"))
    context = [obj for obj in object_index if obj['objecttype'] == obj_type]
    with open(path.with_suffix(".html"), mode="w", encoding="utf-8") as f:
        f.write(template.render(objects=context, type=obj_type))

# context = {"objects": object_index}

# content = template.render(context)


# with open("/tmp/thunk.html", mode="w", encoding="utf-8") as f:
#     f.write(content)
