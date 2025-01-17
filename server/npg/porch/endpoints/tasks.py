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

from npg.porch.models.pipeline import Pipeline
from npg.porch.models.task import Task

from npg.porchdb.data_access import get_DbAccessor

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.get(
    "/",
    response_model=List[Task],
    summary="Returns all tasks.",
    description="Return all tasks. A filter will be applied if used in the query."
)
async def get_tasks(db_accessor=Depends(get_DbAccessor)):
    return await db_accessor.get_tasks()

#@router.get(
#    "/{task_name}",
#    response_model=Task,
#    summary="Get one task.",
#    description="Get one task using its unique name."
#)
#def get_task(task_name: str):
#    return Task(name=task_name)

@router.post(
    "/",
    response_model=Task,
    summary="Create one task."
)
async def create_task(task: Task, db_accessor=Depends(get_DbAccessor)):
    """
    Given a Task object, creats a database record for it and returns
    the same object with status 201 'Created'

    The pipeline specified by the `pipeline` attribute of the Task object
    should exist. If it does not exist, return status 404 'Not found' and
    an error.

    Errors if task status is not PENDING.
    """
    # Needs error handling when creating a clashing unique task
    return await db_accessor.create_task(agent_id=1, task=task)

@router.put(
    "/",
    response_model=Task,
    summary="Update one task."
)
async def update_task(task: Task, db_accessor=Depends(get_DbAccessor)):
    """
    Given a Task object, updates the status of the task in the database.

    The pipeline specified by the `pipeline` attribute of the Task object
    should exist. If it does not exist, return status 404 'Not found' and
    an error.
    """
    return await db_accessor.update_task(task)

@router.post(
    "/claim",
    response_model=List[Task],
    summary="Claim tasks.",
    description="Claim tasks for a particular pipeline."
)
async def claim_task(
    pipeline: Pipeline,
    num_tasks: PositiveInt=1,
    db_accessor=Depends(get_DbAccessor)
) -> List[Task]:
    """
    Arguments - the Pipeline object and the maximum number of tasks
    to retrieve and claim, the latter defaults to 1 if not given.

    Return an error and status 404 'Not Found' if the pipeline with the
    given name does not exist.

    Do not accept requests for non-current pipelines or their versions,
    check for the up-to-date db value. Return an error and status 406
    'Not acceptable' or 409 'Conflict'.

    If the version is specified as `latest`, retrieve tasks for
    the latest version, otherwise, retrieve tasks for the specified
    version.

    It is possible that no tasks that satisfy the given criteria and
    are unclaimed are found. Return status 200 and an empty array.

    If any tasks are claimed, return an array of these Task objects and
    status 200.
    """

    # The pipeline object returned within the Task should be consistent
    # with the pipeline object in the payload, but, typically, will have
    # more attributes defined (uri, the specific version).

    tasks = await db_accessor.claim_tasks(
        agent_id=1,
        pipeline=pipeline,
        claim_limit=num_tasks
    )
    return tasks
