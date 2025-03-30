from PIL import Image
from faker import Faker
import datetime

from auth.hashing import get_password_hash
import random

from config import IMAGE_DIR, DB_DIR
from dataBase import CoursesModel, UsersModel
from dataBase.data import BelongingCategoryModel, ImageFormatModel, ModuleModel
from routers.dependencies import get_image_path, COURSE_TYPE, MODULE_TYPE, USER_TYPE
from routers.images.db_requests import IMAGE_MODEL_BY_TYPE
from routers.images.repository import ORIGINAL_FORMAT_IMAGE

fake = Faker()

IMAGES_PATH = DB_DIR.joinpath("generate").joinpath("Images")

def save_images(model_id: int, model_type: str):
    for form in ImageFormatModel.select():
        file_path = get_image_path(
            id_model=model_id,
            name_model=model_type,
            format_name=form.format_name
        )

        img = Image.open(IMAGES_PATH.joinpath(str(random.randint(1, 22))+".jpeg"))

        if form.format_name != ORIGINAL_FORMAT_IMAGE:
            img.thumbnail((form.width, form.height))

        img.save(file_path)

        IMAGE_MODEL_BY_TYPE.get(model_type).create(
            format=form.id,
            image_path=file_path.name,
            object_id=model_id
        )


def add_module(course: CoursesModel):
    title = fake.catch_phrase()
    description = fake.text(max_nb_chars=300)


    module = ModuleModel.create(
        course=course,
        title=title,
        description=description,
        video_URL="https://www.youtube.com/watch?v=ZY6uHybLoZA"
    )
    save_images(module.id, MODULE_TYPE)

def add_category(course: CoursesModel):
    if random.randint(1, 2) == 1:
        BelongingCategoryModel.create(course=course, category=1)

    if random.randint(1, 2) == 1:
        BelongingCategoryModel.create(course=course, category=2)

    if random.randint(1, 2) == 1:
        BelongingCategoryModel.create(course=course, category=3)

def add_course(user: UsersModel):
    title = fake.catch_phrase()
    description = fake.text(max_nb_chars=300)
    course = CoursesModel.create(creator=user, title=title, description=description)

    add_category(course)
    save_images(course.id, COURSE_TYPE)
    for i in range(random.randint(0, 20)):
        add_module(course)

def add_user():
    email = fake.email()
    password = get_password_hash(fake.password())
    name = fake.name()
    age = random.randint(15, 65)
    gender = random.randint(1, 2)  # 1 или 2
    print("USER: ", name, email)

    user = UsersModel.create(
        email=email,
        hashed_password=password,
        name=name,
        age=age,
        sex=gender,
        created_at=(datetime.date.today() - datetime.timedelta(days=random.randint(0, 2000)))
    )
    if random.randint(1, 5) == 1:
        save_images(user.id, USER_TYPE)
    if random.randint(1, 6) == 1:
        add_course(user)



def run():
    for _ in range(1):
        add_user()


if __name__ == "__main__":
    run()

