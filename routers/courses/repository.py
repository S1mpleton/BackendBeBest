import datetime
import os
from math import ceil

from fastapi import HTTPException, status, UploadFile
from peewee import ModelSelect, fn, SQL

from dataBase import CoursesModel, ImageCourseModel, ImageFormatModel, ModuleModel
from routers.courses.schemes import GetCourseSchema, CreateCourseSchema, PaginationCourseSchema, UpdateCourseSchema
from routers.dependencies import get_image_path, FeaturedImageSchema, get_featured_image, check_image_format, \
    PaginationSchema, COURSE_TYPE

from ..modules import repository as repository_modules
from ..users import repository as repository_users
from ..images import repository as repository_images



class CourseRepository:
    @classmethod
    def get_model_by_id(cls, id_course) -> CoursesModel:
        try:
            return CoursesModel.get_by_id(id_course)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not fount")

    @classmethod
    def get_image_request_by_model(cls, course: CoursesModel) -> ModelSelect:
        images = (
            ImageCourseModel.select(
                ImageCourseModel,
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(ImageCourseModel.object == course)
        )

        return images

    @classmethod
    def get_image_by_model(cls, course: CoursesModel) -> FeaturedImageSchema:
        images = cls.get_image_request_by_model(course)

        return get_featured_image(images)

    @classmethod
    def remove_image_by_model(cls, course: CoursesModel):
        images = cls.get_image_request_by_model(course)

        for image in images:
            file_path = get_image_path(
                id_model=course.id,
                name_model="course",
                format_name=image.format.format_name
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def save_images(cls, course: CoursesModel, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            id_model=course.id,
            object_type=COURSE_TYPE,
            image_data=image_data
        )



    @classmethod
    def get_by_id(cls, id_course: int) -> GetCourseSchema:
        course = cls.get_model_by_id(id_course)

        featured_image = CourseRepository.get_image_by_model(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)

    @classmethod
    def create(cls, data: CreateCourseSchema) -> GetCourseSchema:
        check_image_format(data.image.content_type)
        user = repository_users.UserRepository.get_model_by_id(data.creator_id)

        course = CoursesModel.create(
            creator_id=user,
            title=data.title,
            description=data.description,
            created_at=datetime.date.today()
        )

        cls.save_images(course, data.image)

        featured_image = cls.get_image_by_model(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)

    @classmethod
    def get_by_page(cls, number_page: int, quantity_on_page: int, description: str) -> PaginationCourseSchema:
        total_elements = ceil(CoursesModel.select(CoursesModel.id).count())

        courses_data = []
        courses = (
            CoursesModel
            .select(
                CoursesModel,
                fn.ifNotNull(
                    bool(description), fn.comparison(CoursesModel.title + CoursesModel.description, description)
                ).alias('discount')
            )
            .limit(quantity_on_page).offset((number_page - 1) * quantity_on_page)
            .order_by(SQL("discount").desc())
        )

        for course in courses:
            featured_image = CourseRepository.get_image_by_model(course)

            course.__data__["featuredImage"] = featured_image
            course.__data__["creator_id"] = course.__data__.pop("creator")

            courses_data.append(GetCourseSchema(**course.__data__))

        return PaginationCourseSchema(
            data=courses_data,
            pagination=PaginationSchema(
                current_page=number_page,
                total_pages=ceil(total_elements / quantity_on_page),
                total_elements=total_elements
            )
        )

    @classmethod
    def get_by_creator_id(cls, id_user) -> list[GetCourseSchema]:
        course_data = []
        user = repository_users.UserRepository.get_model_by_id(id_user)

        for course in CoursesModel.select().where(CoursesModel.creator == user):
            featured_image = cls.get_image_by_model(course)

            course.__data__["featuredImage"] = featured_image
            course.__data__["creator_id"] = course.__data__.pop("creator")

            course_data.append(GetCourseSchema(**course.__data__))

        return course_data

    @classmethod
    def delete_by_id(cls, id_course):
        course = CoursesModel.get_by_id(id_course)

        modules = ModuleModel.select().where(ModuleModel.course == course)
        for module in modules:
            repository_modules.ModulRepository.delete_by_id(module.id)

        CourseRepository.remove_image_by_model(course)

        course.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_course(cls, data: UpdateCourseSchema) -> GetCourseSchema:
        course = cls.get_model_by_id(data.id)
        check_image_format(data.image.content_type)

        if data.title:
            course.title = data.title

        if data.description:
            course.description = data.description

        if data.image:
            cls.remove_image_by_model(course)
            cls.save_images(course, data.image)

        course.save()

        featured_image = cls.get_image_by_model(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)
