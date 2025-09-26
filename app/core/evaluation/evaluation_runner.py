"""
Evaluation Runner for Product Knowledge Agent

This module handles running evaluations against the Langsmith dataset
using LLM-as-Judge evaluators.
"""

import asyncio
from typing import Dict, Any, List, Optional
from langsmith import Client, evaluate
from langsmith.schemas import Dataset
from app.core.knowledge.agent import ProductKnowledgeAgent
from app.core.evaluation.evaluators import ProductKnowledgeEvaluator
from app.config.settings import settings
from app.config.langsmith_config import get_langsmith_dataset_id, get_langsmith_project
import logging

logger = logging.getLogger(__name__)

class EvaluationRunner:
    """Runs evaluations against the Product Knowledge Agent."""
    
    def __init__(self):
        """Initialize the evaluation runner."""
        self.client = Client(api_key=settings.LANGSMITH_API_KEY)
        self.agent = ProductKnowledgeAgent()
        self.evaluator = ProductKnowledgeEvaluator()
        self.dataset_id = get_langsmith_dataset_id()
        self.project_name = get_langsmith_project()
        
    async def initialize_agent(self):
        """Initialize the knowledge agent before evaluation."""
        logger.info("Initializing Product Knowledge Agent for evaluation...")
        await self.agent.initialize_agent()
        logger.info("Agent initialization complete")
    
    def get_dataset_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the evaluation dataset."""
        if not self.dataset_id:
            logger.error("No dataset ID configured")
            return None
            
        try:
            dataset = self.client.read_dataset(dataset_id=self.dataset_id)
            examples = list(self.client.list_examples(dataset_id=self.dataset_id))
            
            return {
                "dataset_id": self.dataset_id,
                "dataset_name": dataset.name,
                "description": dataset.description,
                "example_count": len(examples),
                "examples": examples[:5]  # Show first 5 examples
            }
        except Exception as e:
            logger.error(f"Error fetching dataset info: {e}")
            return None
    
    async def run_evaluation(
        self, 
        max_examples: Optional[int] = None,
        evaluators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run evaluation against the dataset.
        
        Args:
            max_examples: Maximum number of examples to evaluate (None for all)
            evaluators: List of evaluator names to run (None for all)
            
        Returns:
            Evaluation results
        """
        if not self.dataset_id:
            raise ValueError("No dataset ID configured")
        
        logger.info(f"Starting evaluation against dataset: {self.dataset_id}")
        
        # Get evaluators to run
        if evaluators is None:
            evaluators_to_run = self.evaluator.get_all_evaluators()
        else:
            evaluators_to_run = []
            if "helpfulness" in evaluators:
                evaluators_to_run.append(self.evaluator.create_helpfulness_evaluator())
            if "accuracy" in evaluators:
                evaluators_to_run.append(self.evaluator.create_accuracy_evaluator())
            if "relevance" in evaluators:
                evaluators_to_run.append(self.evaluator.create_relevance_evaluator())
        
        # Define the prediction function
        async def predict_example(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Generate prediction for a single example."""
            query = inputs.get("query", "")
            logger.info(f"Evaluating query: {query}")
            
            try:
                from app.models.schemas import KnowledgeQuery
                knowledge_query = KnowledgeQuery(query=query)
                response = await self.agent.get_response(knowledge_query)
                
                return {
                    "response": response.response,
                    "confidence": response.confidence,
                    "context_count": len(response.context)
                }
            except Exception as e:
                logger.error(f"Error generating prediction: {e}")
                return {
                    "response": f"Error: {str(e)}",
                    "confidence": 0.0,
                    "context_count": 0
                }
        
        # Run evaluation
        try:
            evaluation_result = await evaluate(
                lambda inputs: predict_example(inputs),
                data=self.dataset_id,
                evaluators=evaluators_to_run,
                max_examples=max_examples,
                project_name=f"{self.project_name}-evaluation" if self.project_name else None,
                experiment_prefix="product_knowledge_eval"
            )
            
            logger.info("Evaluation completed successfully")
            return {
                "status": "success",
                "evaluation_id": evaluation_result.get("id"),
                "project_name": evaluation_result.get("project_name"),
                "results": evaluation_result
            }
            
        except Exception as e:
            logger.error(f"Error running evaluation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_quick_evaluation(self, num_examples: int = 5) -> Dict[str, Any]:
        """Run a quick evaluation on a subset of examples."""
        logger.info(f"Running quick evaluation on {num_examples} examples")
        return await self.run_evaluation(max_examples=num_examples)
    
    async def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all examples in the dataset."""
        logger.info("Running full evaluation on all examples")
        return await self.run_evaluation()
    
    def get_evaluation_summary(self, evaluation_id: str) -> Dict[str, Any]:
        """Get summary of evaluation results."""
        try:
            # This would need to be implemented based on Langsmith's API
            # For now, return a placeholder
            return {
                "evaluation_id": evaluation_id,
                "status": "completed",
                "summary": "Evaluation results available in Langsmith dashboard"
            }
        except Exception as e:
            logger.error(f"Error getting evaluation summary: {e}")
            return {
                "evaluation_id": evaluation_id,
                "status": "error",
                "error": str(e)
            }
