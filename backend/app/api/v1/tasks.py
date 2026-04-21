from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.schemas import SSEEvent, TaskCreate, TaskOut, TaskStatusUpdate
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.services import event_manager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    task = Task(
        user_id=current_user.id,
        title=body.title,
        description=body.description,
        status=TaskStatus.todo,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    return list(result.scalars().all())


@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    # Validate status value
    try:
        new_status = TaskStatus(body.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status '{body.status}'. Must be one of: todo, in_progress, done",
        )

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = new_status
    await db.commit()
    await db.refresh(task)

    # Publish SSE notification when task is marked done
    if new_status == TaskStatus.done:
        await event_manager.publish(
            current_user.id,
            SSEEvent(
                type="task_done",
                data={"task_id": task.id, "title": task.title},
            ),
        )

    return task
