from fastapi import APIRouter, Path, Response
from pydantic import BaseModel, Field, HttpUrl

from typing import Union, Annotated
from math import ceil
from datetime import date
from dataBase import ModuleModel


router = APIRouter(
    prefix="/moduls",
    tags=["Moduls📼"]
)


class ModuleSchema(BaseModel):
    course_id: int = Field(ge=1)
    title: str = Field(max_length=150)
    description: str = Field(max_length=400)
    image_url: HttpUrl
    video_url: HttpUrl




@router.get(
    "/getPageByCourse/{id_course}/{number_page}/{quantity_on_page}",
    summary="Get page module by course"
)
async def read_modules(
        id_course: Annotated[int, Path(ge=1)],
        number_page: Annotated[int, Path(ge=1)],
        quantity_on_page: Annotated[int, Path(ge=1)],
        response: Response
):
    total_elements = ceil(ModuleModel
                            .select(ModuleModel.ID)
                            .where(ModuleModel.Course == id_course)
                            .count())

    modules = (
        ModuleModel
        .select()
        .where(ModuleModel.Course == id_course)
        .limit(quantity_on_page).offset((number_page-1)*quantity_on_page)
        .order_by(ModuleModel.Created_at)
    )

    return {
        "data": [x.__data__ for x in modules],
        "pagination": {
            "current_page": number_page,
            "total_pages": ceil(total_elements / quantity_on_page),
            "total_elements": total_elements
        }
    }



@router.get(
    "/getById/{id_module}",
    summary="Get module for ID"
)
async def read_module_for_id(id_module: Annotated[int, Path(ge=1)]):
    module = ModuleModel.get_by_id(id_module)
    return module.__data__


@router.get(
    "/getByCourseId{id_course}",
    summary="Get a moduls on course ID"
)
async def read_modules_for_course_id(id_course: Annotated[int, Path(ge=1)]):
    courses_modules = [x.__data__ for x in ModuleModel.select().where(ModuleModel.Course == id_course)]
    return courses_modules




@router.post(
    "/create",
    summary="Make modul in data base"
)
async def create_module(new_module: ModuleSchema):
    ModuleModel(
        Course_id = new_module.course_id,
        Title = new_module.title,
        Description = new_module.description,
        Video_URL = new_module.video_url,
        Image_URL=new_module.image_url,
        Created_at = date.today()
    ).save()
    return {"status": "ok"}