from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import VoiceEvent
from app.core.voice.vapi_client import vapi_client
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook", response_model=Dict[str, Any])
async def handle_voice_webhook(event: VoiceEvent):
    """
    Handle incoming voice events from VAPI
    
    Args:
        event: VoiceEvent object containing event details
        
    Returns:
        Dict containing response and metadata
    """
    logger.info("Received voice webhook event: %s", event.type)
    try:
        response = await vapi_client.handle_voice_event(event)
        logger.info("Voice webhook response: %s", response.get('type'))
        return response
    except Exception as e:
        logger.error("Error in voice webhook: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speak", response_model=Dict[str, Any])
async def speak_text(text: str):
    """
    Convert text to speech using VAPI
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Dict containing response and metadata
    """
    try:
        response = await vapi_client.speak(text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 