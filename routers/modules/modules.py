from fastapi import APIRouter, Path
from fastapi.params import Depends

from typing import Annotated

from auth.dependencies import UserGetterByTokenType
from auth.utils import ACCESS_TOKEN_TYPE
from routers.modules.repository import ModulRepository
from routers.modules.schemes import PaginationModuleSchema, CreateModuleSchema, GetModuleSchema, UpdateModuleSchema, \
    GetPaginationModuleSchema
from routers.users.schemes import GetUserSchema

router = APIRouter(
    prefix="/modules",
    tags=["Modules📼"]
)



@router.get(
    "/getPageByCourseAndDescription/{id_course}",
    summary="Get page module by course"
)
async def read_modules(
        id_course: Annotated[int, Path(ge=1)],
        pagination: Annotated[GetPaginationModuleSchema, Depends()],
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> PaginationModuleSchema:
    if not all([pagination.number_page, pagination.number_page]):
        pagination.number_page = 1
        pagination.quantity_on_page = 30

    return ModulRepository.get_by_page(id_course, pagination)



@router.get(
    "/getById/{id_module}",
    summary="Get module for ID"
)
async def read_module_for_id(
        id_module: Annotated[int, Path(ge=1)],
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> GetModuleSchema:
    return ModulRepository.get_by_id(id_module)



@router.post(
    "/create",
    summary="Make modul in data base"
)
async def create_module(
        new_module: Annotated[CreateModuleSchema, Depends()],
        creator: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> GetModuleSchema:
    return ModulRepository.create(new_module, creator.id)




@router.patch(
    "/updateById/{id_module}",
    summary="Update module by id"
)
async def update_course(
        module: Annotated[UpdateModuleSchema, Depends()],
        creator: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> GetModuleSchema:
    return ModulRepository.update_module(module)




@router.delete(
    "/deleteById/{id_module}",
    summary="Delete module by id"
)
async def delete_course(
        id_module: Annotated[int, Path(ge=1)],
        creator: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
):
    ModulRepository.delete_by_id(id_module)
    return {"status": "ok"}




