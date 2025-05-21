from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from routers.users.users import router as users_router
from routers.modules.modules import router as modules_router
from routers.courses.courses import router as courses_router
from routers.images.images import router as images_router
from routers.purchase import router as purchase_router

from auth import auth





SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




app = FastAPI()


app.include_router(users_router)
app.include_router(courses_router)
app.include_router(modules_router)
app.include_router(images_router)
app.include_router(purchase_router)
app.include_router(auth.router)


origins = [
    "*",
    "https://bebest.fun"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)








if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)