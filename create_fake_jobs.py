# -*- coding: utf-8 -*-
import sys
from db.models.jobs import Job
from db.session import SessionLocal
from sqlalchemy.orm import Session
from db.models.users import User
"""
  id = Column(Integer,primary_key=True,index=True)
    title = Column(String(50),nullable=False)
    company = Column(String(50), nullable=False)
    company_url = Column(String(50))
    location = Column(String(50), nullable=False)
    description = Column(String(50), nullable=False)
    date_posted = Column(Date)
    is_active = Column(Boolean(), default=True)
    owner_id = Column(Integer,ForeignKey("user.id"))
    owner = relationship("User",back_populates="jobs")
"""


def create_fake_users(n,db:Session):

    """Generate fake users."""
    for i in range(n):
        title = f"test_title{i}"
        company = f"baidu{i}"
        company_url = "www.baidu.com"
        location = "beijing"
        description = "a"*20
        owner_id =1
        job = Job(title=title,company=company,company_url=company_url,location=location,description=description,owner_id=owner_id)
        db.add(job)
    db.commit()
    print(f'Added {n} fake users to the database.')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Pass the number of users you want to create as an argument.')
        #sys.exit(1)
        db = SessionLocal()
        create_fake_users(10,db)
