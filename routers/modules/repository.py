import datetime
import os
from math import ceil

from PIL import Image
from fastapi import HTTPException, status, UploadFile
from peewee import ModelSelect, SQL, fn
from pydantic import HttpUrl

from dataBase import ModuleModel, ImageModuleModel, ImageFormatModel
from routers.dependencies import FeaturedImageSchema, check_image_format, PaginationSchema, get_image_path, \
    get_featured_image, MODULE_TYPE
from routers.modules.schemes import GetModuleSchema, CreateModuleSchema, PaginationModuleSchema, UpdateModuleSchema

from ..courses import repository as repository_courses
from ..images import repository as repository_images



class ModulRepository:
    @classmethod
    def get_module_by_id(cls, id_module) -> ModuleModel:
        try:
            return ModuleModel.get_by_id(id_module)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not fount")

    @classmethod
    def get_image_request_by_modul(cls, module: ModuleModel) -> ModelSelect:
        images = (
            ImageModuleModel.select(
                ImageModuleModel,
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(ImageModuleModel.object == module)
        )

        return images

    @classmethod
    def get_image_by_module(cls, module: ModuleModel) -> FeaturedImageSchema:
        images = cls.get_image_request_by_modul(module)

        return get_featured_image(images)

    @classmethod
    def remove_image_by_module(cls, module: ModuleModel):
        images = cls.get_image_request_by_modul(module)

        for image in images:
            file_path = get_image_path(
                id_model=module.id,
                name_model="module",
                format_name=image.format.format_name
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def save_images(cls, module: ModuleModel, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            id_model=module.id,
            object_type=MODULE_TYPE,
            image_data=image_data
        )



    @classmethod
    def get_by_id(cls, id_module: int) -> GetModuleSchema:
        module = cls.get_module_by_id(id_module)

        featured_image = cls.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)

    @classmethod
    def get_by_page(
            cls, id_course: int,
            number_page: int,
            quantity_on_page: int,
            description: str
    ) -> PaginationModuleSchema:

        total_elements = ceil(
            ModuleModel
            .select(ModuleModel.id)
            .where(ModuleModel.course == id_course)
            .count()
        )

        modules_data = []
        modules = (
            ModuleModel
            .select(
                ModuleModel,
                fn.ifNotNull(
                    bool(description), fn.comparison(ModuleModel.title + ModuleModel.description, description)
                ).alias('discount')
            )
            .where(ModuleModel.course == id_course)
            .limit(quantity_on_page).offset((number_page - 1) * quantity_on_page)
            .order_by(SQL("discount").desc())
        )


        for module in modules:
            featured_image = cls.get_image_by_module(module)

            module.__data__["featuredImage"] = featured_image
            module.__data__["course_id"] = module.__data__.pop("course")

            modules_data.append(GetModuleSchema(**module.__data__))

        return PaginationModuleSchema(
            data=modules_data,
            pagination=PaginationSchema(
                current_page=number_page,
                total_pages=ceil(total_elements / quantity_on_page),
                total_elements=total_elements
            )
        )

    @classmethod
    def create(cls, data: CreateModuleSchema) -> GetModuleSchema:
        check_image_format(data.image.content_type)
        course = repository_courses.CourseRepository.get_model_by_id(data.course_id)

        module = ModuleModel.create(
            course_id=course,
            title=data.title,
            description=data.description,
            video_URL=data.video_URL,
            created_at=datetime.date.today()
        )

        cls.save_images(module, data.image)

        featured_image = cls.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)

    @classmethod
    def delete_by_id(cls, id_module):
        module = cls.get_module_by_id(id_module)

        cls.remove_image_by_module(module)

        module.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_module(cls, data: UpdateModuleSchema) -> GetModuleSchema:
        module = cls.get_module_by_id(data.id)
        check_image_format(data.image.content_type)

        if data.title:
            module.title = data.title

        if data.description:
            module.description = data.description

        if data.video_url:
            module.video_URL = data.video_url

        if data.image:
            cls.remove_image_by_module(module)
            cls.save_images(module, data.image)

        module.save()

        featured_image = cls.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)



