"""
Adaptive Cards for Microsoft Teams Bot
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

class AdaptiveCardBuilder:
    """Builder for Microsoft Teams Adaptive Cards"""
    
    @staticmethod
    def create_welcome_card(
        bot_name: str = "CustomGPT Bot",
        starter_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a welcome card with starter questions"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "Image",
                            "url": "https://app.customgpt.ai/logo.png",
                            "size": "Medium",
                            "horizontalAlignment": "Center"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Welcome to {bot_name}!",
                            "weight": "Bolder",
                            "size": "Large",
                            "horizontalAlignment": "Center",
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "I'm here to help answer your questions. You can ask me anything or choose from the suggestions below.",
                            "wrap": True,
                            "horizontalAlignment": "Center",
                            "spacing": "Small"
                        }
                    ]
                }
            ]
        }
        
        if starter_questions:
            # Add starter questions section
            question_container = {
                "type": "Container",
                "spacing": "Large",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "**Suggested Questions:**",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    }
                ]
            }
            
            # Add action buttons for each starter question
            actions = []
            for i, question in enumerate(starter_questions[:5]):  # Limit to 5 questions
                actions.append({
                    "type": "Action.Submit",
                    "title": question,
                    "data": {
                        "action": "ask_question",
                        "question": question
                    }
                })
            
            card["body"].append(question_container)
            card["actions"] = actions
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_response_card(
        response: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        show_feedback: bool = True
    ) -> Dict[str, Any]:
        """Create a response card with citations and feedback buttons"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "TextBlock",
                    "text": response,
                    "wrap": True,
                    "size": "Default"
                }
            ],
            "actions": []
        }
        
        # Add citations if available
        if citations and len(citations) > 0:
            citations_container = {
                "type": "Container",
                "spacing": "Large",
                "separator": True,
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "**Sources:**",
                        "weight": "Bolder",
                        "size": "Small",
                        "spacing": "Medium"
                    }
                ]
            }
            
            for citation in citations[:5]:  # Limit to 5 citations
                citation_item = {
                    "type": "Container",
                    "spacing": "Small",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"• [{citation.get('title', 'Source')}]({citation.get('url', '#')})",
                            "wrap": True,
                            "size": "Small",
                            "color": "Accent"
                        }
                    ]
                }
                citations_container["items"].append(citation_item)
            
            card["body"].append(citations_container)
        
        # Add feedback buttons if enabled
        if show_feedback and session_id and message_id:
            card["actions"].extend([
                {
                    "type": "Action.Submit",
                    "title": "👍",
                    "data": {
                        "action": "feedback",
                        "reaction": "thumbs_up",
                        "session_id": session_id,
                        "message_id": message_id
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "👎",
                    "data": {
                        "action": "feedback",
                        "reaction": "thumbs_down",
                        "session_id": session_id,
                        "message_id": message_id
                    }
                }
            ])
        
        # Add copy button
        card["actions"].append({
            "type": "Action.Submit",
            "title": "Copy Response",
            "data": {
                "action": "copy",
                "text": response
            }
        })
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_error_card(
        error_message: str,
        details: Optional[str] = None,
        retry_available: bool = True
    ) -> Dict[str, Any]:
        """Create an error card"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "attention",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "⚠️",
                                            "size": "Large"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "**Error**",
                                            "weight": "Bolder",
                                            "size": "Medium"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": error_message,
                                            "wrap": True,
                                            "spacing": "Small"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        if details:
            card["body"].append({
                "type": "Container",
                "spacing": "Medium",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": details,
                        "wrap": True,
                        "size": "Small",
                        "isSubtle": True
                    }
                ]
            })
        
        if retry_available:
            card["actions"] = [
                {
                    "type": "Action.Submit",
                    "title": "Try Again",
                    "data": {
                        "action": "retry"
                    }
                }
            ]
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_rate_limit_card(
        reset_time: int,
        user_remaining: Optional[int] = None,
        api_remaining: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a rate limit notification card"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "warning",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "**Rate Limit Reached**",
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Please wait {reset_time} seconds before sending another message.",
                            "wrap": True,
                            "spacing": "Small"
                        }
                    ]
                }
            ]
        }
        
        # Add quota information if available
        if user_remaining is not None or api_remaining is not None:
            quota_items = []
            
            if user_remaining is not None:
                quota_items.append({
                    "type": "TextBlock",
                    "text": f"• Messages remaining: {user_remaining}",
                    "size": "Small"
                })
            
            if api_remaining is not None:
                quota_items.append({
                    "type": "TextBlock",
                    "text": f"• API queries remaining: {api_remaining}",
                    "size": "Small"
                })
            
            card["body"].append({
                "type": "Container",
                "spacing": "Medium",
                "items": quota_items
            })
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_typing_indicator_card() -> Dict[str, Any]:
        """Create a typing indicator card"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",
                                            "size": "Small",
                                            "altText": "Typing..."
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "CustomGPT is thinking...",
                                            "isSubtle": True
                                        }
                                    ],
                                    "verticalContentAlignment": "Center"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_feedback_confirmation_card(reaction: str) -> Dict[str, Any]:
        """Create a feedback confirmation card"""
        emoji = "👍" if reaction == "thumbs_up" else "👎"
        message = "Thank you for your positive feedback!" if reaction == "thumbs_up" else "Thank you for your feedback. We'll work on improving."
        
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "good" if reaction == "thumbs_up" else "attention",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{emoji} {message}",
                            "wrap": True,
                            "horizontalAlignment": "Center"
                        }
                    ]
                }
            ]
        }
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def create_help_card() -> Dict[str, Any]:
        """Create a help card with bot instructions"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "**CustomGPT Bot Help**",
                    "weight": "Bolder",
                    "size": "Large"
                },
                {
                    "type": "Container",
                    "spacing": "Medium",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "**How to use this bot:**",
                            "weight": "Bolder",
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "• In channels: @mention me with your question",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "• In direct chat: Just type your question",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "• Use threads to maintain context in conversations",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "Container",
                    "spacing": "Medium",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "**Available Commands:**",
                            "weight": "Bolder",
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "• **/help** - Show this help message",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "• **/clear** - Clear conversation history",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "• **/status** - Check bot status and limits",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
        
        return AdaptiveCardBuilder._create_attachment(card)
    
    @staticmethod
    def _create_attachment(card: Dict[str, Any]) -> Dict[str, Any]:
        """Create an attachment from an Adaptive Card"""
        return {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card
        }