"""
API endpoints for the CrewAI coordination.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.coordinator.crew_manager import CrewManager

router = APIRouter()

# Initialize the CrewManager
crew_manager = CrewManager()

# Pydantic models for request/response
class TaskRequest(BaseModel):
    """Request model for task planning and execution."""
    task_description: str
    context: Optional[Dict[str, Any]] = None

class PlanRequest(BaseModel):
    """Request model for executing a plan."""
    plan: str
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    """Response model for task results."""
    plan: Optional[str] = None
    execution: Optional[str] = None
    status: str = "completed"
    message: str = "Task processed successfully"

class TaskStatus(BaseModel):
    """Model for task status updates."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

# Task storage (in-memory for simplicity, would use a database in production)
task_results = {}

@router.post("/plan", response_model=TaskResponse)
async def plan_task(request: TaskRequest):
    """
    Plan a task using the Planner agent.
    """
    try:
        result = crew_manager.plan_task(
            task_description=request.task_description,
            context=request.context
        )
        return TaskResponse(
            plan=result["plan"],
            status="completed",
            message="Planning completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error planning task: {str(e)}"
        )

@router.post("/execute", response_model=TaskResponse)
async def execute_plan(request: PlanRequest):
    """
    Execute a plan using the Executor agent.
    """
    try:
        result = crew_manager.execute_task(
            plan=request.plan,
            context=request.context
        )
        return TaskResponse(
            execution=result["execution"],
            status="completed",
            message="Execution completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing plan: {str(e)}"
        )

@router.post("/process", response_model=TaskResponse)
async def process_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Process a task through both planning and execution stages.
    This endpoint runs the processing in the background.
    """
    # Generate a unique task ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # Store initial status
    task_results[task_id] = {
        "status": "processing",
        "result": None
    }
    
    # Define the background task
    def process_in_background(
        task_id: str,
        task_description: str,
        context: Dict[str, Any]
    ):
        try:
            result = crew_manager.run_full_process(
                task_description=task_description,
                context=context
            )
            # Update task status
            task_results[task_id] = {
                "status": "completed",
                "result": result
            }
        except Exception as e:
            # Update with error
            task_results[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Add the task to background tasks
    background_tasks.add_task(
        process_in_background,
        task_id,
        request.task_description,
        request.context or {}
    )
    
    # Return the task ID for status checking
    return TaskResponse(
        status="processing",
        message=f"Task processing started with ID: {task_id}"
    )

@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    Check the status of a background task.
    """
    if task_id not in task_results:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )
    
    task_data = task_results[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        result=task_data.get("result")
    ) 