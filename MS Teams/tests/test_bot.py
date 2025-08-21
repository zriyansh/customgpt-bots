"""
Tests for CustomGPT Teams Bot
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from botbuilder.core import TurnContext, MessageFactory
from botbuilder.schema import Activity, ChannelAccount, ConversationAccount

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import CustomGPTBot
from config import Config
from rate_limiter import RateLimiter
from conversation_manager import ConversationManager


class TestCustomGPTBot:
    """Test cases for CustomGPT Teams Bot"""
    
    @pytest.fixture
    def bot(self):
        """Create bot instance"""
        with patch('customgpt_client.CustomGPTClient'):
            return CustomGPTBot()
    
    @pytest.fixture
    def mock_turn_context(self):
        """Create mock turn context"""
        activity = Activity(
            type="message",
            text="Hello bot",
            from_property=ChannelAccount(id="user123", name="Test User"),
            conversation=ConversationAccount(id="conv123"),
            channel_id="msteams",
            service_url="https://test.com"
        )
        
        context = Mock(spec=TurnContext)
        context.activity = activity
        context.send_activity = AsyncMock()
        context.send_activities = AsyncMock()
        
        return context
    
    @pytest.mark.asyncio
    async def test_on_message_activity_personal_chat(self, bot, mock_turn_context):
        """Test handling personal chat message"""
        mock_turn_context.activity.conversation.conversation_type = "personal"
        
        with patch.object(bot.customgpt_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'response': {'text': 'Hello! How can I help you?'},
                'citations': []
            }
            
            await bot.on_message_activity(mock_turn_context)
            
            # Verify message was sent to CustomGPT
            mock_send.assert_called_once()
            
            # Verify response was sent to user
            mock_turn_context.send_activity.assert_called()
    
    @pytest.mark.asyncio
    async def test_on_message_activity_channel_with_mention(self, bot, mock_turn_context):
        """Test handling channel message with bot mention"""
        mock_turn_context.activity.conversation.conversation_type = "channel"
        mock_turn_context.activity.text = "<at>CustomGPT Bot</at> What is the weather?"
        
        # Mock mention removal
        with patch.object(bot, '_remove_mentions') as mock_remove:
            mock_remove.return_value = "What is the weather?"
            
            with patch.object(bot.customgpt_client, 'send_message') as mock_send:
                mock_send.return_value = {
                    'response': {'text': 'I cannot provide weather information.'},
                    'citations': []
                }
                
                await bot.on_message_activity(mock_turn_context)
                
                # Verify mention was removed
                mock_remove.assert_called_once()
                
                # Verify message was processed
                mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_on_message_activity_channel_without_mention(self, bot, mock_turn_context):
        """Test handling channel message without bot mention"""
        mock_turn_context.activity.conversation.conversation_type = "channel"
        Config.REQUIRE_MENTION_IN_CHANNELS = True
        
        await bot.on_message_activity(mock_turn_context)
        
        # Verify no response was sent
        mock_turn_context.send_activity.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, bot, mock_turn_context):
        """Test rate limiting functionality"""
        # Mock rate limiter to return limit exceeded
        with patch.object(bot.rate_limiter, 'check_and_update') as mock_check:
            mock_check.return_value = False
            
            await bot.on_message_activity(mock_turn_context)
            
            # Verify rate limit message was sent
            mock_turn_context.send_activity.assert_called_once()
            call_args = mock_turn_context.send_activity.call_args[0][0]
            assert "rate limit" in call_args.text.lower()
    
    @pytest.mark.asyncio
    async def test_command_handling_help(self, bot, mock_turn_context):
        """Test /help command"""
        mock_turn_context.activity.text = "/help"
        
        await bot.on_message_activity(mock_turn_context)
        
        # Verify help message was sent
        mock_turn_context.send_activity.assert_called_once()
        call_args = mock_turn_context.send_activity.call_args[0][0]
        assert "available commands" in call_args.text.lower()
    
    @pytest.mark.asyncio
    async def test_command_handling_reset(self, bot, mock_turn_context):
        """Test /reset command"""
        mock_turn_context.activity.text = "/reset"
        
        # Add some conversation history first
        bot.conversation_manager.add_message("conv123", "user", "Previous message")
        
        await bot.on_message_activity(mock_turn_context)
        
        # Verify conversation was cleared
        history = bot.conversation_manager.get_conversation_history("conv123")
        assert len(history) == 0
        
        # Verify confirmation was sent
        mock_turn_context.send_activity.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, bot, mock_turn_context):
        """Test error handling"""
        # Mock CustomGPT client to raise exception
        with patch.object(bot.customgpt_client, 'send_message') as mock_send:
            mock_send.side_effect = Exception("API Error")
            
            await bot.on_message_activity(mock_turn_context)
            
            # Verify error message was sent
            mock_turn_context.send_activity.assert_called_once()
            call_args = mock_turn_context.send_activity.call_args[0][0]
            assert "error" in call_args.text.lower()
    
    @pytest.mark.asyncio
    async def test_file_attachment_handling(self, bot, mock_turn_context):
        """Test file attachment handling"""
        # Add attachment to activity
        mock_turn_context.activity.attachments = [{
            'contentType': 'application/pdf',
            'contentUrl': 'https://test.com/file.pdf',
            'name': 'test.pdf'
        }]
        
        Config.ENABLE_FILE_ATTACHMENTS = True
        
        with patch.object(bot.customgpt_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'response': {'text': 'I received your file.'},
                'citations': []
            }
            
            await bot.on_message_activity(mock_turn_context)
            
            # Verify attachment was processed
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert 'attachments' in call_args or 'files' in call_args
    
    @pytest.mark.asyncio
    async def test_conversation_context(self, bot, mock_turn_context):
        """Test conversation context management"""
        # Send first message
        mock_turn_context.activity.text = "Remember the number 42"
        with patch.object(bot.customgpt_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'response': {'text': 'I will remember the number 42.'},
                'citations': []
            }
            await bot.on_message_activity(mock_turn_context)
        
        # Send second message
        mock_turn_context.activity.text = "What number did I tell you?"
        with patch.object(bot.customgpt_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'response': {'text': 'You told me to remember the number 42.'},
                'citations': []
            }
            await bot.on_message_activity(mock_turn_context)
            
            # Verify context was included
            call_args = mock_send.call_args[1]
            assert 'conversation_id' in call_args or 'context' in call_args
    
    @pytest.mark.asyncio
    async def test_typing_indicator(self, bot, mock_turn_context):
        """Test typing indicator"""
        # Mock slow API response
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(0.1)
            return {
                'response': {'text': 'Slow response'},
                'citations': []
            }
        
        with patch.object(bot.customgpt_client, 'send_message', slow_response):
            await bot.on_message_activity(mock_turn_context)
            
            # Verify typing activity was sent
            calls = mock_turn_context.send_activity.call_args_list
            typing_sent = any(
                'typing' in str(call[0][0].type) if len(call[0]) > 0 else False
                for call in calls
            )
            assert typing_sent


class TestRateLimiter:
    """Test cases for rate limiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance"""
        return RateLimiter()
    
    def test_rate_limit_user(self, rate_limiter):
        """Test user rate limiting"""
        user_id = "test_user"
        
        # Should allow up to limit
        for i in range(Config.RATE_LIMIT_PER_USER):
            assert rate_limiter.check_and_update(user_id, "user")
        
        # Should block after limit
        assert not rate_limiter.check_and_update(user_id, "user")
    
    def test_rate_limit_channel(self, rate_limiter):
        """Test channel rate limiting"""
        channel_id = "test_channel"
        
        # Should allow up to limit
        for i in range(Config.RATE_LIMIT_PER_CHANNEL):
            assert rate_limiter.check_and_update(channel_id, "channel")
        
        # Should block after limit
        assert not rate_limiter.check_and_update(channel_id, "channel")
    
    def test_rate_limit_reset(self, rate_limiter):
        """Test rate limit reset after window"""
        user_id = "test_user"
        
        # Fill up rate limit
        for i in range(Config.RATE_LIMIT_PER_USER):
            rate_limiter.check_and_update(user_id, "user")
        
        # Should be blocked
        assert not rate_limiter.check_and_update(user_id, "user")
        
        # Mock time passing
        with patch('time.time', return_value=float('inf')):
            # Should be allowed after window
            assert rate_limiter.check_and_update(user_id, "user")


class TestConversationManager:
    """Test cases for conversation manager"""
    
    @pytest.fixture
    def manager(self):
        """Create conversation manager instance"""
        return ConversationManager()
    
    def test_add_and_get_messages(self, manager):
        """Test adding and retrieving messages"""
        conv_id = "test_conv"
        
        manager.add_message(conv_id, "user", "Hello")
        manager.add_message(conv_id, "assistant", "Hi there!")
        
        history = manager.get_conversation_history(conv_id)
        assert len(history) == 2
        assert history[0]['role'] == "user"
        assert history[0]['content'] == "Hello"
        assert history[1]['role'] == "assistant"
        assert history[1]['content'] == "Hi there!"
    
    def test_conversation_timeout(self, manager):
        """Test conversation timeout"""
        conv_id = "test_conv"
        
        # Add message
        manager.add_message(conv_id, "user", "Hello")
        
        # Mock time passing beyond timeout
        with patch('time.time', return_value=float('inf')):
            # Should return empty history after timeout
            history = manager.get_conversation_history(conv_id)
            assert len(history) == 0
    
    def test_max_context_messages(self, manager):
        """Test max context messages limit"""
        conv_id = "test_conv"
        
        # Add more messages than limit
        for i in range(Config.MAX_CONTEXT_MESSAGES + 5):
            manager.add_message(conv_id, "user", f"Message {i}")
        
        history = manager.get_conversation_history(conv_id)
        assert len(history) == Config.MAX_CONTEXT_MESSAGES
        # Should keep latest messages
        assert history[-1]['content'] == f"Message {Config.MAX_CONTEXT_MESSAGES + 4}"
    
    def test_clear_conversation(self, manager):
        """Test clearing conversation"""
        conv_id = "test_conv"
        
        manager.add_message(conv_id, "user", "Hello")
        manager.clear_conversation(conv_id)
        
        history = manager.get_conversation_history(conv_id)
        assert len(history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])