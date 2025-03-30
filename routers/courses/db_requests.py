from math import ceil

from peewee import fn, SQL, ModelSelect, Model

from dataBase import CoursesModel
from dataBase.data import BelongingCategoryModel, CategoryModel


class CourseRequestsDB:
    def __init__(self):
        self.select = CoursesModel.select()

    @classmethod
    def get_category_model(cls, category: str):
        return (
            CategoryModel.select()
            .where(CategoryModel.category == category)
            .first()
        )


    def get_count(self):
        return ceil(self.select.count())

    def order_by_description(self, description: str):
        self.select = self.select.select(
            CoursesModel,
            fn.ifNotNull(
                bool(description), fn.comparison(CoursesModel.title + CoursesModel.description, description)
            ).alias('discount')
        ).order_by(SQL("discount").desc())

    def sample_by_pagination(self, number_page: int, quantity_on_page: int):
        self.select = self.select.paginate(number_page, quantity_on_page)

    def sample_by_categories(self, category: str):
        category_model = self.get_category_model(category)

        category_courses_id = (
            BelongingCategoryModel
            .select(BelongingCategoryModel.course)
            .where(BelongingCategoryModel.category == category_model)
        )

        self.select = self.select.where(CoursesModel.id.in_(category_courses_id))

    def sample_by_id(self, course_id: int):
        self.select = self.select.where(CoursesModel.id == course_id)

    def sample_by_creator_id(self, user_id: int):
        self.select = self.select.where(CoursesModel.creator == user_id)

    def update_title(self, title: str):
        for course in self.select:
            course.title = title

    def update_description(self, description: str):
        for course in self.select:
            course.description = description

    def delete(self):
        for course in self.select:
            course.delete_instance(recursive=True, delete_nullable=True)

    def save(self):
        for course in self.select:
            course.save()

    def get_select(self):
        return self.select

    def get_first_course(self):
        return self.select.first()

    def get_iterator_course(self):
        yield from self.select

# c = CourseRequestsDB()
# # c.split_by_pagination(1, 2)
# # c.order_by_description("Стройная")
#
# c.sample_by_categories("Финансы")
#
# for i in c.courses:
#     print(i.__data__)

