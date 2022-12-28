# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from schemas.jobs import JobCreate
from db.models.jobs import Job


def create_new_job(job: JobCreate, db: Session, owner_id: int):
    job_object = Job(**job.dict(), owner_id=owner_id)
    db.add(job_object)
    db.commit()
    db.refresh(job_object)
    return job_object


def retreive_job(id: int, db: Session):
    item = db.query(Job).filter(Job.id == id).first()
    return item

def list_jobs(db : Session,limit:int,page:int):    #new
    skip = (page-1)*limit
    jobs = db.query(Job).filter(Job.is_active == True).limit(limit).offset(skip).all()
    return jobs

def update_job_by_id(id:int,job:JobCreate,db:Session,owner_id):
    one_job = db.query(Job).filter(Job.id==id)
    if not one_job.first():
        return 0
    job.__dict__.update(owner_id=owner_id)
    one_job.update(job.__dict__)
    db.commit()
    return 1

def delete_job_by_id(id:int,db:Session,owner_id):
    one_job = db.query(Job).filter(Job.id==id)
    if not one_job:
        return 0
    one_job.delete(synchronize_session=False) # 加上'synchronize_session=False'这样就是不删除关联的实体，只删除本身
    db.commit()
    return 1

def search_job(query: str, db: Session):
    jobs = db.query(Job).filter(Job.title.contains(query))
    return jobs