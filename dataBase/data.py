from peewee import *

from datetime import date


db = SqliteDatabase('dataBase/data.db')


class UsersModel(Model):
    ID = IntegerField(primary_key=True)
    Name = CharField(max_length=25)
    Age = IntegerField(default=18)
    Mail = CharField(max_length=80)
    Role = CharField(max_length=25, default="user")
    Password = CharField(max_length=128)
    Created_at = DateField()

    class Meta:
        database = db # This model uses the "people.db" database
        db_table = "Users"


class CoursesModel(Model):
    ID = IntegerField(primary_key=True)
    Creator = ForeignKeyField(UsersModel)
    Title = CharField(max_length=50)
    Description = CharField(max_length=400)
    Created_at = DateField()

    class Meta:
        database = db # This model uses the "people.db" database
        db_table = "Courses"


class PurchasesModel(Model):
    ID = IntegerField(primary_key=True)
    User = ForeignKeyField(UsersModel)
    Course = ForeignKeyField(CoursesModel)
    #Payment_ID = IntegerField()
    #Payment_Method = CharField(max_length=80)
    created_at = DateField()

    class Meta:
        database = db
        db_table = "Purchases"


class ModuleModel(Model):
    ID = IntegerField(primary_key=True)
    Course = ForeignKeyField(CoursesModel)
    Title = CharField(max_length=50)
    Description = CharField(max_length=400)
    Video_URL = CharField(max_length=500)
    Created_at = DateField()

    class Meta:
        database = db
        db_table = "Moduls"



if __name__ == "__main__":
    db.create_tables([UsersModel, CoursesModel, PurchasesModel, ModuleModel])