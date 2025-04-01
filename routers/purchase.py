from fastapi import APIRouter
from pydantic import BaseModel, Field, EmailStr

from datetime import date
from typing import Union
from dataBase import PurchasesModel

router = APIRouter(
    prefix="/purchase",
    tags=["Purchase💸"]
)


class PurchaseSchema(BaseModel):
    user_id: int = Field(ge=1)
    course_id: int = Field(ge=1)

#
# @router.get(
#     "/get/id/{id_purchase}",
#     summary="Get purchase for ID"
# )
# async def read_purchase_for_id(id_purchase: int):
#     purchase = PurchasesModel.get_by_id(id_purchase)
#     return {
#         "ID": purchase.ID,
#         "user_id": purchase.User_id,
#         "course_id": purchase.Course_id,
#         "created_at": purchase.Created_at
#     }
#
#
# @router.get(
#     "/get/user/id/{id_user}",
#     summary="Get a purchases on user ID"
# )
# async def read_purchase_for_user_id(id_user: int):
#     user_purchase = []
#     for purchase in PurchasesModel.select().where(PurchasesModel.User == id_user):
#         user_purchase.append({
#         "ID": purchase.ID,
#         "user_id": purchase.User_id,
#         "course_id": purchase.Course_id,
#         "created_at": purchase.Created_at
#     })
#     return user_purchase
#
#
# @router.post(
#     "/create",
#     summary="Make purchase in data base"
# )
# async def create_purchase(new_purchase: PurchaseSchema):
#     PurchasesModel(
#         User_id = new_purchase.user_id,
#         Course_id = new_purchase.course_id,
#         Created_at = date.today() #with small symbol / fix later
#     ).save()
#     return {"status": "ok"}
