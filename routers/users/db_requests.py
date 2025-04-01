from math import ceil

from peewee import fn, SQL, ModelSelect, Model

from auth.hashing import get_password_hash
from dataBase import UsersModel
from dataBase.data import BelongingCategoryModel, CategoryModel


class UserRequestsDB:
    def __init__(self):
        self.select = UsersModel.select()




    def get_count(self):
        return ceil(self.select.count())

    def sample_by_id(self, user_id: int):
        self.select = self.select.where(UsersModel.id == user_id)

    def sample_by_email(self, email: str):
        self.select = self.select.where(UsersModel.email == email)

    def update_name(self, name: str):
        for user in self.select:
            user.name = name

    def update_email(self, email: str):
        for user in self.select:
            user.email = email

    def update_password(self, password: str):
        for user in self.select:
            user.hashed_password = get_password_hash(password)

    def update_age(self, age: int):
        for user in self.select:
            user.age = age

    def update_sex(self, sex: int):
        for user in self.select:
            user.sex = sex

    def delete(self):
        for user in self.select:
            user.delete_instance(recursive=True, delete_nullable=True)

    def save(self):
        for user in self.select:
            user.save()

    def get_select(self):
        return self.select

    def get_first_user(self):
        return self.select.first()

    def get_iterator_user(self):
        yield from self.select


# c = UserRequestsDB()
# c.sample_by_email("qweasd@qwe.qwe")
# print(c.get_first_user().__data__)
# # c.split_by_pagination(1, 2)
# # c.order_by_description("Стройная")
#
# c.sample_by_categories("Финансы")
#
# for i in c.courses:
#     print(i.__data__)

