from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel, Field
from dataBase import CoursesModel

router = APIRouter(
    prefix="/courses",
    tags=["Courses📺"]
)

class CourseSchema(BaseModel):
    title: str = Field(max_length=150)
    description: str = Field(max_length=400)
    creator_id: int = Field(ge=1)


@router.get(
    "/get/all",
    summary="Get all courses"
)
async def read_courses():
    all_courses = []
    for course in CoursesModel.select():
        all_courses.append({
            "ID": course.ID,
            "title": course.Title,
            "description": course.Description,
            "creator_id": course.Creator_id,
            "created_at": course.Created_at
        })
    return all_courses


@router.get(
    "/get/id/{id_course}",
    summary="Get course for ID"
)
async def read_course_for_id(id_course: int):
    course = CoursesModel.get_by_id(id_course)
    return {
        "ID": course.ID,
        "title": course.Title,
        "description": course.Description,
        "creator_id": course.Creator_id,
        "created_at": course.Created_at
    }


@router.get(
    "/get/user/id/{id_user}/creator",
    summary="Get courses by their creator(user_id) ID"
)
async def read_courses_for_user_creator_id(id_user: int):
    user_courses = []
    for course in CoursesModel.select().where(CoursesModel.Creator == id_user):
        user_courses.append({
            "ID": course.ID,
            "title": course.Title,
            "description": course.Description,
            "creator_id": course.Creator_id,
            "created_at": course.Created_at
        })
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
        Created_at = date.today()
    ).save()
    return {"status": "ok"}

