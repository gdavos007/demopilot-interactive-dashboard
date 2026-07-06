# Langsmith Evaluation Guide

This guide explains how to use the LLM observability and evaluation framework implemented for the Product Knowledge Agent.

## Overview

The system implements comprehensive LLM observability using Langsmith with:
- **Tracing**: Automatic tracing of all Claude API calls with detailed metrics
- **LLM-as-Judge Evaluation**: Automated evaluation using Claude as a judge
- **Three Evaluation Criteria**: Helpfulness, Accuracy, and Relevance
- **Dataset Integration**: Uses your uploaded 27-question dataset

## Setup

### 1. Environment Variables

Ensure these environment variables are set in your `.env` file:

```bash
# Langsmith Configuration
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXX
LANGSMITH_PROJECT=pr-product-knowledge-25
LANGSMITH_DATASET_ID=XXXXXXXXXXXXXXXXXXXXX
```

### 2. Dependencies

The required dependencies are already installed:
- `langchain-anthropic>=0.1.0`
- `langsmith>=0.1.0`

## Features

### 1. Automatic Tracing

All Claude API calls are automatically traced with:
- **Input prompts** and user queries
- **Claude's responses** and token usage
- **Latency metrics** and performance data
- **Error tracking** and exception handling
- **Context retrieval** information

### 2. LLM-as-Judge Evaluation

The system uses Claude Haiku as a judge to evaluate responses on three criteria:

#### Helpfulness (1-5 scale)
- **5**: Excellent - Response directly and completely answers the question
- **4**: Good - Response mostly answers with relevant information
- **3**: Fair - Response partially answers but lacks detail
- **2**: Poor - Response tangentially related but doesn't address the question
- **1**: Very Poor - Response doesn't help answer the question

#### Accuracy (1-5 scale)
- **5**: Excellent - All information is accurate and verifiable
- **4**: Good - Most information is accurate with minor inaccuracies
- **3**: Fair - Some accurate information but contains notable errors
- **2**: Poor - Contains significant factual errors
- **1**: Very Poor - Mostly or entirely inaccurate information

#### Relevance (1-5 scale)
- **5**: Excellent - Response directly addresses the question
- **4**: Good - Response mostly stays on topic
- **3**: Fair - Response somewhat relevant but includes off-topic information
- **2**: Poor - Response partially off-topic
- **1**: Very Poor - Response is largely irrelevant

## Usage

### 1. API Endpoints

The evaluation system provides several API endpoints:

#### Check Status
```bash
GET /api/v1/evaluation/status
```

#### Get Dataset Information
```bash
GET /api/v1/evaluation/dataset-info
```

#### Run Quick Evaluation (5 examples)
```bash
POST /api/v1/evaluation/run-quick
```

#### Run Full Evaluation
```bash
POST /api/v1/evaluation/run
{
  "max_examples": 10,
  "evaluators": ["helpfulness", "accuracy", "relevance"]
}
```

#### Get Evaluation Summary
```bash
GET /api/v1/evaluation/summary/{evaluation_id}
```

### 2. CLI Script

Use the command-line script for evaluations:

```bash
# Show dataset information
python run_evaluation.py --dataset-info

# Run quick evaluation (5 examples)
python run_evaluation.py --quick

# Run full evaluation
python run_evaluation.py

# Run evaluation on specific number of examples
python run_evaluation.py --max-examples 10

# Run specific evaluators only
python run_evaluation.py --evaluators helpfulness accuracy
```

### 3. Programmatic Usage

```python
from app.core.evaluation.evaluation_runner import EvaluationRunner

# Initialize runner
runner = EvaluationRunner()

# Initialize agent
await runner.initialize_agent()

# Run evaluation
result = await runner.run_evaluation(max_examples=10)

# Check results
if result["status"] == "success":
    print(f"Evaluation ID: {result['evaluation_id']}")
    print(f"Project: {result['project_name']}")
```

## Monitoring Dashboard

### 1. Langsmith Dashboard

Access your Langsmith dashboard to view:
- **Traces**: All API calls with detailed metrics
- **Evaluations**: Results from LLM-as-Judge evaluations
- **Performance**: Latency, token usage, and error rates
- **Trends**: Performance over time

### 2. Key Metrics to Monitor

- **Response Quality**: Average scores for helpfulness, accuracy, relevance
- **Token Usage**: Cost tracking for both main model and judge model
- **Latency**: Response times for different query types
- **Error Rates**: Failed requests and exceptions
- **Context Retrieval**: Success rate of finding relevant documentation

## Interpreting Results

### 1. Evaluation Scores

- **Pass Threshold**: Score ≥ 4 (Good or Excellent)
- **Overall Performance**: Average of all three criteria
- **Trend Analysis**: Track improvements over time

### 2. Common Issues

- **Low Helpfulness**: Agent not finding relevant context
- **Low Accuracy**: Outdated or incorrect information in knowledge base
- **Low Relevance**: Agent going off-topic or not addressing the question

### 3. Action Items

Based on evaluation results:
- **Update Knowledge Base**: Add missing documentation
- **Improve Context Retrieval**: Adjust similarity search parameters
- **Refine Prompts**: Update system prompts for better responses
- **Monitor Performance**: Set up alerts for score degradation

## Troubleshooting

### 1. Common Issues

#### Tracing Not Working
- Check `LANGSMITH_TRACING=true`
- Verify `LANGSMITH_API_KEY` is correct
- Ensure `LANGSMITH_PROJECT` is set

#### Evaluation Fails
- Verify `LANGSMITH_DATASET_ID` is correct
- Check dataset has examples with "query" in inputs
- Ensure agent initialization completes successfully

#### Low Scores
- Check if knowledge base is properly initialized
- Verify documentation is being retrieved
- Review system prompts and context formatting

### 2. Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger("app").setLevel(logging.DEBUG)
```

## Best Practices

### 1. Regular Evaluations
- Run evaluations after knowledge base updates
- Monitor performance trends over time
- Set up automated evaluation runs

### 2. Score Interpretation
- Focus on trends rather than individual scores
- Consider context when interpreting low scores
- Use evaluation feedback to improve the system

### 3. Cost Management
- Use Claude Haiku for judge evaluations (cost-effective)
- Monitor token usage in Langsmith dashboard
- Set up alerts for unusual usage patterns

## Next Steps

1. **Run Initial Evaluation**: Test the system with your 27-question dataset
2. **Monitor Performance**: Set up regular evaluation runs
3. **Iterate and Improve**: Use results to enhance the knowledge base
4. **Scale Up**: Expand evaluation criteria as needed

For more information, visit the [Langsmith Documentation](https://docs.langchain.com/langsmith/).
