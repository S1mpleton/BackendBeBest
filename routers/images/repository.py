import os

from PIL import Image
from fastapi import UploadFile
from fastapi.responses import FileResponse

from config import IMAGE_DIR
from dataBase import ImageFormatModel
from dataBase.data import ORIGINAL_FORMAT_IMAGE
from routers.dependencies import get_image_path, FeaturedImageSchema, get_featured_image
from routers.images.db_requests import IMAGE_MODEL_BY_TYPE, ImageRequestsDB



class ImagesRepository:
    @classmethod
    def get_image_schema(cls, model_id: int, model_type: str) -> FeaturedImageSchema:
        select = ImageRequestsDB(model_type)
        select.sample_by_model_id(model_id)
        return get_featured_image(select.get_select())

    @classmethod
    def save_image(cls, model_id: int, model_type: str, image_data: UploadFile):
        for form in ImageFormatModel.select():
            file_path = get_image_path(
                id_model=model_id,
                name_model=model_type,
                format_name=form.format_name
            )

            img = Image.open(image_data.file)

            if form.format_name != ORIGINAL_FORMAT_IMAGE.format_name:
                img.thumbnail((form.width, form.height))

            img.save(file_path)

            IMAGE_MODEL_BY_TYPE.get(model_type).create(
                format=form.id,
                image_path=file_path.name,
                object_id=model_id
            )

    @classmethod
    def delete_image(cls, model_id: int, model_type: str):
        select = ImageRequestsDB(model_type)
        select.sample_by_model_id(model_id)

        for image in select.get_select():
            file_path = get_image_path(
                id_model=model_id,
                name_model=model_type,
                format_name=image.format.format_name
            )

            os.remove(file_path)
        select.delete()



    @classmethod
    def get_response_image(cls, image_name):
        file_path = IMAGE_DIR.joinpath(image_name)
        return FileResponse(file_path)
