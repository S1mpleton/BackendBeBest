from dataBase import ImageCourseModel, ImageUserModel, ImageModuleModel
from dataBase.data import ImageFormatModel
from routers.dependencies import USER_TYPE, MODULE_TYPE, COURSE_TYPE




IMAGE_MODEL_BY_TYPE = {
    USER_TYPE: ImageUserModel,
    COURSE_TYPE: ImageCourseModel,
    MODULE_TYPE: ImageModuleModel
}





class ImageRequestsDB:
    def __init__(self, type_model):
        self.type_model = type_model
        self.select = IMAGE_MODEL_BY_TYPE.get(type_model).select()

    def sample_by_model_id(self, model_id: int):
        self.select = (self.select.select(
                IMAGE_MODEL_BY_TYPE.get(self.type_model),
                ImageFormatModel
            )
            .join(ImageFormatModel)
            .where(IMAGE_MODEL_BY_TYPE.get(self.type_model).object == model_id)
        )

    def delete(self):
        for image in self.select:
            image.delete_instance(recursive=True, delete_nullable=True)

    def get_select(self):
        return self.select

