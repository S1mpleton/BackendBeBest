from peewee import *  # Ensure Peewee library is installed

from fuzzywuzzy import fuzz




db = SqliteDatabase('dataBase/data.db')

@db.func('comparison')
def comparison(string_1, string_2):
    return fuzz.WRatio(string_1, string_2)


class BaseModel(Model):
    ID = IntegerField(primary_key=True, unique=True)

    class Meta:
        order_by = "ID"
        database = db


class UsersModel(BaseModel):
    Name = CharField(max_length=25)
    Age = IntegerField(default=18)
    Sex = IntegerField(default=0)
    Mail = CharField(max_length=80)
    Role = CharField(max_length=25, default="user")
    Created_at = DateField()

    class Meta:
        db_table = "Users"


class CoursesModel(BaseModel):
    Creator = ForeignKeyField(UsersModel)
    Title = CharField(max_length=50)
    Description = CharField(max_length=400)
    Image_URL = CharField(max_length=500)
    Created_at = DateField()

    class Meta:
        db_table = "Courses"


class ModuleModel(BaseModel):
    Course = ForeignKeyField(CoursesModel)
    Title = CharField(max_length=50)
    Description = CharField(max_length=400)
    Video_URL = CharField(max_length=500)
    Image_URL = CharField(max_length=500)
    Created_at = DateField()

    class Meta:
        db_table = "Moduls"


class PurchasesModel(BaseModel):
    User = ForeignKeyField(UsersModel)
    Course = ForeignKeyField(CoursesModel)
    Created_at = DateField()

    class Meta:
        db_table = "Purchases"


class CategoryModel(BaseModel):
    Course = ForeignKeyField(CoursesModel)
    Category = CharField(max_length=50)

    class Meta:
        db_table = "Categories"



if __name__ == "__main__":
    with db:
        db.create_tables([UsersModel, CoursesModel, PurchasesModel, ModuleModel, CategoryModel])