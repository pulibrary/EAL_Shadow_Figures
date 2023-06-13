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
        self.filename: str = filename
        self.id: str = filename.split('.')[0]
        self.associated_objects: list("ShadowObject") = []

    def __repr__(self) -> str:
        return f"ShadowImage({self.id})"

    @property
    def image_url(self) -> str:
        return f"images/{self.filename}"

    @property
    def thumbnail_url(self) -> str:
        return f"thumbnails/{self.filename}"

    @property
    def page_url(self) -> str:
        return f"{self.id}.html"

    def context(self, context: dict) -> dict:
        my_context = {
            "id": self.id,
            "thumbnail": self.thumbnail_url,
            "url": self.image_url,
            "page_url": self.page_url,
        }
        return my_context


class ShadowObject:
    def __init__(self, record: ObjectRecord) -> None:
        self.id = record.objectno
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
            "object_class": type_to_label(self.type),
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
        self.id: ObjectType = object_type
        self.filename: str = f"{object_type.name}.html"

        self.type: ObjectType = object_type
        self.objects = [obj for obj in objects if obj.type == self.type]

    def __repr__(self) -> str:
        return f"TypePage({self.type.name})"

    def url(self, base_url: str | None = None) -> str:
        if base_url:
            return f"{base_url}/{self.filename}"
        else:
            return self.filename

    def context(self, context: dict = {}) -> dict:
        my_context = {
            "object_class": type_to_label(self.type),
            "objects": [obj.context(context) for obj in self.objects],
        }
        return my_context

    def render(self, base_path: Path) -> None:
        environment = Environment(loader=FileSystemLoader("templates"))
        template = environment.get_template("objects.html")
        with open(self.url(base_path), mode="w", encoding="utf-8") as f:
            f.write(template.render(self.context()))


class ImagePage(Page):
    def __init__(self, shadow_image: ShadowImage) -> None:
        self.shadow_image: ShadowImage = shadow_image
        self.filename: str = f"{shadow_image.id}.html"

    @property
    def image_url(self) -> str:
        return self.shadow_image.image_url

    def context(self, context: dict = {}) -> dict:
        descriptions = [
            object.description for object in self.shadow_image.associated_objects
        ]

        my_context = {
            "image_url": self.image_url,
            "descriptions": descriptions,
        }
        return my_context

    def render(self, base_path: Path) -> None:
        environment = Environment(loader=FileSystemLoader("templates"))
        template = environment.get_template("images.html")
        path = base_path / self.filename
        with open(path, mode="w", encoding="utf-8") as f:
            f.write(template.render(self.context()))


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

    def generate(self, site_dir: str) -> None:
        for page in self.type_pages:
            page.render(site_dir)

        for page in self.image_pages:
            page.render(site_dir)

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
