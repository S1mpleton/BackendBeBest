from datetime import date
from fastapi import APIRouter, Path,  Response
from pydantic import BaseModel, Field, HttpUrl
from dataBase import CoursesModel
from typing import Annotated

from math import ceil
from peewee import fn, SQL

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

router = APIRouter(
    prefix="/courses",
    tags=["Courses📺"]
)

class CourseSchema(BaseModel):
    creator_id: int = Field(ge=1)
    title: str = Field(max_length=150)
    description: str = Field(max_length=400)
    image_url: HttpUrl



@router.get(
    "/getAll",
    summary="Get all courses"
)
async def read_courses():
    all_courses = [x.__data__ for x in CoursesModel.select()]
    return all_courses



@router.get(
    "/getPageByDescription/{number_page}/{quantity_on_page}/{description}",
    summary="Get page courses for description"
)
async def read_course_for_id(
        number_page: Annotated[int, Path(ge=1)],
        quantity_on_page: Annotated[int, Path(ge=1)],
        description: Annotated[str, Path(max_length=50)],
        response: Response
):
    response.headers["quantity_pages"] = str(ceil(CoursesModel
                                                  .select(CoursesModel.ID)
                                                  .count() / quantity_on_page))

    courses = (
        CoursesModel
        .select(
            CoursesModel,
            fn.comparison(CoursesModel.Title, description).alias('discount')
        )
        .limit(quantity_on_page).offset((number_page - 1) * quantity_on_page)
        .order_by(SQL("discount").desc())
    )

    return [x.__data__ for x in courses]



@router.get(
    "/getById/{id_course}",
    summary="Get course for ID"
)
async def read_course_for_id(id_course: Annotated[int, Path(ge=1)]):
    course = CoursesModel.get_by_id(id_course)
    return course.__data__



@router.get(
    "/getByIdCreator/{id_user}",
    summary="Get courses by their creator(user_id) ID"
)
async def read_courses_for_user_creator_id(id_user: Annotated[int, Path(ge=1)]):
    user_courses = [x.__data__ for x in CoursesModel.select().where(CoursesModel.Creator == id_user)]
    return user_courses




@router.post(
    "/create",
    summary="Make course in data base"
)
async def create_course(new_course: CourseSchema):
    CoursesModel(
        Creator_id = new_course.creator_id,
        Title = new_course.title,
        Description = new_course.description,
        Image_URL = new_course.image_url,
        Created_at = date.today()
    ).save()
    return {"status": "ok"}

