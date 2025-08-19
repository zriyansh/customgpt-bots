"""
Analytics Module for CustomGPT Slack Bot
Tracks usage, performance, and user interactions
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import aiohttp

from config import Config

logger = logging.getLogger(__name__)

class Analytics:
    """Analytics tracking for bot usage"""
    
    def __init__(self):
        self.enabled = Config.ENABLE_ANALYTICS
        self.endpoint = Config.ANALYTICS_ENDPOINT
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_size = 100
        self.flush_interval = 60  # seconds
        
        # In-memory metrics
        self.metrics = {
            'queries': defaultdict(int),
            'responses': defaultdict(int),
            'errors': defaultdict(int),
            'feedback': defaultdict(lambda: {'positive': 0, 'negative': 0}),
            'response_times': defaultdict(list),
            'active_users': set(),
            'active_channels': set()
        }
        
        # Start periodic flush
        if self.enabled:
            asyncio.create_task(self._periodic_flush())
    
    async def track_query(self, user_id: str, channel_id: str, query: str, agent_id: Optional[str] = None):
        """Track a user query"""
        if not self.enabled:
            return
        
        event = {
            'event': 'query_submitted',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'channel_id': channel_id,
            'agent_id': agent_id or Config.CUSTOMGPT_PROJECT_ID,
            'query_length': len(query),
            'properties': {
                'has_thread': '::' in channel_id,
                'is_dm': channel_id.startswith('D')
            }
        }
        
        # Update metrics
        self.metrics['queries'][agent_id or 'default'] += 1
        self.metrics['active_users'].add(user_id)
        self.metrics['active_channels'].add(channel_id)
        
        await self._add_event(event)
    
    async def track_response(self, user_id: str, channel_id: str, agent_id: str, 
                           success: bool, response_time: Optional[float] = None):
        """Track a bot response"""
        if not self.enabled:
            return
        
        event = {
            'event': 'response_generated',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'channel_id': channel_id,
            'agent_id': agent_id,
            'success': success,
            'response_time': response_time
        }
        
        # Update metrics
        if success:
            self.metrics['responses'][agent_id] += 1
            if response_time:
                self.metrics['response_times'][agent_id].append(response_time)
        else:
            self.metrics['errors'][agent_id] += 1
        
        await self._add_event(event)
    
    async def track_feedback(self, user_id: str, message_id: str, feedback_type: str):
        """Track user feedback"""
        if not self.enabled:
            return
        
        event = {
            'event': 'feedback_received',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'message_id': message_id,
            'feedback_type': feedback_type
        }
        
        # Update metrics
        if feedback_type == 'positive':
            self.metrics['feedback']['total']['positive'] += 1
        else:
            self.metrics['feedback']['total']['negative'] += 1
        
        await self._add_event(event)
    
    async def track_error(self, error_type: str, user_id: Optional[str] = None, 
                         details: Optional[Dict[str, Any]] = None):
        """Track errors"""
        if not self.enabled:
            return
        
        event = {
            'event': 'error_occurred',
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type,
            'user_id': user_id,
            'details': details or {}
        }
        
        # Update metrics
        self.metrics['errors'][error_type] += 1
        
        await self._add_event(event)
    
    async def track_command(self, command: str, user_id: str, channel_id: str, 
                          parameters: Optional[Dict[str, Any]] = None):
        """Track slash command usage"""
        if not self.enabled:
            return
        
        event = {
            'event': 'command_executed',
            'timestamp': datetime.utcnow().isoformat(),
            'command': command,
            'user_id': user_id,
            'channel_id': channel_id,
            'parameters': parameters or {}
        }
        
        await self._add_event(event)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        # Calculate averages
        avg_response_times = {}
        for agent_id, times in self.metrics['response_times'].items():
            if times:
                avg_response_times[agent_id] = sum(times) / len(times)
        
        # Calculate feedback ratio
        feedback_ratio = {}
        for key, feedback in self.metrics['feedback'].items():
            total = feedback['positive'] + feedback['negative']
            if total > 0:
                feedback_ratio[key] = feedback['positive'] / total
        
        return {
            'period': 'session',
            'total_queries': sum(self.metrics['queries'].values()),
            'total_responses': sum(self.metrics['responses'].values()),
            'total_errors': sum(self.metrics['errors'].values()),
            'unique_users': len(self.metrics['active_users']),
            'unique_channels': len(self.metrics['active_channels']),
            'queries_by_agent': dict(self.metrics['queries']),
            'average_response_times': avg_response_times,
            'feedback_ratio': feedback_ratio,
            'errors_by_type': dict(self.metrics['errors'])
        }
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        # This would typically query a database
        # For now, return placeholder data
        return {
            'user_id': user_id,
            'total_queries': 0,
            'first_seen': None,
            'last_seen': None,
            'favorite_agent': None
        }
    
    async def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        response_times = self.metrics['response_times'].get(agent_id, [])
        
        return {
            'agent_id': agent_id,
            'total_queries': self.metrics['queries'].get(agent_id, 0),
            'total_responses': self.metrics['responses'].get(agent_id, 0),
            'total_errors': self.metrics['errors'].get(agent_id, 0),
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'success_rate': self._calculate_success_rate(agent_id)
        }
    
    def _calculate_success_rate(self, agent_id: str) -> float:
        """Calculate success rate for an agent"""
        responses = self.metrics['responses'].get(agent_id, 0)
        errors = self.metrics['errors'].get(agent_id, 0)
        total = responses + errors
        
        if total == 0:
            return 0.0
        
        return responses / total
    
    async def _add_event(self, event: Dict[str, Any]):
        """Add event to buffer"""
        self.buffer.append(event)
        
        # Flush if buffer is full
        if len(self.buffer) >= self.buffer_size:
            await self._flush_events()
    
    async def _flush_events(self):
        """Flush events to analytics endpoint"""
        if not self.buffer or not self.endpoint:
            return
        
        events_to_send = self.buffer.copy()
        self.buffer.clear()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json={'events': events_to_send},
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send analytics: {response.status}")
                        # Add events back to buffer for retry
                        self.buffer.extend(events_to_send)
        except Exception as e:
            logger.error(f"Error sending analytics: {str(e)}")
            # Add events back to buffer for retry
            self.buffer.extend(events_to_send)
    
    async def _periodic_flush(self):
        """Periodically flush events"""
        while True:
            await asyncio.sleep(self.flush_interval)
            if self.buffer:
                await self._flush_events()
    
    async def close(self):
        """Close analytics and flush remaining events"""
        if self.buffer:
            await self._flush_events()