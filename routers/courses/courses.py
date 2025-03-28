from fastapi import APIRouter, Path, UploadFile, File, Depends, Query

from typing import Annotated, Union

from routers.courses.repository import CourseRepository
from routers.courses.schemes import PaginationCourseSchema, GetCourseSchema, CreateCourseSchema, UpdateCourseSchema

router = APIRouter(
    prefix="/courses",
    tags=["Courses📺"]
)



@router.get(
    "/getPageByDescription",
    summary="Get page courses for description"
)
async def read_course_for_id(
        number_page: Annotated[Union[int, None], Query(ge=1)] = None,
        quantity_on_page: Annotated[Union[int, None], Query(ge=1)] = None,
        description: Annotated[Union[str, None], Query(max_length=50)] = None
)-> PaginationCourseSchema:
    if not number_page or not quantity_on_page:
        number_page = 1
        quantity_on_page = 30

    return CourseRepository.get_by_page(number_page, quantity_on_page, description)



@router.get(
    "/getById/{id_course}",
    summary="Get course for ID"
)
async def read_course_for_id(id_course: Annotated[int, Path(ge=1)]) -> GetCourseSchema:
    return CourseRepository.get_by_id(id_course)




@router.get(
    "/getByIdCreator/{id_user}",
    summary="Get courses by their creator(user_id) ID"
)
async def read_courses_for_user_creator_id(id_user: Annotated[int, Path(ge=1)])-> list[GetCourseSchema]:
    return CourseRepository.get_by_creator_id(id_user)




@router.post(
    "/create",
    summary="Make course in data base"
)
async def create_course(new_course: Annotated[CreateCourseSchema, Depends()]) -> GetCourseSchema:
    return CourseRepository.create(new_course)



@router.patch(
    "/updateById/{id_course}",
    summary="Update full course by id"
)
async def update_course(course: Annotated[UpdateCourseSchema, Depends()]) -> GetCourseSchema:
    return CourseRepository.update_course(course)



@router.delete(
    "/deleteById/{id_course}",
    summary="Delete course by id, also deleted all modules, in this course"
)
async def delete_course(id_course: Annotated[int, Path(ge=1)]):
    CourseRepository.delete_by_id(id_course)
    return {"status": "ok"}
