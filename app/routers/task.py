from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app import models, oauth2, schemas
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(tags=["Tasks"], prefix="/tasks")


# Getting my tasks
@router.get("/my", response_model=List[schemas.Task])
def get_my_tasks(
    user_data: schemas.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        task_query = db.query(models.Task).filter(
            models.Task.owner_id == str(user_data.id)
        )
        db_tasks = task_query.all()

        if not db_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tasks found.",
            )

        return db_tasks

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + str(e),
        )


# Creating new task
@router.post("/create", response_model=schemas.Task)
def create_tasks(
    new_task: schemas.TaskCreate,
    user_data: schemas.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_task.owner_id = str(user_data.id)
        db_task = models.Task(**new_task.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        return db_task

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong: " + str(e),
        )
