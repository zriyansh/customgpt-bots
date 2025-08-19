"""
Security Manager for CustomGPT Slack Bot
Handles user authentication, authorization, and input validation
"""

import re
import logging
import hashlib
import hmac
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)

class SecurityManager:
    """Manages security aspects of the bot"""
    
    def __init__(self):
        self.allowed_channels = Config.get_allowed_channels()
        self.blocked_users = Config.get_blocked_users()
        
        # Patterns for detecting potentially harmful content
        self.harmful_patterns = [
            r'(?i)(drop\s+table|delete\s+from|insert\s+into)',  # SQL injection
            r'<script[^>]*>.*?</script>',  # XSS attempts
            r'(?i)(api[_\s-]?key|secret|token|password)\s*[:=]\s*["\']?[\w-]+',  # Secrets
            r'(?i)(eval|exec|__import__|compile)\s*\(',  # Code execution
        ]
        
        # Compile regex patterns
        self.harmful_regex = [re.compile(pattern) for pattern in self.harmful_patterns]
    
    async def is_user_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to use the bot"""
        # Check if user is blocked
        if self.blocked_users and user_id in self.blocked_users:
            logger.warning(f"Blocked user attempted access: {user_id}")
            return False
        
        return True
    
    async def is_channel_allowed(self, channel_id: str) -> bool:
        """Check if channel is allowed for bot usage"""
        # If no allowed channels configured, allow all
        if not self.allowed_channels:
            return True
        
        # Check if channel is in allowed list
        if channel_id not in self.allowed_channels:
            logger.warning(f"Unauthorized channel access attempt: {channel_id}")
            return False
        
        return True
    
    def validate_input(self, text: str) -> bool:
        """
        Validate user input for security threats
        
        Args:
            text: User input text
        
        Returns:
            bool: True if input is safe, False otherwise
        """
        if not text:
            return True
        
        # Check length
        if len(text) > Config.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(text)} characters")
            return False
        
        # Check for harmful patterns
        for regex in self.harmful_regex:
            if regex.search(text):
                logger.warning(f"Potentially harmful content detected: {text[:100]}...")
                return False
        
        return True
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content
        
        Args:
            text: User input text
        
        Returns:
            str: Sanitized text
        """
        if not text:
            return text
        
        # Truncate if too long
        if len(text) > Config.MAX_MESSAGE_LENGTH:
            text = text[:Config.MAX_MESSAGE_LENGTH] + "..."
        
        # Remove potentially harmful patterns
        for regex in self.harmful_regex:
            text = regex.sub('[REDACTED]', text)
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    def verify_slack_request(self, timestamp: str, signature: str, body: bytes) -> bool:
        """
        Verify that a request came from Slack
        
        Args:
            timestamp: Request timestamp from Slack
            signature: Request signature from Slack
            body: Raw request body
        
        Returns:
            bool: True if request is valid, False otherwise
        """
        # Check timestamp to prevent replay attacks
        current_time = time.time()
        if abs(current_time - float(timestamp)) > 60 * 5:  # 5 minutes
            logger.warning("Request timestamp too old")
            return False
        
        # Verify signature
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        my_signature = 'v0=' + hmac.new(
            Config.SLACK_SIGNING_SECRET.encode('utf-8'),
            sig_basestring.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(my_signature, signature):
            logger.warning("Invalid request signature")
            return False
        
        return True
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive data in logs or responses
        
        Args:
            data: Dictionary containing potentially sensitive data
        
        Returns:
            dict: Dictionary with sensitive data masked
        """
        sensitive_keys = [
            'token', 'api_key', 'secret', 'password', 'auth',
            'authorization', 'x-api-key', 'bearer'
        ]
        
        def mask_value(value: Any) -> Any:
            if isinstance(value, str) and len(value) > 4:
                # Show first 2 and last 2 characters
                return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
            elif isinstance(value, dict):
                return mask_dict(value)
            elif isinstance(value, list):
                return [mask_value(item) for item in value]
            else:
                return value
        
        def mask_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            masked = {}
            for key, value in d.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    masked[key] = mask_value(value) if value else None
                elif isinstance(value, dict):
                    masked[key] = mask_dict(value)
                elif isinstance(value, list):
                    masked[key] = [mask_value(item) if isinstance(item, dict) else item for item in value]
                else:
                    masked[key] = value
            return masked
        
        return mask_dict(data)
    
    def validate_agent_id(self, agent_id: str) -> bool:
        """
        Validate agent ID format
        
        Args:
            agent_id: Agent/Project ID
        
        Returns:
            bool: True if valid, False otherwise
        """
        # CustomGPT agent IDs are numeric
        return agent_id.isdigit()
    
    def get_safe_error_message(self, error: Exception) -> str:
        """
        Get a safe error message that doesn't expose sensitive information
        
        Args:
            error: The exception
        
        Returns:
            str: Safe error message
        """
        error_str = str(error).lower()
        
        # Check for specific error types
        if 'rate limit' in error_str:
            return "Rate limit exceeded. Please try again later."
        elif 'unauthorized' in error_str or '401' in error_str:
            return "Authentication error. Please contact your administrator."
        elif 'not found' in error_str or '404' in error_str:
            return "The requested resource was not found."
        elif 'timeout' in error_str:
            return "Request timed out. Please try again."
        else:
            # Generic error message
            return "An error occurred while processing your request. Please try again later."
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            user_id: User ID involved
            details: Additional details about the event
        """
        masked_details = self.mask_sensitive_data(details)
        logger.warning(f"Security Event - Type: {event_type}, User: {user_id}, Details: {masked_details}")