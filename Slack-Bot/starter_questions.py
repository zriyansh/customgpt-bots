"""
Starter Questions Manager for CustomGPT Slack Bot
Manages and caches starter questions from agent settings
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class StarterQuestionsManager:
    """Manages starter questions for agents"""
    
    def __init__(self, customgpt_client):
        self.customgpt_client = customgpt_client
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Default questions if none are configured
        self.default_questions = [
            "What can you help me with?",
            "Tell me about your main features",
            "How do I get started?",
            "What information do you have?",
            "Can you give me an overview?"
        ]
    
    async def get_questions(self, agent_id: str, force_refresh: bool = False) -> List[str]:
        """
        Get starter questions for an agent
        
        Args:
            agent_id: Agent/Project ID
            force_refresh: Force refresh from API
        
        Returns:
            List of starter questions
        """
        # Check cache first
        if not force_refresh and agent_id in self.cache:
            cache_entry = self.cache[agent_id]
            if datetime.now() < cache_entry['expires']:
                return cache_entry['questions']
        
        # Fetch from API
        try:
            settings = await self.customgpt_client.get_agent_settings(agent_id)
            questions = settings.get('example_questions', [])
            
            # Filter out empty questions
            questions = [q.strip() for q in questions if q and q.strip()]
            
            # If no questions configured, use defaults
            if not questions:
                questions = self.default_questions.copy()
            
            # Cache the questions
            self.cache[agent_id] = {
                'questions': questions,
                'expires': datetime.now() + self.cache_duration
            }
            
            logger.info(f"Loaded {len(questions)} starter questions for agent {agent_id}")
            return questions
            
        except Exception as e:
            logger.error(f"Error fetching starter questions for agent {agent_id}: {str(e)}")
            # Return cached questions if available, otherwise defaults
            if agent_id in self.cache:
                return self.cache[agent_id]['questions']
            return self.default_questions
    
    async def get_random_questions(self, agent_id: str, count: int = 3) -> List[str]:
        """
        Get random starter questions
        
        Args:
            agent_id: Agent/Project ID
            count: Number of questions to return
        
        Returns:
            List of random starter questions
        """
        all_questions = await self.get_questions(agent_id)
        
        # If we have fewer questions than requested, return all
        if len(all_questions) <= count:
            return all_questions
        
        # Return random sample
        return random.sample(all_questions, count)
    
    async def get_contextualized_questions(self, agent_id: str, context: str = "") -> List[str]:
        """
        Get starter questions with optional context awareness
        
        Args:
            agent_id: Agent/Project ID
            context: Optional context (e.g., user's previous questions)
        
        Returns:
            List of contextualized starter questions
        """
        base_questions = await self.get_questions(agent_id)
        
        # If no context, return base questions
        if not context:
            return base_questions
        
        # You could implement more sophisticated context-aware question selection here
        # For now, we'll just prioritize certain questions based on keywords
        
        context_lower = context.lower()
        prioritized = []
        others = []
        
        for question in base_questions:
            question_lower = question.lower()
            
            # Prioritize questions that might be related to the context
            if any(word in question_lower for word in ['start', 'begin', 'how to']) and 'start' in context_lower:
                prioritized.append(question)
            elif 'feature' in question_lower and 'feature' in context_lower:
                prioritized.append(question)
            elif 'help' in question_lower and 'help' in context_lower:
                prioritized.append(question)
            else:
                others.append(question)
        
        # Return prioritized questions first, then others
        return prioritized + others
    
    def clear_cache(self, agent_id: Optional[str] = None):
        """
        Clear cached questions
        
        Args:
            agent_id: Specific agent to clear, or None to clear all
        """
        if agent_id:
            if agent_id in self.cache:
                del self.cache[agent_id]
                logger.info(f"Cleared cache for agent {agent_id}")
        else:
            self.cache.clear()
            logger.info("Cleared all starter questions cache")
    
    async def get_formatted_questions(self, agent_id: str, format_type: str = "buttons") -> Dict[str, Any]:
        """
        Get questions formatted for Slack
        
        Args:
            agent_id: Agent/Project ID
            format_type: Format type (buttons, list, menu)
        
        Returns:
            Formatted questions for Slack
        """
        questions = await self.get_questions(agent_id)
        
        if format_type == "buttons":
            # Format as buttons
            blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Here are some questions to get you started:*"}
                }
            ]
            
            for i, question in enumerate(questions[:5]):  # Limit to 5 for UI
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"• {question}"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Ask"},
                        "action_id": f"ask_starter_{i}",
                        "value": question
                    }
                })
            
            return {"blocks": blocks}
        
        elif format_type == "list":
            # Format as numbered list
            text = "*Here are some questions to get you started:*\n\n"
            for i, question in enumerate(questions, 1):
                text += f"{i}. {question}\n"
            
            return {"text": text, "mrkdwn": True}
        
        elif format_type == "menu":
            # Format as dropdown menu
            options = []
            for i, question in enumerate(questions[:25]):  # Slack limit
                options.append({
                    "text": {"type": "plain_text", "text": question[:75]},  # Truncate for menu
                    "value": f"q_{i}"
                })
            
            blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Select a question to ask:*"},
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {"type": "plain_text", "text": "Choose a question"},
                        "options": options,
                        "action_id": "select_starter_question"
                    }
                }
            ]
            
            return {"blocks": blocks}
        
        else:
            # Default to list format
            return await self.get_formatted_questions(agent_id, "list")