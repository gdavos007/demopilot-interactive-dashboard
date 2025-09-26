"""
Evaluation API Routes

This module provides API endpoints for running evaluations
against the Product Knowledge Agent.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.evaluation.evaluation_runner import EvaluationRunner
from app.config.langsmith_config import is_langsmith_enabled
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class EvaluationRequest(BaseModel):
    """Request model for running evaluations."""
    max_examples: Optional[int] = None
    evaluators: Optional[List[str]] = None  # ["helpfulness", "accuracy", "relevance"]

class EvaluationResponse(BaseModel):
    """Response model for evaluation results."""
    status: str
    evaluation_id: Optional[str] = None
    project_name: Optional[str] = None
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.get("/status")
async def get_evaluation_status():
    """Get the status of the evaluation system."""
    if not is_langsmith_enabled():
        return {
            "status": "disabled",
            "message": "Langsmith tracing is not enabled or configured"
        }
    
    try:
        runner = EvaluationRunner()
        dataset_info = runner.get_dataset_info()
        
        if dataset_info:
            return {
                "status": "ready",
                "message": "Evaluation system is ready",
                "dataset_info": dataset_info
            }
        else:
            return {
                "status": "error",
                "message": "Could not access evaluation dataset"
            }
    except Exception as e:
        logger.error(f"Error checking evaluation status: {e}")
        return {
            "status": "error",
            "message": f"Error checking evaluation status: {str(e)}"
        }

@router.post("/run", response_model=EvaluationResponse)
async def run_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks
):
    """Run evaluation against the dataset."""
    if not is_langsmith_enabled():
        raise HTTPException(
            status_code=400,
            detail="Langsmith tracing is not enabled or configured"
        )
    
    try:
        runner = EvaluationRunner()
        
        # Initialize agent
        await runner.initialize_agent()
        
        # Run evaluation
        result = await runner.run_evaluation(
            max_examples=request.max_examples,
            evaluators=request.evaluators
        )
        
        if result["status"] == "success":
            return EvaluationResponse(
                status="success",
                evaluation_id=result.get("evaluation_id"),
                project_name=result.get("project_name"),
                message="Evaluation completed successfully",
                results=result.get("results")
            )
        else:
            return EvaluationResponse(
                status="error",
                message="Evaluation failed",
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running evaluation: {str(e)}"
        )

@router.post("/run-quick", response_model=EvaluationResponse)
async def run_quick_evaluation():
    """Run a quick evaluation on 5 examples."""
    if not is_langsmith_enabled():
        raise HTTPException(
            status_code=400,
            detail="Langsmith tracing is not enabled or configured"
        )
    
    try:
        runner = EvaluationRunner()
        
        # Initialize agent
        await runner.initialize_agent()
        
        # Run quick evaluation
        result = await runner.run_quick_evaluation()
        
        if result["status"] == "success":
            return EvaluationResponse(
                status="success",
                evaluation_id=result.get("evaluation_id"),
                project_name=result.get("project_name"),
                message="Quick evaluation completed successfully",
                results=result.get("results")
            )
        else:
            return EvaluationResponse(
                status="error",
                message="Quick evaluation failed",
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Error running quick evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running quick evaluation: {str(e)}"
        )

@router.get("/dataset-info")
async def get_dataset_info():
    """Get information about the evaluation dataset."""
    if not is_langsmith_enabled():
        raise HTTPException(
            status_code=400,
            detail="Langsmith tracing is not enabled or configured"
        )
    
    try:
        runner = EvaluationRunner()
        dataset_info = runner.get_dataset_info()
        
        if dataset_info:
            return {
                "status": "success",
                "dataset_info": dataset_info
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Could not access evaluation dataset"
            )
            
    except Exception as e:
        logger.error(f"Error getting dataset info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dataset info: {str(e)}"
        )

@router.get("/summary/{evaluation_id}")
async def get_evaluation_summary(evaluation_id: str):
    """Get summary of evaluation results."""
    if not is_langsmith_enabled():
        raise HTTPException(
            status_code=400,
            detail="Langsmith tracing is not enabled or configured"
        )
    
    try:
        runner = EvaluationRunner()
        summary = runner.get_evaluation_summary(evaluation_id)
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting evaluation summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting evaluation summary: {str(e)}"
        )
