from fastapi import APIRouter
from pydantic import BaseModel, Field, HttpUrl

from datetime import date
from dataBase import ModuleModel


router = APIRouter(
    prefix="/moduls",
    tags=["moduls🎞"]
)


class ModuleSchema(BaseModel):
    title: str = Field(max_length=150)
    description: str = Field(max_length=400)
    course_id: int = Field(ge=1)
    video_url: HttpUrl


@router.get(
    "/get/all",
    summary="Get all modules"
)
async def read_modules():
    all_modules = []
    for module in ModuleModel.select():
        all_modules.append({
            "ID": module.ID,
            "title": module.Title,
            "description": module.Description,
            "video_url": module.Video_URL,
            "course_id": module.Course_id,
            "created_at": module.Created_at
        })
    return all_modules


@router.get(
    "/get/id/{id_module}",
    summary="Get module for ID"
)
async def read_module_for_id(id_module: int):
    module = ModuleModel.get_by_id(id_module)
    return {
        "ID": module.ID,
        "title": module.Title,
        "description": module.Description,
        "video_url": module.Video_URL,
        "course_id": module.Course_id,
        "created_at": module.Created_at
    }


@router.get(
    "/get/course/id/{id_user}",
    summary="Get a moduls on course ID"
)
async def read_modules_for_course_id(id_course: int):
    courses_modules = []
    for module in ModuleModel.select().where(ModuleModel.Course == id_course):
        courses_modules.append({
            "ID": module.ID,
            "title": module.Title,
            "description": module.Description,
            "video_url": module.Video_URL,
            "course_id": module.Course_id,
            "created_at": module.Created_at
        })
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
        Created_at = date.today()
    ).save()
    return {"status": "ok"}