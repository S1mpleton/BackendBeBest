import datetime
import os
from math import ceil

from PIL import Image
from fastapi import UploadFile
from peewee import fn, SQL
from pydantic import HttpUrl

from dataBase import CoursesModel, ImageFormatModel, ImageCourseModel, ModuleModel, ImageModuleModel, UsersModel, \
    ImageUserModel
from routers.schemes import CreateCourseSchema, FeaturedImageSchema, GetCourseSchema, PaginationCourseSchema, \
    PaginationSchema, PaginationModuleSchema, GetModuleSchema, CreateModuleSchema, GetUserSchema, CreateUserSchema, \
    UserRole, UpdateUserSchema


class UserRepository:
    @classmethod
    def get_all(cls):
        pass

    @classmethod
    def get_image_by_user(cls, user: UsersModel) -> FeaturedImageSchema:
        feature = (
            ImageUserModel.select(ImageUserModel, ImageFormatModel)
            .join(ImageFormatModel)
            .where(ImageUserModel.user == user)
        )

        images = {}
        for f in feature:
            images[f.format.format_name] = f.image_path

        return FeaturedImageSchema(**images)

    @classmethod
    def remove_image_by_user(cls, user: UsersModel):
        images = ImageUserModel.select().where(ImageUserModel.user == user)

        for image in images:
            image.delete_instance(recursive=True, delete_nullable=True)

        if bool(images):
            for form in ImageFormatModel.select():
                file_name = f"{user.id}-user-{form.format_name}-{user.created_at}.jpg"
                file_path = os.path.join("resources", "images", file_name)

                os.remove(file_path)

    @classmethod
    def save_images(cls, user: UsersModel, image_data: UploadFile):
        for form in ImageFormatModel.select():

            file_name = f"{user.id}-user-{form.format_name}-{user.created_at}.jpg"
            file_path = os.path.join("resources", "images", file_name)

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageUserModel.create(
                format=form.id,
                image_path=file_name,
                user_id=user
            )



    @classmethod
    def get_by_id(cls, id_user: int) -> GetUserSchema:
        user = UsersModel.get_by_id(id_user)

        featured_image = UserRepository.get_image_by_user(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def create(cls, data: CreateUserSchema) -> GetUserSchema:
        user = UsersModel.create(
            mail=data.mail,
            password=data.password,
            name=data.name,
            role=UserRole.user,
            created_at=datetime.date.today()
        )

        featured_image = UserRepository.get_image_by_user(user)

        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)

    @classmethod
    def delete_by_id(cls, id_user):
        user = UsersModel.get_by_id(id_user)

        UserRepository.remove_image_by_user(user)

        courses = CoursesModel.select().where(CoursesModel.creator == user)
        for course in courses:
            CourseRepository.delete_by_id(course.id)

        user.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_user(cls, id_user: int, data: UpdateUserSchema) -> GetUserSchema:
        user = UsersModel.get_by_id(id_user)

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
            UserRepository.remove_image_by_user(user)
            UserRepository.save_images(user, data.image)

        user.save()

        featured_image = UserRepository.get_image_by_user(user)
        user.__data__["featuredImage"] = featured_image

        return GetUserSchema(**user.__data__)




class ModulRepository:
    @classmethod
    def get_all(cls):
        pass

    @classmethod
    def get_image_by_module(cls, module: ModuleModel) -> FeaturedImageSchema:
        feature = (ImageModuleModel.select(ImageModuleModel, ImageFormatModel)
                   .join(ImageFormatModel)
                   .where(ImageModuleModel.module == module))

        images = {}
        for f in feature:
            images[f.format.format_name] = f.image_path

        return FeaturedImageSchema(**images)

    @classmethod
    def remove_image_by_module(cls, module: ModuleModel):
        images = ImageModuleModel.select().where(ImageModuleModel.module == module)

        for image in images:
            image.delete_instance(recursive=True, delete_nullable=True)

        for form in ImageFormatModel.select():
            file_name = f"{module.id}-module-{form.format_name}-{module.created_at}.jpg"
            file_path = os.path.join("resources", "images", file_name)

            os.remove(file_path)

    @classmethod
    def save_images(cls, module: ModuleModel, image_data: UploadFile):
        for form in ImageFormatModel.select():

            file_name = f"{module.id}-module-{form.format_name}-{module.created_at}.jpg"
            file_path = os.path.join("resources", "images", file_name)

            img = Image.open(image_data.file)

            if form.format_name != "original":
                img = img.resize((form.width, form.height))

            img.save(file_path)

            ImageModuleModel.create(
                format=form.id,
                image_path=file_name,
                module_id=module
            )



    @classmethod
    def get_by_id(cls, id_module: int) -> GetModuleSchema:
        module = ModuleModel.get_by_id(id_module)

        featured_image = ModulRepository.get_image_by_module(module)

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
            featured_image = ModulRepository.get_image_by_module(module)

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
        module = ModuleModel.create(
            course_id=data.course_id,
            title=data.title,
            description=data.description,
            video_URL=data.video_URL,
            created_at=datetime.date.today()
        )

        ModulRepository.save_images(module, data.image)

        featured_image = ModulRepository.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)

    @classmethod
    def delete_by_id(cls, id_module):
        module = ModuleModel.get_by_id(id_module)

        ModulRepository.remove_image_by_module(module)

        module.delete_instance(recursive=True, delete_nullable=True)

    @classmethod
    def update_course(
            cls, id_module: int, title: str, description: str,
            video_url: HttpUrl, image: UploadFile
    ) -> GetModuleSchema:
        module = ModuleModel.get_by_id(id_module)

        if title:
            module.title = title

        if description:
            module.description = description

        if video_url:
            module.video_URL = video_url

        if image:
            ModulRepository.remove_image_by_module(module)
            ModulRepository.save_images(module, image)

        module.save()

        featured_image = ModulRepository.get_image_by_module(module)

        module.__data__["featuredImage"] = featured_image
        module.__data__["course_id"] = module.__data__.pop("course")

        return GetModuleSchema(**module.__data__)






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

        modules = ModuleModel.select().where(ModuleModel.course == course)
        for module in modules:
            ModulRepository.delete_by_id(module.id)

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
