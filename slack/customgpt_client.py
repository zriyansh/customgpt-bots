"""
CustomGPT API Client for Slack Bot
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)

class CustomGPTClient:
    """Client for interacting with CustomGPT API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.CUSTOMGPT_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session:
            await self._session.close()
    
    async def create_conversation(self, project_id: str) -> Dict[str, Any]:
        """Create a new conversation"""
        url = f"{self.base_url}/projects/{project_id}/conversations"
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers) as response:
                if response.status == 201:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create conversation: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    async def send_message(
        self,
        project_id: str,
        session_id: Optional[str] = None,
        message: str = "",
        stream: bool = False,
        lang: str = "en",
        response_source: str = "default"
    ) -> Dict[str, Any]:
        """Send a message to CustomGPT"""
        
        # Create conversation if no session_id provided
        if not session_id:
            conversation = await self.create_conversation(project_id)
            session_id = conversation['session_id']
        
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}/messages"
        
        payload = {
            "prompt": message,
            "response_source": response_source,
            "stream": stream,
            "lang": lang
        }
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                elif response.status == 429:
                    raise Exception("Rate limit exceeded. Please try again later.")
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send message: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def send_message_openai_format(
        self,
        project_id: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        lang: str = "en",
        is_inline_citation: bool = False
    ) -> Dict[str, Any]:
        """Send a message in OpenAI format"""
        url = f"{self.base_url}/projects/{project_id}/chat/completions"
        
        payload = {
            "messages": messages,
            "stream": stream,
            "lang": lang,
            "is_inline_citation": is_inline_citation
        }
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send OpenAI format message: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error sending OpenAI format message: {str(e)}")
            raise
    
    async def get_agent_settings(self, project_id: str) -> Dict[str, Any]:
        """Get agent settings including starter questions"""
        url = f"{self.base_url}/projects/{project_id}/settings"
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get agent settings: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting agent settings: {str(e)}")
            raise
    
    async def get_agent_info(self, project_id: str) -> Dict[str, Any]:
        """Get agent information"""
        url = f"{self.base_url}/projects/{project_id}"
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get agent info: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting agent info: {str(e)}")
            raise
    
    async def get_citations(self, project_id: str, citation_id: str) -> Dict[str, Any]:
        """Get citation details"""
        url = f"{self.base_url}/projects/{project_id}/citations/{citation_id}"
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get citation: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting citation: {str(e)}")
            raise
    
    async def update_message_feedback(
        self,
        project_id: str,
        session_id: str,
        prompt_id: str,
        reaction: str
    ) -> Dict[str, Any]:
        """Update message feedback"""
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}/messages/{prompt_id}/feedback"
        
        payload = {"reaction": reaction}
        
        try:
            session = await self._get_session()
            async with session.put(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update feedback: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error updating feedback: {str(e)}")
            raise
    
    async def get_conversation_messages(
        self,
        project_id: str,
        session_id: str,
        page: int = 1,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """Get messages from a conversation"""
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}/messages"
        params = {"page": page, "order": order}
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get messages: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            raise