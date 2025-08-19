import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, AsyncGenerator
import structlog
from datetime import datetime
import ssl
import certifi

logger = structlog.get_logger()


class CustomGPTClient:
    def __init__(self, api_url: str, api_key: str, project_id: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.project_id = project_id
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.session = None
        
        # Create SSL context with proper certificates
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def ensure_session(self):
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def create_conversation(self, name: Optional[str] = None) -> Optional[str]:
        """Create a new conversation and return the session ID"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}/conversations"
            
            # Add name field as required by API
            payload = {
                "name": name or f"Telegram Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
            async with self.session.post(url, headers=self.headers, json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    session_id = data.get('data', {}).get('session_id')
                    logger.info("conversation_created", 
                               project_id=self.project_id, 
                               session_id=session_id)
                    return session_id
                else:
                    error_text = await response.text()
                    logger.error("conversation_creation_failed", 
                                status=response.status, 
                                error=error_text)
                    return None
                    
        except Exception as e:
            logger.error("conversation_creation_error", error=str(e))
            return None
    
    async def send_message(self, session_id: str, message: str, 
                          stream: bool = False,
                          language: str = 'en',
                          custom_persona: Optional[str] = None,
                          response_source: str = 'default') -> Optional[Dict]:
        """Send a message to the conversation"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}/conversations/{session_id}/messages"
            
            params = {
                'lang': language
            }
            
            # Only add stream param if it's True (as string)
            if stream:
                params['stream'] = 'true'
            
            payload = {
                'prompt': message,
                'response_source': response_source
            }
            
            if custom_persona:
                payload['custom_persona'] = custom_persona
            
            if stream:
                return await self._send_streaming_message(url, params, payload)
            else:
                return await self._send_regular_message(url, params, payload)
                
        except Exception as e:
            logger.error("message_sending_error", error=str(e))
            return None
    
    async def _send_regular_message(self, url: str, params: Dict, payload: Dict) -> Optional[Dict]:
        """Send a regular non-streaming message"""
        async with self.session.post(url, 
                                   headers=self.headers, 
                                   params=params,
                                   json=payload) as response:
            if response.status == 200:
                data = await response.json()
                logger.info("customgpt_response", 
                          response_type=type(data).__name__,
                          response_data=data)
                
                # Handle different response formats
                if isinstance(data, dict):
                    # If response has 'data' key, return that
                    if 'data' in data:
                        return data['data']
                    # Otherwise return the whole response
                    return data
                else:
                    logger.warning("unexpected_response_type", 
                                 response_type=type(data).__name__,
                                 response=str(data))
                    return None
            else:
                error_text = await response.text()
                logger.error("message_send_failed", 
                           status=response.status, 
                           error=error_text,
                           url=url,
                           params=params,
                           payload=payload)
                return None
    
    async def _send_streaming_message(self, url: str, params: Dict, payload: Dict) -> AsyncGenerator:
        """Send a streaming message and yield chunks"""
        async with self.session.post(url, 
                                   headers=self.headers, 
                                   params=params,
                                   json=payload) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                yield data
                                if data.get('status') == 'finish':
                                    break
                            except json.JSONDecodeError:
                                continue
            else:
                error_text = await response.text()
                logger.error("streaming_message_failed", 
                           status=response.status, 
                           error=error_text)
                yield {'error': error_text, 'status': 'error'}
    
    async def send_message_openai_format(self, messages: List[Dict], 
                                       stream: bool = False,
                                       model: Optional[str] = None) -> Optional[Dict]:
        """Send messages using OpenAI chat completion format"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}/chat-completions"
            
            payload = {
                'messages': messages,
                'stream': stream
            }
            
            if model:
                payload['model'] = model
            
            async with self.session.post(url, 
                                       headers=self.headers, 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.error("openai_format_message_failed", 
                               status=response.status, 
                               error=error_text)
                    return None
                    
        except Exception as e:
            logger.error("openai_format_error", error=str(e))
            return None
    
    async def get_conversation_messages(self, session_id: str, 
                                      page: int = 1, 
                                      limit: int = 10) -> Optional[Dict]:
        """Retrieve messages from a conversation"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}/conversations/{session_id}/messages"
            
            params = {
                'page': page,
                'limit': limit,
                'order': 'asc'
            }
            
            async with self.session.get(url, 
                                      headers=self.headers, 
                                      params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {})
                else:
                    error_text = await response.text()
                    logger.error("messages_retrieval_failed", 
                               status=response.status, 
                               error=error_text)
                    return None
                    
        except Exception as e:
            logger.error("messages_retrieval_error", error=str(e))
            return None
    
    async def update_message_feedback(self, session_id: str, 
                                    prompt_id: int, 
                                    reaction: str) -> bool:
        """Update reaction/feedback for a message"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}/conversations/{session_id}/messages/{prompt_id}/feedback"
            
            payload = {
                'reaction': reaction
            }
            
            async with self.session.put(url, 
                                      headers=self.headers, 
                                      json=payload) as response:
                if response.status == 200:
                    logger.info("feedback_updated", 
                              prompt_id=prompt_id, 
                              reaction=reaction)
                    return True
                else:
                    error_text = await response.text()
                    logger.error("feedback_update_failed", 
                               status=response.status, 
                               error=error_text)
                    return False
                    
        except Exception as e:
            logger.error("feedback_update_error", error=str(e))
            return False
    
    async def get_agent_info(self) -> Optional[Dict]:
        """Get information about the current agent"""
        await self.ensure_session()
        
        try:
            url = f"{self.api_url}/api/v1/projects/{self.project_id}"
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {})
                else:
                    error_text = await response.text()
                    logger.error("agent_info_failed", 
                               status=response.status, 
                               error=error_text)
                    return None
                    
        except Exception as e:
            logger.error("agent_info_error", error=str(e))
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()