from fastapi import APIRouter, Path, UploadFile, File, Depends, Query

from typing import Annotated, Union

from dataBase.repository import CourseRepository
from routers.schemes import GetCourseSchema, CreateCourseSchema, PaginationCourseSchema

router = APIRouter(
    prefix="/courses",
    tags=["Courses📺"]
)



@router.get(
    "/getPageByDescription/{number_page}/{quantity_on_page}",
    summary="Get page courses for description"
)
async def read_course_for_id(
        number_page: Annotated[int, Path(ge=1)],
        quantity_on_page: Annotated[int, Path(ge=1)],
        description: Union[Annotated[str, Path(max_length=50)], None] = None
)-> PaginationCourseSchema:
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
async def update_course(
        id_course: Annotated[int, Path(ge=1)],
        title: Annotated[Union[str, None], Query(max_length=50)] = None,
        description: Annotated[Union[str, None], Query(max_length=600)] = None,
        image: Annotated[Union[UploadFile, None], File()] = None
):
    return CourseRepository.update_course(id_course, title, description, image)



@router.delete(
    "/deleteById/{id_course}",
    summary="Delete course by id, also deleted all modules, in this course"
)
async def delete_course(id_course: Annotated[int, Path(ge=1)]):
    CourseRepository.delete_by_id(id_course)
    return {"status": "ok"}
