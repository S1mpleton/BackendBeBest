from PIL import Image
from fastapi import UploadFile
from fastapi.responses import FileResponse

from config import IMAGE_DIR
from dataBase import ImageUserModel, ImageCourseModel, ImageModuleModel, ImageFormatModel
from routers.dependencies import USER_TYPE, COURSE_TYPE, MODULE_TYPE, get_image_path

ORIGINAL_FORMAT_IMAGE = "original"

IMAGE_MODEL_BY_TYPE = {
    USER_TYPE: ImageUserModel,
    COURSE_TYPE: ImageCourseModel,
    MODULE_TYPE: ImageModuleModel
}


class ImagesRepository:
    @classmethod
    def save_image(cls, id_model: int, object_type: str, image_data: UploadFile):
        for form in ImageFormatModel.select():
            file_path = get_image_path(
                id_model=id_model,
                name_model=object_type,
                format_name=form.format_name
            )

            img = Image.open(image_data.file)

            if form.format_name != ORIGINAL_FORMAT_IMAGE:
                img.thumbnail((form.width, form.height))

            img.save(file_path)

            IMAGE_MODEL_BY_TYPE.get(object_type).create(
                format=form.id,
                image_path=file_path.name,
                object_id=id_model
            )

    @classmethod
    def get_response_image(cls, image_name):
        file_path = IMAGE_DIR.joinpath(image_name)
        return FileResponse(file_path)
