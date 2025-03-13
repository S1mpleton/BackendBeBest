import datetime
import os
from math import ceil

from PIL import Image
from fastapi import UploadFile
from peewee import fn, SQL

from dataBase import CoursesModel, ImageFormatModel, ImageCourseModel
from routers.schemes import CreateCourseSchema, FeaturedImageSchema, GetCourseSchema, PaginationCourseSchema, \
    PaginationSchema


class CourseRepository:
    @classmethod
    def get_all(cls):
        pass

    @classmethod
    def remove_image_by_course(cls, course: CoursesModel):
        images = ImageCourseModel.select().where(ImageCourseModel.course == course)

        for image in images:
            image.delete_instance(recursive=True, delete_nullable=True)

        for form in ImageFormatModel.select():
            file_name = f"{course.id}-course-{form.format_name}-{course.created_at}.jpg"
            file_path = os.path.join("resources", "images", file_name)

            os.remove(file_path)

    @classmethod
    def get_image_by_course(cls, course: CoursesModel) -> FeaturedImageSchema:
        feature = (ImageCourseModel.select(ImageCourseModel, ImageFormatModel)
                   .join(ImageFormatModel)
                   .where(ImageCourseModel.course == course))

        images = {}
        for f in feature:
            images[f.format.format_name] = f.image_path

        return FeaturedImageSchema(**images)

    @classmethod
    def save_images(cls, course: CoursesModel, image_data: UploadFile):
        for form in ImageFormatModel.select():

            file_name = f"{course.id}-course-{form.format_name}-{course.created_at}.jpg"
            file_path = os.path.join("resources", "images", file_name)

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageCourseModel.create(
                format=form.id,
                image_path=file_name,
                course_id=course
            )




    @classmethod
    def get_by_id(cls, id_course: int) -> GetCourseSchema:
        course = CoursesModel.get_by_id(id_course)

        featured_image = CourseRepository.get_image_by_course(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)

    @classmethod
    def create(cls, data: CreateCourseSchema) -> GetCourseSchema:
        course = CoursesModel.create(
            creator_id=data.creator_id,
            title=data.title,
            description=data.description,
            created_at=datetime.date.today()
        )

        CourseRepository.save_images(course, data.image)

        featured_image = CourseRepository.get_image_by_course(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)

    @classmethod
    def get_by_page(cls, number_page: int, quantity_on_page: int, description: str) -> PaginationCourseSchema:
        total_elements = int(ceil(CoursesModel.select(CoursesModel.id).count()))

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
            featured_image = CourseRepository.get_image_by_course(course)

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

        for course in CoursesModel.select().where(CoursesModel.creator == id_user):
            CourseRepository.get_image_by_course(course)

            featured_image = CourseRepository.get_image_by_course(course)

            course.__data__["featuredImage"] = featured_image
            course.__data__["creator_id"] = course.__data__.pop("creator")

            course_data.append(GetCourseSchema(**course.__data__))

        return course_data

    @classmethod
    def delete_by_id(cls, id_course):
        course = CoursesModel.get_by_id(id_course)

        CourseRepository.remove_image_by_course(course)

        course.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_course(cls, id_course: int, title: str, description: str, image: UploadFile) -> GetCourseSchema:
        course = CoursesModel.get_by_id(id_course)

        if title:
            course.title = title

        if description:
            course.description = description

        if image:
            CourseRepository.remove_image_by_course(course)
            CourseRepository.save_images(course, image)

        course.save()

        featured_image = CourseRepository.get_image_by_course(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)
