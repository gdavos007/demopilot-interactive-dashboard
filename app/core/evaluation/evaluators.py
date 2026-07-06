"""
LLM-as-Judge Evaluation Framework

This module implements LLM-as-Judge evaluators for the Product Knowledge Agent
using Langsmith evaluation framework.
"""

from typing import Dict, Any, List, Callable
from langsmith.schemas import Run, Example
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

EvaluatorFn = Callable[[Run, Example], Dict[str, Any]]

class ProductKnowledgeEvaluator:
    """LLM-as-Judge evaluator for Product Knowledge Agent responses."""
    
    def __init__(self):
        """Initialize the evaluator with Claude as the judge."""
        self.judge_model = ChatAnthropic(
            model="claude-haiku-4-5-20251001",  # Use Haiku for cost efficiency
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.1,
            max_tokens=500
        )
        
    def create_helpfulness_evaluator(self) -> EvaluatorFn:
        """Create an evaluator for response helpfulness."""
        
        helpfulness_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the helpfulness of AI responses to product knowledge questions.

Your task is to evaluate whether the response directly helps answer the user's question.

Scoring Rubric:
- 5: Excellent - Response directly and completely answers the question with specific, actionable information
- 4: Good - Response mostly answers the question with relevant information, minor gaps
- 3: Fair - Response partially answers the question but lacks detail or misses some aspects
- 2: Poor - Response tangentially related but doesn't directly address the question
- 1: Very Poor - Response doesn't help answer the question at all

Consider:
- Does the response directly address what was asked?
- Is the information specific and actionable?
- Does it provide enough detail to be useful?
- Is it clear and well-structured?

Provide your score (1-5) and a brief explanation of your reasoning."""),
            ("human", """Question: {input}
Response: {prediction}

Score the helpfulness of this response (1-5) and explain your reasoning.""")
        ])
        
        def helpfulness_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate response helpfulness."""
            try:
                chain = helpfulness_prompt | self.judge_model
                result = chain.invoke({
                    "input": example.inputs.get("query", ""),
                    "prediction": run.outputs.get("response", "")
                })
                
                # Parse score from response
                response_text = result.content.lower()
                score = 3  # Default score
                
                if "5" in response_text or "excellent" in response_text:
                    score = 5
                elif "4" in response_text or "good" in response_text:
                    score = 4
                elif "2" in response_text or "poor" in response_text:
                    score = 2
                elif "1" in response_text or "very poor" in response_text:
                    score = 1
                
                return {
                    "key": "helpfulness",
                    "score": score,
                    "reasoning": result.content,
                    "value": score >= 4  # Pass if score >= 4
                }
                
            except Exception as e:
                logger.error(f"Error in helpfulness evaluation: {e}")
                return {
                    "key": "helpfulness",
                    "score": 0,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "value": False
                }
        
        return helpfulness_evaluator
    
    def create_accuracy_evaluator(self) -> EvaluatorFn:
        """Create an evaluator for response accuracy."""
        
        accuracy_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the factual accuracy of AI responses about cybersecurity products.

Your task is to evaluate whether the information provided is factually correct and reliable.

Scoring Rubric:
- 5: Excellent - All information is accurate, specific, and verifiable
- 4: Good - Most information is accurate with minor inaccuracies
- 3: Fair - Some accurate information but contains notable errors or outdated info
- 2: Poor - Contains significant factual errors or misleading information
- 1: Very Poor - Mostly or entirely inaccurate information

Consider:
- Are the product names, features, and capabilities correct?
- Are technical details accurate?
- Is the information current and up-to-date?
- Are there any misleading claims?

Provide your score (1-5) and a brief explanation of your reasoning."""),
            ("human", """Question: {input}
Response: {prediction}

Score the accuracy of this response (1-5) and explain your reasoning.""")
        ])
        
        def accuracy_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate response accuracy."""
            try:
                chain = accuracy_prompt | self.judge_model
                result = chain.invoke({
                    "input": example.inputs.get("query", ""),
                    "prediction": run.outputs.get("response", "")
                })
                
                # Parse score from response
                response_text = result.content.lower()
                score = 3  # Default score
                
                if "5" in response_text or "excellent" in response_text:
                    score = 5
                elif "4" in response_text or "good" in response_text:
                    score = 4
                elif "2" in response_text or "poor" in response_text:
                    score = 2
                elif "1" in response_text or "very poor" in response_text:
                    score = 1
                
                return {
                    "key": "accuracy",
                    "score": score,
                    "reasoning": result.content,
                    "value": score >= 4  # Pass if score >= 4
                }
                
            except Exception as e:
                logger.error(f"Error in accuracy evaluation: {e}")
                return {
                    "key": "accuracy",
                    "score": 0,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "value": False
                }
        
        return accuracy_evaluator
    
    def create_relevance_evaluator(self) -> EvaluatorFn:
        """Create an evaluator for response relevance."""
        
        relevance_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the relevance of AI responses to user questions.

Your task is to evaluate whether the response stays on-topic and addresses what was actually asked.

Scoring Rubric:
- 5: Excellent - Response directly addresses the question with highly relevant information
- 4: Good - Response mostly stays on topic with minor tangents
- 3: Fair - Response somewhat relevant but includes off-topic information
- 2: Poor - Response partially off-topic or doesn't address the main question
- 1: Very Poor - Response is largely irrelevant to the question asked

Consider:
- Does the response address the specific question asked?
- Is the information directly related to the topic?
- Are there unnecessary tangents or off-topic information?
- Does it stay focused on what was requested?

Provide your score (1-5) and a brief explanation of your reasoning."""),
            ("human", """Question: {input}
Response: {prediction}

Score the relevance of this response (1-5) and explain your reasoning.""")
        ])
        
        def relevance_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate response relevance."""
            try:
                chain = relevance_prompt | self.judge_model
                result = chain.invoke({
                    "input": example.inputs.get("query", ""),
                    "prediction": run.outputs.get("response", "")
                })
                
                # Parse score from response
                response_text = result.content.lower()
                score = 3  # Default score
                
                if "5" in response_text or "excellent" in response_text:
                    score = 5
                elif "4" in response_text or "good" in response_text:
                    score = 4
                elif "2" in response_text or "poor" in response_text:
                    score = 2
                elif "1" in response_text or "very poor" in response_text:
                    score = 1
                
                return {
                    "key": "relevance",
                    "score": score,
                    "reasoning": result.content,
                    "value": score >= 4  # Pass if score >= 4
                }
                
            except Exception as e:
                logger.error(f"Error in relevance evaluation: {e}")
                return {
                    "key": "relevance",
                    "score": 0,
                    "reasoning": f"Evaluation error: {str(e)}",
                    "value": False
                }
        
        return relevance_evaluator
    
    def get_all_evaluators(self) -> List[EvaluatorFn]:
        """Get all evaluators for comprehensive assessment."""
        return [
            self.create_helpfulness_evaluator(),
            self.create_accuracy_evaluator(),
            self.create_relevance_evaluator()
        ]
