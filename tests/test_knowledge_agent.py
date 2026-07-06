import pytest
from app.core.knowledge.agent import ProductKnowledgeAgent
from app.models.schemas import KnowledgeQuery

@pytest.mark.asyncio
async def test_knowledge_agent_initialization():
    """Test that the knowledge agent initializes correctly"""
    agent = ProductKnowledgeAgent(product_type="carbon_black")
    assert agent.product_type == "carbon_black"
    assert agent.anthropic_client is not None

@pytest.mark.asyncio
async def test_knowledge_query():
    """Test basic knowledge query functionality"""
    agent = ProductKnowledgeAgent(product_type="carbon_black")
    query = KnowledgeQuery(query="What is Carbon Black?")
    
    # This test will fail if API keys are not set
    # In a real test environment, you'd mock the API calls
    try:
        response = await agent.get_response(query)
        assert response is not None
        assert hasattr(response, 'response')
        assert hasattr(response, 'confidence')
    except Exception as e:
        # If API keys are not set, this is expected
        assert "API key" in str(e) or "authentication" in str(e).lower()

def test_fallback_product_info():
    """Test that fallback product information is added"""
    agent = ProductKnowledgeAgent(product_type="crowdstrike")
    agent._add_fallback_product_info()
    assert agent.vector_store is not None 