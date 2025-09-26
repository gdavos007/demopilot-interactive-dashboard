#!/usr/bin/env python3
"""
Evaluation CLI Script

This script provides a command-line interface for running evaluations
against the Product Knowledge Agent using Langsmith.
"""

import asyncio
import argparse
import sys
from typing import Optional, List
from app.core.evaluation.evaluation_runner import EvaluationRunner
from app.config.langsmith_config import is_langsmith_enabled
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Run Product Knowledge Agent evaluations")
    
    parser.add_argument(
        "--max-examples",
        type=int,
        help="Maximum number of examples to evaluate (default: all)"
    )
    
    parser.add_argument(
        "--evaluators",
        nargs="+",
        choices=["helpfulness", "accuracy", "relevance"],
        help="Specific evaluators to run (default: all)"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick evaluation on 5 examples"
    )
    
    parser.add_argument(
        "--dataset-info",
        action="store_true",
        help="Show dataset information only"
    )
    
    args = parser.parse_args()
    
    # Check if Langsmith is enabled
    if not is_langsmith_enabled():
        logger.error("Langsmith tracing is not enabled or configured")
        logger.error("Please check your environment variables:")
        logger.error("- LANGSMITH_TRACING=true")
        logger.error("- LANGSMITH_API_KEY")
        logger.error("- LANGSMITH_PROJECT")
        logger.error("- LANGSMITH_DATASET_ID")
        sys.exit(1)
    
    try:
        runner = EvaluationRunner()
        
        # Show dataset info if requested
        if args.dataset_info:
            dataset_info = runner.get_dataset_info()
            if dataset_info:
                print("\n=== Dataset Information ===")
                print(f"Dataset ID: {dataset_info['dataset_id']}")
                print(f"Dataset Name: {dataset_info['dataset_name']}")
                print(f"Description: {dataset_info['description']}")
                print(f"Example Count: {dataset_info['example_count']}")
                print("\n=== Sample Examples ===")
                for i, example in enumerate(dataset_info['examples'], 1):
                    print(f"{i}. {example.inputs.get('query', 'No query')}")
            else:
                logger.error("Could not retrieve dataset information")
                sys.exit(1)
            return
        
        # Initialize agent
        logger.info("Initializing Product Knowledge Agent...")
        await runner.initialize_agent()
        logger.info("Agent initialization complete")
        
        # Run evaluation
        if args.quick:
            logger.info("Running quick evaluation (5 examples)...")
            result = await runner.run_quick_evaluation()
        else:
            logger.info("Running evaluation...")
            result = await runner.run_evaluation(
                max_examples=args.max_examples,
                evaluators=args.evaluators
            )
        
        # Display results
        if result["status"] == "success":
            print("\n=== Evaluation Results ===")
            print(f"Status: {result['status']}")
            print(f"Evaluation ID: {result.get('evaluation_id', 'N/A')}")
            print(f"Project: {result.get('project_name', 'N/A')}")
            print("\nEvaluation completed successfully!")
            print("Check the Langsmith dashboard for detailed results.")
        else:
            logger.error(f"Evaluation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
