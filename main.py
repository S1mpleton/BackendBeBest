from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException

from routers import users, courses, modules, purchase



#GVT
#токен
#UI
#Яндекс трекер

#Ручки поиска КУрсов и модулей по курсу




app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(purchase.router)



# class ModelName(str, Enum):
#     alexnet = "alexn1et"
#     resnet = "resnet"
#     lenet = "lenet"

# @app.get("/models/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name is ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}
#
#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}
#
#     return {"model_name": model_name, "message": "Have some residuals"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)