import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from csv import DictReader, reader
from pathlib import Path
from models import ObjectRecord, Object, Image


def clean_type(type_string) -> str:
    return type_string.replace(" ", "_")


class ShadowImage:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.id = filename.split('.')[0]
        self.associated_objects = []

    def __repr__(self) -> str:
        return f"ShadowImage({self.id})"

    def context(self, context: dict) -> dict:
        my_context = {"id": self.id}
        if "image_path" in context:
            my_context["path"] = context["image_path"] / Path(self.id).with_suffix(
                ".html"
            )
            my_context["thumbnail"] = Path("thumbnails") / Path(self.filename)
        else:
            my_context["path"] = Path(self.filename)
        return my_context


class ShadowObject:
    def __init__(self, record: ObjectRecord) -> None:
        self.id = record.objectno
        self.type = clean_type(record.objecttype)
        self.description = record.description
        self.notes = record.notes
        self.dimensions = record.dimensions
        self.associated_images = None
        if record.imagename:
            self.associated_images = [
                ShadowImage(fname) for fname in record.imagename.split('|')
            ]

    def __repr__(self) -> str:
        return f"ShadowObject({self.id})"

    def context(self, context: dict = {}) -> dict:
        image_contexts = [image.context(context) for image in self.associated_images]
        my_context = {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "notes": self.notes,
            "dimensions": self.dimensions,
            "images": image_contexts,
        }
        return my_context


class Page:
    def __init__(self, id: str) -> None:
        self.id = id
        self.path: Path = Path(f"{id}.html")


class TypePage(Page):
    def __init__(self, type_id: str, objects: list[ShadowObject]) -> None:
        super().__init__(type_id)
        self.type = type_id
        self.objects = [obj for obj in objects if obj.type == self.type]

    def __repr__(self) -> str:
        return f"TypePage({self.type})"

    def context(self, context: dict = {}) -> dict:
        my_context = {
            "type": self.type,
            "objects": [obj.context(context) for obj in self.objects],
        }
        return my_context

    def render(self, base_path: Path, image_path: Path) -> None:
        environment = Environment(loader=FileSystemLoader("templates"))
        template = environment.get_template("objects.html")
        path = base_path / self.path
        context = self.context(context={"image_path": image_path})

        with open(path, mode="w", encoding="utf-8") as f:
            f.write(template.render(type=self.type, objects=context["objects"]))


class ImagePage(Page):
    def __init__(self, shadow_image: ShadowImage) -> None:
        super().__init__(self)
        self.shadow_image: ShadowImage = shadow_image


def all_types(obj_list: list[ShadowObject]) -> set:
    return {object.type for object in obj_list}


class ShadowFigureSiteGenerator:
    def __init__(self, source_path: Path) -> None:
        self.shadow_objects = None
        self.shadow_images = None
        self._image_index: Optional[dict] = None
        self._type_pages: Optional[list[TypePage]] = None
        self._image_pages: Optional[list[ImagePage]] = None
        self.read(source_path)

    def read(self, file_path: Path) -> None:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = DictReader(f)
            records = [ObjectRecord(**row) for row in reader]
        self.shadow_objects = [ShadowObject(record) for record in records]

    @property
    def image_index(self) -> dict:
        if self._image_index is None:
            self._image_index = {}
            for object in self.shadow_objects:
                for shadow_image in object.associated_images:
                    if shadow_image.id not in self._image_index:
                        indexed_image = ShadowImage(shadow_image.filename)
                        self._image_index[shadow_image.id] = indexed_image
                    else:
                        indexed_image = self._image_index[shadow_image.id]

                    indexed_image.associated_objects.append(object)
        return self._image_index

    @property
    def type_pages(self) -> list[TypePage]:
        if self._type_pages is None:
            self._type_pages = []
            for type in all_types(self.shadow_objects):
                self.type_pages.append(TypePage(type, self.shadow_objects))
        return self._type_pages

    @property
    def image_pages(self) -> list[ImagePage]:
        if self._image_pages is None:
            self._image_pages = []
            for index, shadow_image in self.image_index.items():
                self._image_pages.append(ImagePage(shadow_image))
        return self._image_pages
