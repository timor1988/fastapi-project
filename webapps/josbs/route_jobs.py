# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter
from fastapi import Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from db.respository.jobs import list_jobs, retreive_job,search_job
from db.session import get_db

from db.models.users import User
from apis.v1.login import get_current_user_from_token
from webapps.josbs.forms import JobCreateForm
from schemas.jobs import JobCreate
from db.respository.jobs import create_new_job
from fastapi import responses, status
from fastapi.security.utils import get_authorization_scheme_param

templates = Jinja2Templates(directory="templates")
# It is not an API, It does not makes much sense to see the result of this router in the OpenAPI documentation
router = APIRouter(include_in_schema=False)
from starlette.datastructures import URL
templates.env.globals["URL"] = URL

class Pagination():

    def __init__(self,items,has_prev=False,prev_num=0,has_next=True,next_num=2,page=0):
        self._items = items
        self._has_prev = has_prev
        self._prev_num = prev_num
        self._has_next = has_next
        self._next_num = next_num
        self._page = page

    @property
    def has_prev(self):
        return self._has_prev

    @property
    def items(self):
        return self._items

    @property
    def prev_num(self):
        return self._prev_num

    @property
    def has_next(self):
        return self._has_next

    @property
    def next_num(self):
        return self._next_num

    @property
    def page(self):
        return self._page

@router.get("/")
async def home(request: Request,db: Session = Depends(get_db),msg:str=None):
    jobs = list_jobs(db=db,limit=10,page=1)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request,"jobs":jobs,"msg":msg}
    )

@router.get("/details/{id}")
def job_detail(id:int,request: Request,db:Session = Depends(get_db)):
    job = retreive_job(id=id, db=db)
    return templates.TemplateResponse(
        "jobs/detail.html", {"request": request,"job":job}
    )

@router.get("/post-a-job/")
def create_job(request:Request,db:Session=Depends(get_db)):
    return templates.TemplateResponse("jobs/create_job.html",{"request": request})

@router.post("/post-a-job/")
async def create_job(request:Request,db:Session=Depends(get_db),
                     current_user:User = Depends(get_current_user_from_token)):
    form = JobCreateForm(request)
    await form.load_data()
    print(form)
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_user: User = get_current_user_from_token(token=param, db=db)
            job = JobCreate(**form.__dict__)
            job = create_new_job(job=job, db=db, owner_id=current_user.id)
            print(job)
            return responses.RedirectResponse(
                f"/details/{job.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            print(form)
            return templates.TemplateResponse("jobs/create_job.html", form.__dict__)
    return templates.TemplateResponse("jobs/create_job.html", form.__dict__)

@router.get("/delete-job")
def show_jobs_to_delete(request:Request,db:Session=Depends(get_db),
                        limit:int=10,page:int=1):
    jobs = list_jobs(db,limit,page)
    if page==1:
        has_prev=False
    else:
        has_prev = True
    data = Pagination(items=jobs,has_prev=has_prev,prev_num=page-1,has_next=True,next_num=page+1,page=page)
    return templates.TemplateResponse(
        "jobs/show_jobs_to_delete.html", {"request": request, "jobs": data}
    )

@router.get("/search/")
def search(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):
    jobs = search_job(query,db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "jobs": jobs}
    )