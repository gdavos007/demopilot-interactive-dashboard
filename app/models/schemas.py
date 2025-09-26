from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VoiceEvent(BaseModel):
    """VAPI voice event model"""
    type: str = Field(..., description="Event type (message, call-start, call-end, etc.)")
    content: Optional[str] = Field(None, description="Event content/message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")

class KnowledgeQuery(BaseModel):
    """Product knowledge query model"""
    query: str = Field(..., description="User query about the product")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for the query")

class KnowledgeResponse(BaseModel):
    """Product knowledge response model"""
    response: str = Field(..., description="Agent's response to the query")
    context: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Relevant context used for the response")
    confidence: float = Field(..., description="Confidence score of the response", ge=0.0, le=1.0)

class DemoSection(BaseModel):
    """Storylane demo section model"""
    id: str = Field(..., description="Section identifier")
    name: str = Field(..., description="Section name")
    description: str = Field(..., description="Section description")
    url: str = Field(..., description="Storylane URL for the section")

class DemoState(BaseModel):
    """Current demo state model"""
    current_section: str = Field(..., description="Current section ID")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Demo interaction history")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional demo state metadata") 