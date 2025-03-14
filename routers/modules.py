from fastapi import APIRouter, Path, Response, Query, File, UploadFile, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, Field, HttpUrl

from typing import Union, Annotated
from dataBase.repository import ModulRepository
from routers.schemes import ModuleSchema, PaginationModuleSchema, CreateModuleSchema, GetModuleSchema, \
    allowed_mime_types




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
    if new_module.image.content_type not in allowed_mime_types:
        raise HTTPException(status_code=400, detail="File type not supported. File isn't PNG, JPEG")

    return ModulRepository.create(new_module)




@router.put(
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
    return ModulRepository.update_course(id_module, title, description, video_url, image)




@router.delete(
    "/deleteById/{id_module}",
    summary="Delete module by id"
)
async def delete_course(id_module: Annotated[int, Path(ge=1)]):
    try:
        ModulRepository.delete_by_id(id_module)


    except Exception as e:
        raise HTTPException(status_code=404, detail="Module not found")
        pass

    else:
        return {"status": "ok"}

    finally:
        pass


