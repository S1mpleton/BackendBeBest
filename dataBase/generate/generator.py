import io
import random

from faker import Faker
from pathlib import Path

from fastapi import UploadFile
from pydantic import HttpUrl

from config import DB_DIR
from dataBase.data import BelongingCategoryModel
from routers.courses.repository import CourseRepository
from routers.courses.schemes import CreateCourseSchema
from routers.dependencies import COURSE_TYPE, MODULE_TYPE, USER_TYPE
from routers.modules.repository import ModulRepository
from routers.modules.schemes import CreateModuleSchema
from routers.users.repository import UserRepository
from routers.users.schemes import CreateUserSchema, UpdateUserSchema




IMAGE_GENERATE_PATH = DB_DIR.joinpath("generate").joinpath("images")

IMAGE_USERS_PATH = IMAGE_GENERATE_PATH.joinpath("users")
IMAGE_MODULES_PATH = IMAGE_GENERATE_PATH.joinpath("modules")
IMAGES_COURSES_PATH = IMAGE_GENERATE_PATH.joinpath("courses")

TYPE_NAME_DIR = {
    USER_TYPE: IMAGE_USERS_PATH,
    COURSE_TYPE: IMAGES_COURSES_PATH,
    MODULE_TYPE: IMAGE_MODULES_PATH
}

IMAGE_EXTENSION = {'.jpeg'}



# DIRTY CODE!!!!!
# In other words, just like all this project
class CustomUploadFile(UploadFile):
    def __init__(self, file: io.BytesIO, file_name: str, content_type: str):
        super().__init__(file=file, filename=file_name)
        self._content_type = content_type

    @property
    def content_type(self) -> str:
        return self._content_type


class GenerateData:
    TYPE_NAME_PHOTOS = {
        USER_TYPE: [
            f.name for f in IMAGE_USERS_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
        ],
        COURSE_TYPE: [
            f.name for f in IMAGES_COURSES_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
        ],
        MODULE_TYPE: [
            f.name for f in IMAGE_MODULES_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
        ]
    }

    def __init__(self, location="Russian"):
        self.fake = Faker(locale=location)

        self.count_users = 100
        self.chance_user_photo_create = 1 / 5

        # if user creates a course,
        self.chance_user_course_create = 1 / 6
        # he creates between self.min_course_quantity_on_user and self.max_course_quantity_on_use courses
        self.min_course_quantity_on_user = 1
        self.max_course_quantity_on_user = 4

        self.min_modules_in_course = 0
        self.max_modules_in_course = 18

    @classmethod
    def add_category(cls, course_id: int):
        if random.randint(1, 2) == 1:
            BelongingCategoryModel.create(course=course_id, category=1)

        if random.randint(1, 2) == 1:
            BelongingCategoryModel.create(course=course_id, category=2)

        if random.randint(1, 2) == 1:
            BelongingCategoryModel.create(course=course_id, category=3)

    @classmethod
    def get_rand_image_path(cls, model_type: str) -> Path:
        img_dir = TYPE_NAME_DIR.get(model_type)
        img_name = random.choice(cls.TYPE_NAME_PHOTOS.get(model_type))
        img_path = img_dir.joinpath(img_name)
        return img_path

    @classmethod
    def get_bin_image(cls, path: Path) -> io.BytesIO:
        with open(path, "rb") as file:
            bin_file = io.BytesIO(file.read())
        return bin_file

    def add_module(self, course_id: int, creator_id : int):
        path = self.get_rand_image_path(MODULE_TYPE)
        bin_file = self.get_bin_image(path)

        create_schema = CreateModuleSchema(
            course_id=course_id,
            title=self.fake.catch_phrase(),
            description=self.fake.text(max_nb_chars=500),
            video_URL=HttpUrl("https://www.youtube.com/watch?v=ZY6uHybLoZA"),
            image=CustomUploadFile(
                file=bin_file,
                file_name=path.name,
                content_type="image/jpeg")
        )

        return ModulRepository.create(create_schema, creator_id).id

    def add_course(self, user_id: int):
        path = self.get_rand_image_path(COURSE_TYPE)
        bin_file = self.get_bin_image(path)

        create_schema = CreateCourseSchema(
            title=self.fake.catch_phrase(),
            description=self.fake.text(max_nb_chars=500),
            image=CustomUploadFile(
                file=bin_file,
                file_name=path.name,
                content_type="image/jpeg")
        )
        print("\tCOURSE: ")
        print("\t\t", f"title: {create_schema.title}")

        return CourseRepository.create(create_schema, user_id).id

    def add_user(self):
        path = self.get_rand_image_path(USER_TYPE)
        bin_file = self.get_bin_image(path)

        email = self.fake.email()
        password = self.fake.password()
        name = self.fake.name()

        print("\nUSER: ")
        print("\t", f"Name: {name} | Email: {email} | Password: {password}")

        create_schema = CreateUserSchema(
            name=name,
            email=email,
            password=password
        )
        user = UserRepository.create(create_schema)

        image = None
        if random.random() <= self.chance_user_photo_create:
            image = CustomUploadFile(
                file=bin_file,
                file_name=path.name,
                content_type="image/jpeg"
            )

        update_schema = UpdateUserSchema(
            sex=random.randint(1, 2),
            age=random.randint(14, 74),
            image=image
        )

        UserRepository.update_user(user.id, update_schema)
        return user.id


    def create(self):
        for _ in range(self.count_users):
            user_id = self.add_user()

            if random.random() > self.chance_user_course_create:
                continue
            for _ in range(random.randint(self.min_course_quantity_on_user, self.max_course_quantity_on_user)):
                course_id = self.add_course(user_id)
                GenerateData.add_category(course_id)

                for _ in range(random.randint(self.min_modules_in_course, self.max_modules_in_course)):
                    self.add_module(course_id, user_id)


if __name__ == "__main__":
    GenerateData().create()