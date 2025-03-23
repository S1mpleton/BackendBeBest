from fastapi import APIRouter, Path, Query, File, UploadFile
from fastapi.params import Depends
from pydantic import HttpUrl

from typing import Union, Annotated
from dataBase.repository import ModulRepository
from routers.schemes import PaginationModuleSchema, CreateModuleSchema, GetModuleSchema




router = APIRouter(
    prefix="/modules",
    tags=["Modules📼"]
)



@router.get(
    "/getPageByCourseAndDescription/{id_course}/{number_page}/{quantity_on_page}",
    summary="Get page module by course"
)
async def read_modules(
        id_course: Annotated[int, Path(ge=1)],
        number_page: Annotated[int, Path(ge=1)],
        quantity_on_page: Annotated[int, Path(ge=1)],
        description: Union[Annotated[str, Path(max_length=50)], None] = None
) -> PaginationModuleSchema:
    return ModulRepository.get_by_page(id_course, number_page, quantity_on_page, description)



@router.get(
    "/getById/{id_module}",
    summary="Get module for ID"
)
async def read_module_for_id(id_module: Annotated[int, Path(ge=1)]):
    return ModulRepository.get_by_id(id_module)



@router.post(
    "/create",
    summary="Make modul in data base"
)
async def create_module(new_module: Annotated[CreateModuleSchema, Depends()]) -> GetModuleSchema:
    return ModulRepository.create(new_module)




@router.patch(
    "/updateById/{id_module}",
    summary="Update module by id"
)
async def update_course(
        id_module: Annotated[int, Path(ge=1)],
        title: Annotated[Union[str, None], Query(max_length=50)] = None,
        description: Annotated[Union[str, None], Query(max_length=600)] = None,
        video_url: Annotated[Union[HttpUrl, None], Query()] = None,
        image: Annotated[Union[UploadFile, None], File()] = None
) -> GetModuleSchema:
    return ModulRepository.update_module(id_module, title, description, video_url, image)




@router.delete(
    "/deleteById/{id_module}",
    summary="Delete module by id"
)
async def delete_course(id_module: Annotated[int, Path(ge=1)]):
    ModulRepository.delete_by_id(id_module)
    return {"status": "ok"}




