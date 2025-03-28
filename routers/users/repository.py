import datetime
import os

from PIL import Image
from fastapi import Depends, HTTPException, status, UploadFile
from peewee import ModelSelect
from pydantic import EmailStr

from auth.hashing import get_password_hash
from dataBase import UsersModel, ImageUserModel, ImageFormatModel, CoursesModel
from routers.dependencies import (
    FeaturedImageSchema, get_featured_image,
    get_image_path, check_image_format,
    USER_TYPE
)
from routers.users.schemes import GetUserSchema, UpdateUserSchema, CreateUserSchema, UserRole

from ..courses import repository as repository_courses
from ..images import repository as repository_images






class UserRepository:
    @classmethod
    def get_user_id_for_email(cls, email: EmailStr) -> int:
        user_id = UsersModel.select(UsersModel.id).where(UsersModel.email == email).first()
        if bool(user_id):
            return user_id.__data__["id"]
        return -1

    @classmethod
    def check_email_for_used(cls, email: Depends(EmailStr)):
        if cls.get_user_id_for_email(email) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already in use"
            )

    @classmethod
    def get_hashed_password(cls, user: GetUserSchema):
        return (
            UsersModel.select(
                UsersModel.hashed_password
            ).where(UsersModel.id == user.id)
            .first()
        ).__data__["hashed_password"]

    @classmethod
    def get_model_by_id(cls, id_user) -> UsersModel:
        try:
            return UsersModel.get_by_id(id_user)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not fount")

    @classmethod
    def get_image_request_by_model(cls, user: UsersModel) -> ModelSelect:
        images = (
            ImageUserModel.select(
                ImageUserModel,
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(ImageUserModel.object == user)
        )

        return images

    @classmethod
    def get_image_schema_by_model(cls, user: UsersModel) -> FeaturedImageSchema:
        images = cls.get_image_request_by_model(user)

        return get_featured_image(images)

    @classmethod
    def remove_image_by_model(cls, user: UsersModel):
        images = cls.get_image_request_by_model(user)

        for image in images:
            file_path = get_image_path(
                id_model=user.id,
                name_model="user",
                format_name=image.format.format_name
            )

            os.remove(file_path)
            image.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def save_images(cls, user: UsersModel, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            id_model=user.id,
            object_type=USER_TYPE,
            image_data=image_data
        )




    @classmethod
    def get_user_for_email(cls, email: Depends(EmailStr)) -> GetUserSchema:
        user_id = cls.get_user_id_for_email(email)
        if user_id < 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email"
            )

        user = cls.get_by_id(user_id)
        return user

    @classmethod
    def get_all(cls) -> list[GetUserSchema]:
        response = []
        users_id = UsersModel.select(UsersModel.id)
        for user_id in users_id:
            user = cls.get_by_id(user_id)
            response.append(user)

        return response

    @classmethod
    def get_by_id(cls, id_user: int) -> GetUserSchema:
        user = cls.get_model_by_id(id_user)
        featured_image = cls.get_image_schema_by_model(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def create(cls, data: CreateUserSchema) -> GetUserSchema: # Check email
        cls.check_email_for_used(data.email)

        user = UsersModel.create(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            name=data.name,
            role=UserRole.user,
            created_at=datetime.date.today()
        )

        featured_image = cls.get_image_schema_by_model(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def delete_by_id(cls, id_user):
        user = cls.get_model_by_id(id_user)

        cls.remove_image_by_model(user)

        courses = CoursesModel.select().where(CoursesModel.creator == user)
        for course in courses:
            repository_courses.CourseRepository.delete_by_id(course.id)

        user.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_user(cls, id_user: int, data: UpdateUserSchema) -> GetUserSchema:
        user = cls.get_model_by_id(id_user)
        cls.check_email_for_used(data.email)



        if data.image:
            check_image_format(data.image.content_type)
            cls.remove_image_by_model(user)
            cls.save_images(user, data.image)

        if data.age:
            user.age = data.age

        if data.name:
            user.name = data.name

        if data.email:
            user.email = data.email

        if data.password:
            user.hashed_password = get_password_hash(data.password)

        if data.sex:
            user.sex = data.sex

        user.save()

        featured_image = cls.get_image_schema_by_model(user)
        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

