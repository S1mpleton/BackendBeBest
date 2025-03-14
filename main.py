from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from routers import users, courses, modules, purchase, images




#GVT
#токен
#UI
#Яндекс трекер







app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(modules.router)
app.include_router(images.router)
app.include_router(purchase.router)


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get_model():
    return {"status": "ok", "message": "This is head page!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)