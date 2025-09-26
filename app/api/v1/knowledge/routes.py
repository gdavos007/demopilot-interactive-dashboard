from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import KnowledgeQuery, KnowledgeResponse
from app.core.knowledge.agent import knowledge_agent
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=KnowledgeResponse)
async def query_knowledge(query: KnowledgeQuery):
    """
    Query the product knowledge agent
    
    Args:
        query: KnowledgeQuery object containing the user query
        
    Returns:
        KnowledgeResponse object with the agent's response
    """
    logger.info("Received knowledge query: %s", query.query)
    try:
        response = await knowledge_agent.get_response(query)
        logger.info("Responding with: %s", response.response[:100])  # Log first 100 chars
        return response
    except Exception as e:
        logger.error("Error in knowledge query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/{query}")
async def get_context(query: str, k: int = Query(default=4, ge=1, le=10)):
    """
    Get relevant context for a query without generating a response
    
    Args:
        query: User query
        k: Number of relevant documents to retrieve
        
    Returns:
        List of relevant documents with metadata
    """
    try:
        context = knowledge_agent.query_knowledge_base(query, k=k)
        return {
            "query": query,
            "context": context,
            "count": len(context)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-documentation")
async def add_documentation(url: str):
    """
    Add additional documentation to the knowledge base
    
    Args:
        url: URL of the documentation to add
        
    Returns:
        Success status and metadata
    """
    try:
        success = await knowledge_agent.add_documentation(url)
        return {
            "success": success,
            "url": url,
            "message": "Documentation added successfully" if success else "Failed to add documentation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agent_status():
    """
    Get the current status of the knowledge agent
    
    Returns:
        Agent status information
    """
    try:
        return {
            "product_type": knowledge_agent.product_type,
            "vector_store_initialized": knowledge_agent.vector_store is not None,
            "processed_urls_count": len(knowledge_agent.processed_urls),
            "processed_urls": list(knowledge_agent.processed_urls)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 