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
from .db_requests import UserRequestsDB






class UserRepository:
    @classmethod
    def get_user_id_for_email(cls, email: Depends(EmailStr)) -> int:
        select = UserRequestsDB()
        select.sample_by_email(str(email))
        user_model = select.get_first_user()

        if not user_model:
            return -1
        return user_model.id

    @classmethod
    def check_email_for_used(cls, email: Depends(EmailStr)):
        user_id = cls.get_user_id_for_email(email)

        if user_id > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already in use"
            )

    @classmethod
    def get_hashed_password(cls, user_id: int) -> str:
        select = UserRequestsDB()
        select.sample_by_id(user_id)

        user_model = select.get_first_user()
        return user_model.hashed_password


    @classmethod
    def get_image_schema_by_id(cls, user_id: int) -> FeaturedImageSchema:
        return repository_images.ImagesRepository.get_image_schema(user_id, USER_TYPE)

    @classmethod
    def remove_image_by_id(cls, user_id: int):
        repository_images.ImagesRepository.delete_image(user_id, USER_TYPE)

    @classmethod
    def save_images(cls, user_id: int, image_data: UploadFile):
        repository_images.ImagesRepository.save_image(
            model_id=user_id,
            model_type=USER_TYPE,
            image_data=image_data.file
        )



    @classmethod
    def get_user_for_email(cls, email: Depends(EmailStr)) -> GetUserSchema:
        user_id = cls.get_user_id_for_email(email)

        if user_id < 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email"
            )

        return cls.get_by_id(user_id)

    @classmethod
    def get_all(cls) -> list[GetUserSchema]:
        select = UserRequestsDB()

        response = []
        for user in select.get_iterator_user():
            response.append(cls.get_by_id(user.id))
        return response

    @classmethod
    def get_by_id(cls, user_id: int) -> GetUserSchema:
        select = UserRequestsDB()
        select.sample_by_id(user_id)
        user = select.get_first_user()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )

        featured_image = cls.get_image_schema_by_id(user_id)

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

        featured_image = cls.get_image_schema_by_id(user.id)

        user.__data__["featuredImage"] = featured_image
        return GetUserSchema(**user.__data__)

    @classmethod
    def delete_by_id(cls, user_id):
        cls.get_by_id(user_id)

        select = UserRequestsDB()
        select.sample_by_id(user_id)

        courses = repository_courses.CourseRepository.get_by_creator_id(user_id)
        for course in courses:
            repository_courses.CourseRepository.delete_by_id(course.id)

        cls.remove_image_by_id(user_id)
        select.delete()

    @classmethod
    def update_user(cls, user_id: int, data: UpdateUserSchema) -> GetUserSchema:
        cls.check_email_for_used(data.email)
        cls.get_by_id(user_id)

        select = UserRequestsDB()
        select.sample_by_id(user_id)

        if data.image:
            check_image_format(data.image.content_type)
            cls.remove_image_by_id(select.get_first_user().id)
            cls.save_images(select.get_first_user().id, data.image)

        if data.age:
            select.update_age(data.age)

        if data.sex:
            select.update_sex(data.sex)

        if data.name:
            select.update_name(data.name)

        if data.email:
            select.update_email(str(data.email))

        if data.password:
            select.update_password(data.password)

        select.save()

        return cls.get_by_id(select.get_first_user().id)

