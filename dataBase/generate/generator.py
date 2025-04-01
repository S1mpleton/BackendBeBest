from faker import Faker
import datetime

from auth.hashing import get_password_hash
import random

from config import DB_DIR
from dataBase import CoursesModel, UsersModel
from dataBase.data import BelongingCategoryModel, ModuleModel
from routers.dependencies import COURSE_TYPE, MODULE_TYPE, USER_TYPE
from routers.images.repository import ImagesRepository




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

USER_NAME_PHOTO = [
    f.name for f in IMAGE_USERS_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
]

COURSE_NAME_PHOTO = [
    f.name for f in IMAGES_COURSES_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
]

MODULE_NAME_PHOTO = [
    f.name for f in IMAGE_MODULES_PATH.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSION
]

TYPE_NAME_PHOTOS = {
    USER_TYPE: USER_NAME_PHOTO,
    COURSE_TYPE: COURSE_NAME_PHOTO,
    MODULE_TYPE:  MODULE_NAME_PHOTO
}



COUNT_USERS = 100
CHANCE_USER_PHOTO_CREATE = 1/5

# if user creates a course, he creates between MIN_COURSE_ON_USER and MAX_COURSE_ON_USER courses
CHANCE_USER_COURSE_CREATE = 1/8
MIN_COURSE_ON_USER = 1
MAX_COURSE_ON_USER = 4

MIN_MODULES_IN_COURSE = 0
MAX_MODULES_IN_COURSE = 18



fake = Faker(locale="Russian")

def save_images(model_id: int, model_type: str):
    image_dir = TYPE_NAME_DIR.get(model_type)
    image_name = random.choice(TYPE_NAME_PHOTOS.get(model_type))

    full_name = image_dir.joinpath(image_name)

    ImagesRepository.save_image(model_id, model_type, full_name)


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
    description = fake.text(max_nb_chars=500)
    course = CoursesModel.create(creator=user, title=title, description=description)
    print("\tCOURSE: ")
    print("\t\t", f"title: {title} | Id: {course.id}")

    add_category(course)
    save_images(course.id, COURSE_TYPE)
    for i in range(random.randint(MIN_MODULES_IN_COURSE, MAX_MODULES_IN_COURSE)):
        add_module(course)

def add_user():
    email = fake.email()
    password = fake.password()
    hash_password = get_password_hash(password)
    name = fake.name()
    age = random.randint(15, 65)
    gender = random.randint(1, 2)  # 1 или 2
    print("USER: ")
    print("\t", f"Name: {name} | Email: {email} | Password: {password}")

    user = UsersModel.create(
        email=email,
        hashed_password=hash_password,
        name=name,
        age=age,
        sex=gender,
        created_at=(datetime.date.today() - datetime.timedelta(days=random.randint(0, 2000)))
    )
    if random.random() <= CHANCE_USER_PHOTO_CREATE:
        save_images(user.id, USER_TYPE)

    if random.random() <= CHANCE_USER_COURSE_CREATE:
        for _ in range(random.randint(MIN_COURSE_ON_USER, MAX_COURSE_ON_USER)):
            add_course(user)



def run(how_users: int):
    for _ in range(how_users):
        add_user()



if __name__ == "__main__":
    run(COUNT_USERS)
