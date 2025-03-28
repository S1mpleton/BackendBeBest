from peewee import *

from fuzzywuzzy import fuzz
import datetime

from config import DB_DIR




DB_PATH = DB_DIR.joinpath("data.db")

db = SqliteDatabase(DB_PATH)



@db.func('comparison')
def comparison(string_1, string_2):
    return fuzz.WRatio(string_1, string_2)

@db.func('ifNotNull')
def comparison(value1, value2):
    if value1:
        return value2
    return value1


class BaseModel(Model):
    id = IntegerField(null=False, primary_key=True, unique=True)
    class Meta:
        order_by = "id"
        database = db


class UsersModel(BaseModel):
    email = CharField(null=False, max_length=100, unique=True)
    hashed_password = CharField(null=False, max_length=800)
    role = CharField(null=False, max_length=25, default="user")

    name = CharField(null=False, max_length=25, default="Гость")
    age = IntegerField(null=True, default=None)
    sex = IntegerField(null=True, default=None)

    created_at = DateField(null=False, default=datetime.date.today)
    class Meta:
        db_table = "Users"


class CoursesModel(BaseModel):
    creator = ForeignKeyField(UsersModel)

    title = CharField(max_length=50)
    description = CharField(max_length=600)

    created_at = DateField(null=False, default=datetime.date.today)
    class Meta:
        db_table = "Courses"


class ModuleModel(BaseModel):
    course = ForeignKeyField(CoursesModel)

    title = CharField(max_length=50)
    description = CharField(max_length=600)

    video_URL = CharField(max_length=500)
    created_at = DateField(null=False, default=datetime.date.today)
    class Meta:
        db_table = "Moduls"


class PurchasesModel(BaseModel):
    user = ForeignKeyField(UsersModel)
    course = ForeignKeyField(CoursesModel)

    created_at = DateField(null=False, default=datetime.date.today)
    class Meta:
        db_table = "Purchases"


class CategoryModel(BaseModel):
    category = CharField(null=False, max_length=100, unique=True)
    class Meta:
        db_table = "Categories"


class BelongingCategoryModel(BaseModel):
    course = ForeignKeyField(CoursesModel)
    category = ForeignKeyField(CategoryModel)
    class Meta:
        db_table = "BelongingCategories"


class ImageFormatModel(BaseModel):
    format_name = CharField(null=False, max_length=50, unique=True)
    width = IntegerField(null=False)
    height = IntegerField(null=False)
    description = CharField(null=True, max_length=100)
    class Meta:
        db_table = "ImagesFormat"


class ImageModel(BaseModel):
    format = ForeignKeyField(ImageFormatModel)
    image_path = CharField(null=False, max_length=200, unique=True)


class ImageCourseModel(ImageModel):
    object = ForeignKeyField(CoursesModel)
    class Meta:
        db_table = "ImagesCourse"


class ImageModuleModel(ImageModel):
    object = ForeignKeyField(ModuleModel)
    class Meta:
        db_table = "ImagesModule"


class ImageUserModel(ImageModel):
    object = ForeignKeyField(UsersModel)
    class Meta:
        db_table = "ImagesUser"




if __name__ == "__main__":
    with db:
        db.create_tables([
            UsersModel, CoursesModel, PurchasesModel,
            ModuleModel, CategoryModel, BelongingCategoryModel,
            ImageCourseModel, ImageModuleModel, ImageUserModel, ImageFormatModel
        ])