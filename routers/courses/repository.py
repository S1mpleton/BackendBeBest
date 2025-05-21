import datetime
from math import ceil

from fastapi import UploadFile, HTTPException, status

from dataBase import CoursesModel
from routers.courses.schemes import (
    GetCourseSchema, CreateCourseSchema, PaginationCourseSchema, UpdateCourseSchema, GetPaginationCourseSchema
)
from routers.dependencies import FeaturedImageSchema, check_image_format, PaginationSchema, COURSE_TYPE

from ..modules import repository as repository_modules
from ..users import repository as repository_users
from ..images import repository as repository_images
from .db_requests import CourseRequestsDB




class CourseRepository:
    @classmethod
    def get_image_schema_by_id(cls, course_id: int) -> FeaturedImageSchema:
        return repository_images.ImagesRepository.get_image_schema(course_id, COURSE_TYPE)

    @classmethod
    def remove_image_by_id(cls, course_id: int):
        repository_images.ImagesRepository.delete_image(course_id, COURSE_TYPE)

    @classmethod
    def save_images(cls, course_id: int, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            model_id=course_id,
            model_type=COURSE_TYPE,
            image_data=image_data.file
        )




    @classmethod
    def get_by_id(cls, course_id: int) -> GetCourseSchema:
        select = CourseRequestsDB()
        select.sample_by_id(course_id)
        course = select.get_first_course()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course not found"
            )

        featured_image = cls.get_image_schema_by_id(course_id)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")
        return GetCourseSchema(**course.__data__)

    @classmethod
    def get_all(cls) -> list[GetCourseSchema]:
        data = []
        select = CourseRequestsDB()
        for course in select.get_iterator_course():
            data.append(cls.get_by_id(course.id))

        return data

    @classmethod
    def get_by_page(cls, pagination: GetPaginationCourseSchema) -> PaginationCourseSchema:
        select = CourseRequestsDB()
        if pagination.category:
            select.sample_by_categories(pagination.category)

        select.order_by_description(pagination.description)
        total_elements = select.get_count()
        select.sample_by_pagination(pagination.number_page, pagination.quantity_on_page)

        courses_data = []
        for course in select.get_iterator_course():
            courses_data.append(cls.get_by_id(course.id))

        return PaginationCourseSchema(
            data=courses_data,
            pagination=PaginationSchema(
                current_page=pagination.number_page,
                total_pages=ceil(total_elements / pagination.quantity_on_page),
                total_elements=total_elements
            )
        )

    @classmethod
    def get_by_creator_id(cls, user_id) -> list[GetCourseSchema]:
        user = repository_users.UserRepository.get_by_id(user_id)
        select = CourseRequestsDB()
        select.sample_by_creator_id(user.id)

        course_data = []
        for course in select.get_iterator_course():
            course_data.append(cls.get_by_id(course.id))

        return course_data

    @classmethod
    def create(cls, data: CreateCourseSchema, creator_id: int) -> GetCourseSchema:
        check_image_format(data.image.content_type)
        user = repository_users.UserRepository.get_by_id(creator_id)

        course = CoursesModel.create(
            creator_id=user.id,
            title=data.title,
            description=data.description,
            created_at=datetime.date.today()
        )

        cls.save_images(course.id, data.image)
        return cls.get_by_id(course.id)

    @classmethod
    def update_course(cls, data: UpdateCourseSchema, user_id: int) -> GetCourseSchema:
        if not cls.get_by_id(data.id) in cls.get_by_creator_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="no access"
            )


        select = CourseRequestsDB()
        select.sample_by_id(data.id)

        if data.image:
            check_image_format(data.image.content_type)
            cls.remove_image_by_id(select.get_first_course().id)
            cls.save_images(select.get_first_course().id, data.image)

        if data.title:
            select.update_title(data.title)

        if data.description:
            select.update_description(data.description)



        select.save()

        return cls.get_by_id(data.id)

    @classmethod
    def delete_by_id(cls, course_id, user_id):
        if not cls.get_by_id(course_id) in cls.get_by_creator_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="no access"
            )

        select = CourseRequestsDB()
        select.sample_by_id(course_id)

        modules = repository_modules.ModulRepository.get_all_by_course_id(course_id)

        for module in modules:
            repository_modules.ModulRepository.delete_by_id(module.id)

        cls.remove_image_by_id(course_id)
        select.delete()
