from peewee import *

from fuzzywuzzy import fuzz
import datetime




db = SqliteDatabase('dataBase/data.db')



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
    mail = CharField(null=False, max_length=100)
    password = CharField(null=False, max_length=100)
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
    format_name = CharField(null=False, max_length=50)
    width = IntegerField(null=False)
    height = IntegerField(null=False)
    description = CharField(null=True, max_length=100)
    class Meta:
        db_table = "ImagesFormat"


class ImageModel(BaseModel):
    format = ForeignKeyField(ImageFormatModel)
    image_path = CharField(null=False, max_length=200)


class ImageCourseModel(ImageModel):
    course = ForeignKeyField(CoursesModel)
    class Meta:
        db_table = "ImagesCourse"


class ImageModuleModel(ImageModel):
    module = ForeignKeyField(ModuleModel)
    class Meta:
        db_table = "ImagesModule"


class ImageUserModel(ImageModel):
    user = ForeignKeyField(UsersModel)
    class Meta:
        db_table = "ImagesUser"




if __name__ == "__main__":
    with db:
        db.create_tables([
            UsersModel, CoursesModel, PurchasesModel,
            ModuleModel, CategoryModel, BelongingCategoryModel,
            ImageCourseModel, ImageModuleModel, ImageUserModel, ImageFormatModel
        ])