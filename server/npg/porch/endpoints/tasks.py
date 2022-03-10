# Copyright (C) 2021, 2022 Genome Research Ltd.
#
# Author: Kieron Taylor kt19@sanger.ac.uk
# Author: Marina Gourtovaia mg8@sanger.ac.uk
#
# This file is part of npg_porch
#
# npg_porch is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from fastapi import APIRouter, HTTPException, Depends
from pydantic import PositiveInt
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from starlette import status

from npg.porch.models.pipeline import Pipeline
from npg.porch.models.task import Task
from npg.porchdb.connection import get_DbAccessor
from npg.porch.auth.token import validate


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not authorised"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected error"}
    }
)


@router.get(
    "/",
    response_model=List[Task],
    summary="Returns all tasks.",
    description="Return all tasks. A filter will be applied if used in the query."
)
async def get_tasks(
    db_accessor=Depends(get_DbAccessor),
    permissions=Depends(validate)
) -> List[Task]:

    return await db_accessor.get_tasks()


@router.post(
    "/",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Task creation was successful"},
        status.HTTP_404_NOT_FOUND: {"description": "The pipeline for this task is invalid"},
        status.HTTP_409_CONFLICT: {"description": "A task with the same signature already exists"}
    },
    summary="Creates one task record.",
    description='''
    Given a Task object, creates a database record for it and returns
    the same object, the response HTTP status is 201 'Created'. The
    new task is assigned pending status, ie becomes awailable for claiming.

    The pipeline specified by the `pipeline` attribute of the Task object
    should exist. If it does not exist, return status 404 'Not found'.'''
)
async def create_task(
    task: Task,
    db_accessor=Depends(get_DbAccessor),
    permissions=Depends(validate)
) -> Task:

    created_task = None
    try:
        created_task = await db_accessor.create_task(
            token_id=1,
            task=task
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail='Unable to create task, as another like it already exists'
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Failed to find pipeline for this task')

    return created_task


@router.put(
    "/",
    response_model=Task,
    responses={
        status.HTTP_200_OK: {"description": "Task was modified"},
        status.HTTP_404_NOT_FOUND: {
            "description": "The pipeline or task in the request is invalid"
        },
    },
    summary="Update one task.",
    description='''
    Given a Task object, updates the status of the task in the database
    to the value of the status in this Task object.

    The pipeline specified by the `pipeline` attribute of the Task object
    should exist. If it does not exist, return status 404 'Not found' and
    an error.'''
)
async def update_task(
    task: Task,
    db_accessor=Depends(get_DbAccessor),
    permissions=Depends(validate)
) -> Task:

    changed_task = None
    try:
        changed_task = await db_accessor.update_task(
            token_id=1,
            task=task
        )
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return changed_task


@router.post(
    "/claim",
    response_model=List[Task],
    responses={
        status.HTTP_200_OK: {"description": "Receive a list of tasks that have been claimed"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Cannot find the pipeline submitted with the claim"
        }
    },
    summary="Claim tasks for a particular pipeline.",
    description='''
    Arguments - the Pipeline object and the maximum number of tasks
    to retrieve and claim, the latter defaults to 1 if not given.

    Return an error and status 404 'Not Found' if the pipeline with the
    given name does not exist.

    It is possible that no tasks that satisfy the given criteria and
    are unclaimed are found. Return status 200 and an empty array.

    If any tasks are claimed, return an array of these Task objects and
    status 200.

    The pipeline object returned within the Task should be consistent
    with the pipeline object in the payload, but, typically, will have
    more attributes defined (uri, the specific version).'''
)
async def claim_task(
    pipeline: Pipeline,
    num_tasks: PositiveInt = 1,
    db_accessor=Depends(get_DbAccessor),
    permissions=Depends(validate)
) -> List[Task]:

    tasks = None
    try:
        tasks = await db_accessor.claim_tasks(
            token_id=1,
            pipeline=pipeline,
            claim_limit=num_tasks
        )
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.value)

    return tasks
