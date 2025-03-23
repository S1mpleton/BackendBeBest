import datetime
import os
from math import ceil

from PIL import Image
from fastapi import UploadFile, HTTPException, status, Depends
from peewee import fn, SQL, ModelSelect
from pydantic import HttpUrl, EmailStr
from typing import Union, Annotated

from auth.hashing import get_password_hash
from config import IMAGE_DIR
from dataBase import CoursesModel, ImageFormatModel, ImageCourseModel, ModuleModel, ImageModuleModel, UsersModel, \
    ImageUserModel
from routers.schemes import *


allowed_mime_types = ["image/jpeg", "image/png"]


def get_image_path(
    id_model: int, name_model: str,
    format_name: str, created_at_model
):
    file_name = f"{id_model}-{name_model}-{format_name}-{created_at_model}.jpg"
    file_path = IMAGE_DIR.joinpath(file_name)
    return file_path

def get_featured_image(db_request: ModelSelect) -> FeaturedImageSchema:
    images = {}
    for f in db_request:
        images[f.format.format_name] = f.image_path

    return FeaturedImageSchema(**images)

def check_image_format(content_type):
    if content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. File isn't PNG, JPEG"
        )



class UserRepository:
    @classmethod
    def get_user_for_email(cls, email: Depends(EmailStr)) -> UsersModel:
        return UsersModel.select().where(UsersModel.mail == email).first()

    @classmethod
    def check_email(cls, email: EmailStr):
        if cls.get_user_for_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    @classmethod
    def get_user_by_id(cls, id_user) -> UsersModel:
        try:
            return UsersModel.get_by_id(id_user)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not fount")

    @classmethod
    def get_image_request_by_user(cls, user: UsersModel) -> ModelSelect:
        images = (
            ImageUserModel.select(
                ImageUserModel,
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(ImageUserModel.user == user)
        )

        return images

    @classmethod
    def get_image_by_user(cls, user: UsersModel) -> FeaturedImageSchema:
        images = UserRepository.get_image_request_by_user(user)

        return get_featured_image(images)

    @classmethod
    def remove_image_by_user(cls, user: UsersModel):
        images = UserRepository.get_image_request_by_user(user)

        for image in images:
            file_path = get_image_path(
                id_model=user.id,
                name_model="user",
                format_name=image.format.format_name,
                created_at_model=user.created_at
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def save_images(cls, user: UsersModel, image_data: UploadFile):
        for form in ImageFormatModel.select():
            file_path = get_image_path(
                user.id,
                "user",
                form.format_name,
                user.created_at
            )

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageUserModel.create(
                format=form.id,
                image_path=file_path.name,
                user_id=user
            )



    @classmethod
    def get_by_id(cls, id_user: int) -> GetUserSchema:
        user = cls.get_user_by_id(id_user)
        featured_image = UserRepository.get_image_by_user(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def create(cls, data: CreateUserSchema) -> GetUserSchema: # Check email
        cls.check_email(data.mail)

        user = UsersModel.create(
            mail=data.mail,
            hashed_password=get_password_hash(data.password),
            name=data.name,
            role=UserRole.user,
            created_at=datetime.date.today()
        )

        featured_image = UserRepository.get_image_by_user(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def delete_by_id(cls, id_user):
        user = cls.get_user_by_id(id_user)

        cls.remove_image_by_user(user)

        courses = CoursesModel.select().where(CoursesModel.creator == user)
        for course in courses:
            CourseRepository.delete_by_id(course.id)

        user.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_user(cls, id_user: int, data: UpdateUserSchema) -> GetUserSchema:
        user = cls.get_user_by_id(id_user)
        cls.check_email(data.mail)
        check_image_format(data.image.content_type)

        if data.age:
            user.age = data.age

        if data.name:
            user.name = data.name

        if data.mail:
            user.mail = data.mail

        if data.password:
            user.password = data.password

        if data.sex:
            user.sex = data.sex

        if data.image:
            cls.remove_image_by_user(user)
            cls.save_images(user, data.image)

        user.save()

        featured_image = UserRepository.get_image_by_user(user)
        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)




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
            .where(ImageModuleModel.module == module)
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
                format_name=image.format.format_name,
                created_at_model=module.created_at
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def save_images(cls, module: ModuleModel, image_data: UploadFile):
        for form in ImageFormatModel.select():
            file_path = get_image_path(
                module.id,
                "module",
                form.format_name,
                module.created_at
            )

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageModuleModel.create(
                format=form.id,
                image_path=file_path.name,
                module_id=module
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
            cls, id_course: int, number_page: int, quantity_on_page: int, description: str
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
        course = CourseRepository.get_course_by_id(data.course_id)

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
    def update_module(
            cls, id_module: int, title: str, description: str,
            video_url: HttpUrl, image: UploadFile
    ) -> GetModuleSchema:
        module = cls.get_module_by_id(id_module)
        check_image_format(image.content_type)

        if title:
            module.title = title

        if description:
            module.description = description

        if video_url:
            module.video_URL = video_url

        if image:
            cls.remove_image_by_module(module)
            cls.save_images(module, image)

        module.save()

        featured_image = cls.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)






class CourseRepository:
    @classmethod
    def get_course_by_id(cls, id_course) -> CoursesModel:
        try:
            return CoursesModel.get_by_id(id_course)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not fount")

    @classmethod
    def get_image_request_by_course(cls, course: CoursesModel) -> ModelSelect:
        images = (
            ImageCourseModel.select(
                ImageCourseModel,
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(ImageCourseModel.course == course)
        )

        return images

    @classmethod
    def remove_image_by_course(cls, course: CoursesModel):
        images = cls.get_image_request_by_course(course)

        for image in images:
            file_path = get_image_path(
                id_model=course.id,
                name_model="course",
                format_name=image.format.format_name,
                created_at_model=course.created_at
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def get_image_by_course(cls, course: CoursesModel) -> FeaturedImageSchema:
        images = cls.get_image_request_by_course(course)

        return get_featured_image(images)

    @classmethod
    def save_images(cls, course: CoursesModel, image_data: UploadFile):
        for form in ImageFormatModel.select():
            file_path = get_image_path(
                course.id,"course", form.format_name, course.created_at
            )

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageCourseModel.create(
                format=form.id,
                image_path=file_path.name,
                course_id=course
            )



    @classmethod
    def get_by_id(cls, id_course: int) -> GetCourseSchema:
        course = cls.get_course_by_id(id_course)

        featured_image = CourseRepository.get_image_by_course(course)

        course.__data__["featuredImage"] = featured_image
        course.__data__["creator_id"] = course.__data__.pop("creator")

        return GetCourseSchema(**course.__data__)

    @classmethod
    def create(cls, data: CreateCourseSchema) -> GetCourseSchema:
        check_image_format(data.image.content_type)
        user = UserRepository.get_user_by_id(data.creator_id)

        course = CoursesModel.create(
            creator_id=user,
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
        user = UserRepository.get_user_by_id(id_user)
        for course in CoursesModel.select().where(CoursesModel.creator == user):
            CourseRepository.get_image_by_course(course)

            featured_image = CourseRepository.get_image_by_course(course)

            course.__data__["featuredImage"] = featured_image
            course.__data__["creator_id"] = course.__data__.pop("creator")

            course_data.append(GetCourseSchema(**course.__data__))

        return course_data

    @classmethod
    def delete_by_id(cls, id_course):
        course = CoursesModel.get_by_id(id_course)

        modules = ModuleModel.select().where(ModuleModel.course == course)
        for module in modules:
            ModulRepository.delete_by_id(module.id)

        CourseRepository.remove_image_by_course(course)

        course.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_course(cls, id_course: int, title: str, description: str, image: UploadFile) -> GetCourseSchema:
        course = CoursesModel.get_by_id(id_course)
        check_image_format(image.content_type)

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
