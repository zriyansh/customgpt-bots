"""
CustomGPT API Client for Microsoft Teams Bot
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime, timezone

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
            'Accept': 'application/json',
            'User-Agent': 'CustomGPT-Teams-Bot/1.0'
        }
        self._session: Optional[aiohttp.ClientSession] = None
        self._usage_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes cache for usage data
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self._session or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=Config.RESPONSE_TIMEOUT)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self._session
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def create_conversation(self, project_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new conversation with optional metadata"""
        url = f"{self.base_url}/projects/{project_id}/conversations"
        
        payload = {}
        if metadata:
            payload['metadata'] = metadata
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    logger.info(f"Created conversation: {data['data']['session_id']}")
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create conversation: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
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
        response_source: str = "default",
        user_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send a message to CustomGPT"""
        
        # Create conversation if no session_id provided
        if not session_id:
            metadata = {'source': 'teams', 'user_info': user_info} if user_info else {'source': 'teams'}
            conversation = await self.create_conversation(project_id, metadata)
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
                    logger.info(f"Message sent successfully to session {session_id}")
                    return data['data']
                elif response.status == 429:
                    retry_after = response.headers.get('Retry-After', '60')
                    raise Exception(f"Rate limit exceeded. Please try again after {retry_after} seconds.")
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send message: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def send_message_stream(
        self,
        project_id: str,
        session_id: Optional[str] = None,
        message: str = "",
        lang: str = "en",
        response_source: str = "default",
        user_info: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """Send a message and stream the response"""
        
        # Create conversation if no session_id provided
        if not session_id:
            metadata = {'source': 'teams', 'user_info': user_info} if user_info else {'source': 'teams'}
            conversation = await self.create_conversation(project_id, metadata)
            session_id = conversation['session_id']
        
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}/messages"
        
        payload = {
            "prompt": message,
            "response_source": response_source,
            "stream": True,
            "lang": lang
        }
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]
                                if data_str == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and data['choices']:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            yield delta['content']
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse streaming data: {data_str}")
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send streaming message: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error in streaming message: {str(e)}")
            raise
    
    async def send_message_openai_format(
        self,
        project_id: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        lang: str = "en",
        is_inline_citation: bool = False,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message in OpenAI format"""
        url = f"{self.base_url}/projects/{project_id}/chat/completions"
        
        payload = {
            "messages": messages,
            "stream": stream,
            "lang": lang,
            "is_inline_citation": is_inline_citation
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        try:
            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("OpenAI format message sent successfully")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send OpenAI format message: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
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
                    logger.info(f"Retrieved agent settings for project {project_id}")
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get agent settings: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
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
                    logger.info(f"Retrieved agent info for project {project_id}")
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get agent info: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error getting agent info: {str(e)}")
            raise
    
    async def get_usage_limits(self) -> Dict[str, Any]:
        """Get user's usage limits and current usage"""
        # Check cache first
        now = datetime.now(timezone.utc)
        if self._cache_timestamp and self._usage_cache:
            cache_age = (now - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl:
                return self._usage_cache
        
        url = f"{self.base_url}/limits/usage"
        
        try:
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self._usage_cache = data['data']
                    self._cache_timestamp = now
                    logger.info("Retrieved usage limits")
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get usage limits: {response.status} - {error_text}")
                    # Return empty dict on error to not break rate limiting
                    return {}
        except Exception as e:
            logger.error(f"Error getting usage limits: {str(e)}")
            return {}
    
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
                    raise Exception(f"API Error: {response.status} - {error_text}")
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
        """Update message feedback (thumbs up/down)"""
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}/messages/{prompt_id}/feedback"
        
        payload = {"reaction": reaction}
        
        try:
            session = await self._get_session()
            async with session.put(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Updated feedback for message {prompt_id}: {reaction}")
                    return data['data']
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update feedback: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status} - {error_text}")
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
                    raise Exception(f"API Error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            raise
    
    async def delete_conversation(self, project_id: str, session_id: str) -> bool:
        """Delete a conversation"""
        url = f"{self.base_url}/projects/{project_id}/conversations/{session_id}"
        
        try:
            session = await self._get_session()
            async with session.delete(url, headers=self.headers) as response:
                if response.status == 200:
                    logger.info(f"Deleted conversation {session_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to delete conversation: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False