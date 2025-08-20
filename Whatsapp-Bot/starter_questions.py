"""
Starter questions and suggestions for WhatsApp bot
"""

import random
from typing import List, Optional
import structlog

from config import STARTER_QUESTIONS

logger = structlog.get_logger()


class StarterQuestions:
    def __init__(self, customgpt_client=None):
        self.customgpt = customgpt_client
        self.questions = STARTER_QUESTIONS
        
        # Keywords to category mapping
        self.keyword_categories = {
            'general': ['help', 'start', 'begin', 'what', 'how', 'can'],
            'technical': ['api', 'code', 'integrate', 'technical', 'developer', 'programming'],
            'support': ['issue', 'problem', 'error', 'trouble', 'fix', 'broken'],
            'features': ['feature', 'capability', 'function', 'pricing', 'limit', 'plan']
        }
        
        # Follow-up question templates
        self.follow_up_templates = {
            'clarification': [
                "Can you tell me more about {topic}?",
                "What specific aspect of {topic} interests you?",
                "How would you like to use {topic}?"
            ],
            'deeper': [
                "What are the advanced features of {topic}?",
                "How does {topic} work internally?",
                "What are the best practices for {topic}?"
            ],
            'related': [
                "How does {topic} compare to alternatives?",
                "What are common use cases for {topic}?",
                "What should I know before using {topic}?"
            ],
            'next_steps': [
                "How do I get started with {topic}?",
                "What's the next step after {topic}?",
                "Where can I learn more about {topic}?"
            ]
        }
    
    async def get_initial_questions(self, category: Optional[str] = None) -> List[str]:
        """Get initial starter questions"""
        if category and category in self.questions:
            return self.questions[category]
        
        # Return mixed questions from all categories
        all_questions = []
        for cat_questions in self.questions.values():
            all_questions.extend(cat_questions)
        
        # Return random selection
        return random.sample(all_questions, min(5, len(all_questions)))
    
    async def get_suggestions(self, user_message: str, bot_response: str) -> List[str]:
        """Get follow-up question suggestions based on conversation"""
        suggestions = []
        
        try:
            # Detect topic from message and response
            topic = self._extract_topic(user_message, bot_response)
            
            # Determine category
            category = self._detect_category(user_message)
            
            # Generate follow-up questions
            if topic and len(topic) > 3 and ' ' not in topic[:2]:  # Ensure it's a meaningful topic
                # Add topic-specific follow-ups
                for template_type in ['clarification', 'deeper', 'next_steps']:
                    if template_type in self.follow_up_templates:
                        template = random.choice(self.follow_up_templates[template_type])
                        suggestions.append(template.format(topic=topic))
            
            # Add category-specific questions
            if category and category in self.questions:
                category_questions = [q for q in self.questions[category] 
                                    if q.lower() not in user_message.lower()]
                if category_questions:
                    suggestions.append(random.choice(category_questions))
            
            # Ensure variety and limit
            suggestions = list(dict.fromkeys(suggestions))[:3]  # Remove duplicates, limit to 3
            
            # If no suggestions, provide generic ones
            if not suggestions:
                suggestions = random.sample(
                    self.questions.get('general', []), 
                    min(3, len(self.questions.get('general', [])))
                )
            
        except Exception as e:
            logger.error("suggestion_generation_error", error=str(e))
            # Fallback to generic questions
            suggestions = self.questions.get('general', [])[:3]
        
        return suggestions
    
    def _detect_category(self, message: str) -> Optional[str]:
        """Detect question category from message"""
        message_lower = message.lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.keyword_categories.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'general'
    
    def _extract_topic(self, user_message: str, bot_response: str) -> Optional[str]:
        """Extract main topic from conversation"""
        # Simple topic extraction - can be enhanced with NLP
        
        # Common topic indicators
        topic_indicators = [
            'about', 'regarding', 'for', 'with', 'using', 
            'to', 'of', 'on', 'in', 'at'
        ]
        
        # Look for topic in user message
        words = user_message.lower().split()
        for i, word in enumerate(words):
            if word in topic_indicators and i + 1 < len(words):
                # Get the next word(s) as potential topic
                topic_words = []
                # Collect up to 3 words after the indicator
                for j in range(i + 1, min(i + 4, len(words))):
                    if words[j] not in ['the', 'a', 'an', 'it', 'this', 'that', 'is', 'are', 'was', 'were']:
                        topic_words.append(words[j])
                    else:
                        break
                
                if topic_words:
                    topic = ' '.join(topic_words)
                    # Check if it's a meaningful topic
                    if len(topic) > 2 and not any(char in topic for char in ["'", '"']):
                        return topic
        
        # Extract from bot response if no topic in user message
        # Look for emphasized words (in quotes, capitals, etc.)
        import re
        
        # Find quoted text
        quoted = re.findall(r'"([^"]+)"', bot_response)
        if quoted:
            return quoted[0].lower()
        
        # Find capitalized phrases (excluding sentence starts)
        sentences = bot_response.split('.')
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) > 3:  # Skip very short sentences
                capitalized = [w for w in words[1:] if w and w[0].isupper()]
                if capitalized:
                    return capitalized[0].lower()
        
        return None
    
    def get_category_questions(self, category: str) -> List[str]:
        """Get questions for a specific category"""
        return self.questions.get(category, self.questions['general'])
    
    def get_random_questions(self, count: int = 3, exclude: List[str] = None) -> List[str]:
        """Get random questions excluding certain ones"""
        exclude = exclude or []
        
        # Collect all questions
        all_questions = []
        for questions in self.questions.values():
            all_questions.extend(questions)
        
        # Filter out excluded questions
        available = [q for q in all_questions if q not in exclude]
        
        # Return random sample
        return random.sample(available, min(count, len(available)))