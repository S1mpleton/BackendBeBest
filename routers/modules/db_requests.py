from math import ceil

from peewee import fn, SQL

from dataBase import ModuleModel


class ModuleRequestsDB:
    def __init__(self):
        self.select = ModuleModel.select()


    def get_count(self) -> int:
        return ceil(self.select.count())

    def order_by_description(self, description: str):
        self.select = self.select.select(
            ModuleModel,
            fn.ifNotNull(
                bool(description), fn.comparison(ModuleModel.title, description)
            ).alias('discount')
        ).order_by(SQL("discount").desc())

    def sample_by_pagination(self, number_page: int, quantity_on_page: int):
        self.select = self.select.paginate(number_page, quantity_on_page)

    def sample_by_id(self, module_id: int):
        self.select = self.select.where(ModuleModel.id == module_id)

    def sample_by_course_id(self, course_id: int):
        self.select = self.select.where(ModuleModel.course == course_id)

    def update_title(self, title: str):
        for module in self.select:
            module.title = title

    def update_description(self, description: str):
        for module in self.select:
            module.description = description

    def update_video_url(self, video_url: str):
        for module in self.select:
            module.video_URL = video_url

    def delete(self):
        for module in self.select:
            module.delete_instance(recursive=True, delete_nullable=True)

    def save(self):
        for module in self.select:
            module.save()

    def get_select(self):
        return self.select

    def get_first_modul(self):
        return self.select.first()

    def get_iterator_modul(self):
        yield from self.select

# a = ModuleRequestsDB()
# a.sample_by_course_id(2)
# a.sample_by_id(2)

# a.get_first_modul()
# a.update_title("1234")



# a.save()

# for i in a.get_one_modul():
    # print(i.__data__)

# print(a.get_count())
# a.delete()



