import datetime
import os
from math import ceil

from PIL import Image
from fastapi import HTTPException, status, Depends
from peewee import fn, SQL, ModelSelect

from auth.hashing import get_password_hash
from config import IMAGE_DIR
from dataBase import (
    CoursesModel, ImageFormatModel, ImageCourseModel, ModuleModel,
    ImageModuleModel, UsersModel,
    ImageUserModel
)



