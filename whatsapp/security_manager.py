"""
Security management for WhatsApp bot
"""

import re
from typing import List, Tuple, Optional, Dict
import structlog
from config import Config

logger = structlog.get_logger()


class SecurityManager:
    def __init__(self, config: Config):
        self.config = config
        self.allowed_numbers = config.ALLOWED_NUMBERS if config.ALLOWED_NUMBERS else []
        self.blocked_numbers = config.BLOCKED_NUMBERS if config.BLOCKED_NUMBERS else []
        self.max_message_length = config.MAX_MESSAGE_LENGTH
        self.enable_profanity_filter = config.ENABLE_PROFANITY_FILTER
        
        # Initialize profanity filter if enabled
        if self.enable_profanity_filter:
            try:
                from better_profanity import profanity
                profanity.load_censor_words()
                self.profanity_filter = profanity
            except ImportError:
                logger.warning("Profanity filter not available")
                self.profanity_filter = None
                self.enable_profanity_filter = False
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER)\b)",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b\s*\d+\s*=\s*\d+)",
            r"(\bAND\b\s*\d+\s*=\s*\d+)",
            r"(';|';--|';#)",
            r"(\bEXEC\b|\bEXECUTE\b)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r"(\||&&|;|\n|\r)",
            r"(`|\$\()",
            r"(rm\s+-rf|format\s+c:|del\s+/f)",
        ]
    
    def is_allowed_number(self, phone_number: str) -> bool:
        """Check if phone number is allowed to use the bot"""
        # Clean phone number
        phone_number = self._clean_phone_number(phone_number)
        
        # If no whitelist is configured, allow all numbers
        if not self.allowed_numbers:
            return True
        
        # Check if number is in whitelist
        return any(self._match_phone_number(phone_number, allowed) 
                  for allowed in self.allowed_numbers)
    
    def is_blocked_number(self, phone_number: str) -> bool:
        """Check if phone number is blocked"""
        # Clean phone number
        phone_number = self._clean_phone_number(phone_number)
        
        # Check if number is in blocklist
        return any(self._match_phone_number(phone_number, blocked) 
                  for blocked in self.blocked_numbers)
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """Validate message for security issues"""
        # Check message length
        if len(message) > self.max_message_length:
            return False, f"Message too long. Maximum {self.max_message_length} characters allowed."
        
        # Check for empty message
        if not message or not message.strip():
            return False, "Empty message not allowed."
        
        # Check for SQL injection patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning("sql_injection_attempt", message=message[:50])
                return False, "Invalid message format detected."
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning("xss_attempt", message=message[:50])
                return False, "Invalid message format detected."
        
        # Check for command injection patterns
        for pattern in self.command_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning("command_injection_attempt", message=message[:50])
                return False, "Invalid message format detected."
        
        # Check profanity if enabled
        if self.enable_profanity_filter and self.profanity_filter:
            if self.profanity_filter.contains_profanity(message):
                return False, "Please keep the conversation respectful."
        
        return True, None
    
    def sanitize_message(self, message: str) -> str:
        """Sanitize message by removing potentially harmful content"""
        # Remove any HTML tags
        message = re.sub(r'<[^>]+>', '', message)
        
        # Remove any script tags content
        message = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potentially dangerous characters
        message = re.sub(r'[<>\"\'`;]', '', message)
        
        # Trim whitespace
        message = message.strip()
        
        # Limit length
        if len(message) > self.max_message_length:
            message = message[:self.max_message_length]
        
        return message
    
    def is_admin_number(self, phone_number: str) -> bool:
        """Check if phone number belongs to an admin"""
        if not hasattr(self.config, 'ADMIN_NUMBERS') or not self.config.ADMIN_NUMBERS:
            return False
        
        phone_number = self._clean_phone_number(phone_number)
        admin_numbers = self.config.ADMIN_NUMBERS if isinstance(self.config.ADMIN_NUMBERS, list) else []
        
        return any(self._match_phone_number(phone_number, admin) 
                  for admin in admin_numbers)
    
    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """Validate bot command"""
        # Check if it's a valid command format
        if not command.startswith('/'):
            return False, "Commands must start with /"
        
        # Extract command name
        command_parts = command.split()
        if not command_parts:
            return False, "Empty command"
        
        command_name = command_parts[0][1:]  # Remove the /
        
        # Check if command name is alphanumeric
        if not re.match(r'^[a-zA-Z0-9_]+$', command_name):
            return False, "Invalid command format"
        
        # Check command length
        if len(command_name) > 20:
            return False, "Command name too long"
        
        return True, None
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and normalize phone number"""
        # Remove whatsapp: prefix if present
        if phone_number.startswith('whatsapp:'):
            phone_number = phone_number[9:]
        
        # Remove all non-digit characters except +
        phone_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Ensure it starts with + if it's an international number
        if phone_number and not phone_number.startswith('+'):
            # Assume it's a US number if no country code
            if len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        return phone_number
    
    def _match_phone_number(self, number1: str, number2: str) -> bool:
        """Check if two phone numbers match"""
        # Clean both numbers
        number1 = self._clean_phone_number(number1)
        number2 = self._clean_phone_number(number2)
        
        # Direct match
        if number1 == number2:
            return True
        
        # Check if one is contained in the other (handles different formats)
        if number1 and number2:
            # Remove country codes for comparison
            n1_digits = re.sub(r'^\+\d{1,3}', '', number1)
            n2_digits = re.sub(r'^\+\d{1,3}', '', number2)
            
            if n1_digits == n2_digits and n1_digits:
                return True
            
            # Check if last 10 digits match (common for US numbers)
            if len(n1_digits) >= 10 and len(n2_digits) >= 10:
                return n1_digits[-10:] == n2_digits[-10:]
        
        return False
    
    def get_rate_limit_multiplier(self, phone_number: str) -> float:
        """Get rate limit multiplier based on user type"""
        # Admins get higher limits
        if self.is_admin_number(phone_number):
            return 10.0  # 10x higher limits
        
        # Regular users
        return 1.0
    
    def log_security_event(self, event_type: str, phone_number: str, 
                          details: Optional[Dict] = None):
        """Log security-related events"""
        logger.warning("security_event",
                      event_type=event_type,
                      phone_number=self._clean_phone_number(phone_number),
                      details=details or {})