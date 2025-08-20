import aiohttp
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio

logger = logging.getLogger(__name__)

class CustomGPTClient:
    def __init__(self, api_key: str, api_url: str, agent_id: str):
        self.api_key = api_key
        self.api_url = api_url
        self.agent_id = agent_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self._session = None
        self._conversation_sessions = {}  # Store conversation sessions per Discord channel
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get_or_create_session(self, channel_id: str) -> str:
        """Get existing session or create a new one for a Discord channel"""
        if channel_id not in self._conversation_sessions:
            session_id = await self.create_conversation()
            self._conversation_sessions[channel_id] = session_id
        return self._conversation_sessions[channel_id]
    
    async def create_conversation(self) -> str:
        """Create a new conversation session"""
        url = f"{self.api_url}/projects/{self.agent_id}/conversations"
        
        # Add an empty JSON body as some APIs require it
        payload = {}
        
        try:
            async with self._session.post(url, headers=self.headers, json=payload) as response:
                response_text = await response.text()
                if response.status == 200 or response.status == 201:
                    data = json.loads(response_text)
                    return data['data']['session_id']
                else:
                    logger.error(f"Failed to create conversation: {response.status} - Response: {response_text}")
                    raise Exception(f"Failed to create conversation: {response.status}")
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    async def send_message(self, message: str, channel_id: str, stream: bool = False, inline_citations: bool = False) -> Dict[str, Any]:
        """Send a message to CustomGPT using OpenAI format for better compatibility"""
        # The OpenAI format endpoint doesn't require a session_id
        url = f"{self.api_url}/projects/{self.agent_id}/chat/completions"
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": stream,
            "lang": "en",
            "is_inline_citation": inline_citations
        }
        
        try:
            async with self._session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200 or response.status == 201:
                    if stream:
                        return self._handle_stream(response)
                    else:
                        data = await response.json()
                        return self._parse_response(data)
                else:
                    error_text = await response.text()
                    logger.error(f"API Error: {response.status} - {error_text}")
                    raise Exception(f"API Error: {response.status}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _handle_stream(self, response) -> AsyncGenerator[str, None]:
        """Handle streaming response"""
        async for line in response.content:
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                content = chunk['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the API response"""
        if 'choices' in data and data['choices']:
            message_content = data['choices'][0]['message']['content']
            
            # Extract citations if available (might be in different locations)
            citations = []
            if 'citations' in data:
                citations = data['citations']
            elif 'choices' in data and data['choices'] and 'citations' in data['choices'][0]:
                citations = data['choices'][0]['citations']
            
            return {
                'content': message_content,
                'citations': citations,
                'session_id': data.get('id', '')  # OpenAI format uses 'id' instead of 'session_id'
            }
        else:
            raise Exception("Invalid response format")
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information and settings"""
        url = f"{self.api_url}/projects/{self.agent_id}"
        
        try:
            async with self._session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
                else:
                    raise Exception(f"Failed to get agent info: {response.status}")
        except Exception as e:
            logger.error(f"Error getting agent info: {e}")
            raise
    
    async def get_starter_questions(self) -> list:
        """Get example questions from agent settings"""
        url = f"{self.api_url}/projects/{self.agent_id}/settings"
        
        try:
            async with self._session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data'].get('example_questions', [])
                else:
                    return []  # Return empty list if failed
        except Exception as e:
            logger.error(f"Error getting starter questions: {e}")
            return []