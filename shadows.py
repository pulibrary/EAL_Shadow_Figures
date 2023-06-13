"""shadows.py  Classes for generating HTML pages for EAL Shadow Figures collection.

EAL wishes to migrate an old website containing amateur images of
items in their collection and informal metadata about them.  This
module contains classes that read data from a CSV file and use Jinja
templates to generate a static site that provides most of the features
of the original site.
"""

import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from csv import DictReader, reader
from pathlib import Path
from pydantic import ValidationError
from models import ObjectRecord, Object, Image, ObjectType, type_to_label


class ShadowImage:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.id = filename.split('.')[0]
        self.associated_objects: list("ShadowObject") = []

    def __repr__(self) -> str:
        return f"ShadowImage({self.id})"

    # def context(self, context: dict) -> dict:
    #     my_context = {"id": self.id}
    #     my_context["image"] = Path("images") / Path(self.filename)
    #     my_context["thumbnail"] = Path("thumbnails") / Path(self.filename)

    #     return my_context

    def context(self, context: dict) -> dict:
        my_context = {"id": self.id}
        my_context["thumbnail"] = Path("thumbnails") / Path(self.filename)
        if "image_path" in context:
            my_context["path"] = context["image_path"] / Path(self.id).with_suffix(
                ".html"
            )
        else:
            my_context["path"] = Path(self.filename)

        return my_context

    def context_old(self, context: dict) -> dict:
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
        # self.type = clean_type(record.objecttype)
        self.type: ObjectType = record.objecttype
        self.description: str = record.description
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
            "type": type_to_label(self.type),
            "description": self.description,
            "notes": self.notes,
            "dimensions": self.dimensions,
            "images": image_contexts,
        }
        return my_context


class Page:
    pass


class TypePage(Page):
    def __init__(self, object_type: ObjectType, objects: list[ShadowObject]) -> None:
        # super().__init__(object_type)
        self.id: ObjectType = object_type
        self.path: Path = Path(f"{object_type.name}.html")

        self.type: ObjectType = object_type
        self.objects = [obj for obj in objects if obj.type == self.type]

    def __repr__(self) -> str:
        return f"TypePage({self.type.name})"

    def context(self, context: dict = {}) -> dict:
        my_context = {
            "type": type_to_label(self.type),
            "objects": [obj.context(context) for obj in self.objects],
        }
        return my_context

    def render(self, base_path: Path, image_path: Path) -> None:
        environment = Environment(loader=FileSystemLoader("templates"))
        template = environment.get_template("objects.html")
        path = base_path / self.path
        context = self.context(context={"image_path": image_path})

        with open(path, mode="w", encoding="utf-8") as f:
            f.write(template.render(type=context["type"], objects=context["objects"]))


class ImagePage(Page):
    def __init__(self, shadow_image: ShadowImage) -> None:
        self.shadow_image: ShadowImage = shadow_image
        self.path: Path = Path(f"{shadow_image.id}.html")

    def context(self, context: dict = {}) -> dict:
        descriptions = [
            object.description for object in self.shadow_image.associated_objects
        ]

        if "image_path" in context:
            image = context["image_path"] / Path(self.shadow_image.filename)
        else:
            image = Path(self.shadow_image.filename)
        my_context = {
            "image": str(image),
            "descriptions": descriptions,
        }
        return my_context

    def render(self, base_path: Path, image_page_path: Path, image_path: Path) -> None:
        environment = Environment(loader=FileSystemLoader("templates"))
        template = environment.get_template("images.html")
        path = base_path / image_page_path / self.path
        context = self.context(context={"image_path": image_path})
        with open(path, mode="w", encoding="utf-8") as f:
            f.write(
                template.render(
                    image=context["image"], descriptions=context["descriptions"]
                )
            )


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
            reader: DictReader = DictReader(f, fieldnames=None)
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
            types: set[ObjectType] = {object.type for object in self.shadow_objects}
            for type in types:
                self.type_pages.append(TypePage(type, self.shadow_objects))
        return self._type_pages

    @property
    def image_pages(self) -> list[ImagePage]:
        if self._image_pages is None:
            self._image_pages = []
            for index, shadow_image in self.image_index.items():
                self._image_pages.append(ImagePage(shadow_image))
        return self._image_pages
