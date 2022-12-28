# -*- coding: utf-8 -*-
from fastapi import APIRouter
from apis.v1 import route_users
from apis.v1 import route_jobs
from apis.v1 import login
api_router = APIRouter()
api_router.include_router(route_users.router,prefix="/users",tags=["users"])
api_router.include_router(route_jobs.router,prefix="/jobs",tags=["jobs"])
api_router.include_router(login.router,prefix="/login",tags=["login"])