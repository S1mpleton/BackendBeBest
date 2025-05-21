import datetime
from math import ceil

from fastapi import UploadFile, HTTPException, status

from dataBase import ModuleModel
from routers.dependencies import (
    FeaturedImageSchema, check_image_format, PaginationSchema, MODULE_TYPE, COURSE_TYPE
)
from routers.modules.schemes import (
    GetModuleSchema, CreateModuleSchema, PaginationModuleSchema, UpdateModuleSchema, GetPaginationModuleSchema
)

from ..courses import repository as repository_courses
from ..images import repository as repository_images
from .db_requests import ModuleRequestsDB



class ModulRepository:
    @classmethod
    def get_image_schema_by_id(cls, module_id: int) -> FeaturedImageSchema:
        return repository_images.ImagesRepository.get_image_schema(module_id, MODULE_TYPE)

    @classmethod
    def remove_image_by_id(cls, module_id: int):
        repository_images.ImagesRepository.delete_image(module_id, MODULE_TYPE)

    @classmethod
    def save_images(cls, module_id: int, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            model_id=module_id,
            model_type=MODULE_TYPE,
            image_data=image_data.file
        )




    @classmethod
    def get_by_id(cls, module_id: int) -> GetModuleSchema:
        select = ModuleRequestsDB()
        select.sample_by_id(module_id)
        modul = select.get_first_modul()

        if not modul:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Modul not found"
            )

        featured_image = cls.get_image_schema_by_id(module_id)


        modul.__data__["featuredImage"] = featured_image
        modul.__data__[f"{COURSE_TYPE}_id"] = modul.__data__.pop(COURSE_TYPE)

        return GetModuleSchema(**modul.__data__)

    @classmethod
    def get_all_by_course_id(cls, course_id: int) -> list[GetModuleSchema]:
        select = ModuleRequestsDB()
        select.sample_by_course_id(course_id)

        data_module = []
        for module in select.get_iterator_modul():
            data_module.append(cls.get_by_id(module.id))

        return data_module

    @classmethod
    def get_by_page(cls, course_id: int, pagination: GetPaginationModuleSchema) -> PaginationModuleSchema:
        select = ModuleRequestsDB()
        select.sample_by_course_id(course_id)
        select.order_by_description(pagination.description)

        total_elements = select.get_count()

        select.sample_by_pagination(pagination.number_page, pagination.quantity_on_page)

        modules_data = []
        for module in select.get_iterator_modul():
            module_schema = cls.get_by_id(module.id)
            modules_data.append(module_schema)

        return PaginationModuleSchema(
            data=modules_data,
            pagination=PaginationSchema(
                current_page=pagination.number_page,
                total_pages=ceil(total_elements / pagination.quantity_on_page),
                total_elements=total_elements
            )
        )

    @classmethod
    def create(cls, data: CreateModuleSchema, creator_id: int) -> GetModuleSchema:
        course = repository_courses.CourseRepository.get_by_id(data.course_id)
        if not course in repository_courses.CourseRepository.get_by_creator_id(creator_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="no access"
            )

        check_image_format(data.image.content_type)


        module = ModuleModel.create(
            course_id=course.id,
            title=data.title,
            description=data.description,
            video_URL=data.video_URL,
            created_at=datetime.date.today()
        )

        cls.save_images(module.id, data.image)
        return cls.get_by_id(module.id)

    @classmethod
    def delete_by_id(cls, module_id):
        request = ModuleRequestsDB()
        request.sample_by_id(module_id)

        cls.remove_image_by_id(request.get_first_modul().id)
        request.delete()

    @classmethod
    def update_module(cls, data: UpdateModuleSchema) -> GetModuleSchema:
        cls.get_by_id(data.id)

        select = ModuleRequestsDB()
        select.sample_by_id(data.id)

        if data.image:
            check_image_format(data.image.content_type)
            cls.remove_image_by_id(data.id)
            cls.save_images(data.id, data.image)

        if data.title:
            select.update_title(data.title)

        if data.description:
            select.update_description(data.description)

        if data.video_url:
            select.update_video_url(str(data.video_url))


        select.save()

        return cls.get_by_id(data.id)


