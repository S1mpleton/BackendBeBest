from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException

from routers import users

#GVT
#токен
#UI
#Яндекс трекер




app = FastAPI()

app.include_router(users.router)




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