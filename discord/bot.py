import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional, List
import re

from config import *
from customgpt_client import CustomGPTClient
from rate_limiter import RateLimiter, DiscordRateLimiter
from views import StarterQuestionsView, PaginationView, CitationView, HelpView

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomGPTBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.customgpt_client = None
        self.rate_limiter = None
        self.discord_rate_limiter = None
        self.starter_questions = STARTER_QUESTIONS
        
    async def cog_load(self):
        """Initialize connections when cog loads"""
        # Initialize CustomGPT client
        self.customgpt_client = CustomGPTClient(
            CUSTOMGPT_API_KEY,
            CUSTOMGPT_API_URL,
            CUSTOMGPT_AGENT_ID
        )
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(REDIS_URL)
        await self.rate_limiter.connect()
        
        self.discord_rate_limiter = DiscordRateLimiter(
            self.rate_limiter,
            {
                'RATE_LIMIT_PER_USER': RATE_LIMIT_PER_USER,
                'RATE_LIMIT_PER_CHANNEL': RATE_LIMIT_PER_CHANNEL,
                'RATE_LIMIT_WINDOW': RATE_LIMIT_WINDOW
            }
        )
        
        # Fetch starter questions from API
        await self._fetch_starter_questions()
        
        logger.info("CustomGPT Bot cog loaded successfully")
    
    async def cog_unload(self):
        """Cleanup when cog unloads"""
        if self.rate_limiter:
            await self.rate_limiter.disconnect()
        if self.customgpt_client and self.customgpt_client._session:
            await self.customgpt_client._session.close()
    
    async def _fetch_starter_questions(self):
        """Fetch starter questions from CustomGPT API"""
        try:
            async with self.customgpt_client:
                questions = await self.customgpt_client.get_starter_questions()
                if questions:
                    self.starter_questions = questions
        except Exception as e:
            logger.error(f"Failed to fetch starter questions: {e}")
    
    def _check_permissions(self, ctx: commands.Context) -> bool:
        """Check if user has permission to use the bot"""
        # Check allowed channels
        if ALLOWED_CHANNELS and str(ctx.channel.id) not in ALLOWED_CHANNELS:
            return False
        
        # Check allowed roles
        if ALLOWED_ROLES:
            user_roles = [str(role.id) for role in ctx.author.roles]
            if not any(role in ALLOWED_ROLES for role in user_roles):
                return False
        
        return True
    
    def _split_message(self, content: str, max_length: int = 2000) -> List[str]:
        """Split long messages into chunks"""
        if len(content) <= max_length:
            return [content]
        
        # Try to split at sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def process_message(self, channel: discord.TextChannel, author: discord.User, question: str):
        """Process a message/question"""
        try:
            # Show typing indicator
            if TYPING_INDICATOR:
                async with channel.typing():
                    await self._send_response(channel, author, question)
            else:
                await self._send_response(channel, author, question)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await channel.send(ERROR_MESSAGES['api_error'])
    
    async def _send_response(self, channel: discord.TextChannel, author: discord.User, question: str):
        """Send response to user"""
        async with self.customgpt_client:
            response = await self.customgpt_client.send_message(
                question,
                str(channel.id)
            )
            
            content = response['content']
            citations = response.get('citations', [])
            
            # Split message if too long
            chunks = self._split_message(content)
            
            if len(chunks) == 1:
                # Single message
                if citations and ENABLE_CITATIONS:
                    view = CitationView(citations, chunks[0])
                    await channel.send(chunks[0], view=view)
                else:
                    await channel.send(chunks[0])
            else:
                # Multiple pages
                embed = discord.Embed(
                    description=chunks[0],
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Page 1/{len(chunks)}")
                
                view = PaginationView(chunks, author)
                await channel.send(embed=embed, view=view)
    
    @commands.command(name='ask', aliases=['a', 'q'])
    async def ask(self, ctx: commands.Context, *, question: str = None):
        """Ask a question to the CustomGPT agent"""
        # Check permissions
        if not self._check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['unauthorized'])
            return
        
        # Check if question provided
        if not question:
            await ctx.send(ERROR_MESSAGES['invalid_input'])
            return
        
        # Check message length
        if len(question) > MAX_MESSAGE_LENGTH:
            await ctx.send(f"❌ Your message is too long. Please keep it under {MAX_MESSAGE_LENGTH} characters.")
            return
        
        # Check rate limits
        user_allowed, user_remaining, user_reset = await self.discord_rate_limiter.check_user_limit(
            str(ctx.author.id)
        )
        channel_allowed, channel_remaining, channel_reset = await self.discord_rate_limiter.check_channel_limit(
            str(ctx.channel.id)
        )
        
        if not user_allowed:
            await ctx.send(
                f"{ERROR_MESSAGES['rate_limit']}\n"
                f"Reset in {user_reset} seconds."
            )
            return
        
        if not channel_allowed:
            await ctx.send(
                f"⏱️ This channel has reached its query limit.\n"
                f"Reset in {channel_reset} seconds."
            )
            return
        
        # Process the message
        await self.process_message(ctx.channel, ctx.author, question)
    
    @commands.command(name='starters', aliases=['start', 'questions'])
    async def starters(self, ctx: commands.Context):
        """Show starter questions"""
        if not self._check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['unauthorized'])
            return
        
        if ENABLE_STARTER_QUESTIONS and self.starter_questions:
            embed = discord.Embed(
                title="🚀 Starter Questions",
                description="Click on any button below to ask that question:",
                color=discord.Color.blue()
            )
            
            view = StarterQuestionsView(self.starter_questions, self)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("Starter questions are not available.")
    
    @commands.command(name='info')
    async def info(self, ctx: commands.Context):
        """Show information about the connected agent"""
        if not self._check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['unauthorized'])
            return
        
        try:
            async with self.customgpt_client:
                agent_info = await self.customgpt_client.get_agent_info()
                
                embed = discord.Embed(
                    title=f"📊 {agent_info.get('project_name', 'CustomGPT Agent')}",
                    description=f"Agent ID: {agent_info.get('id', 'Unknown')}",
                    color=discord.Color.green()
                )
                
                # Add statistics if available
                if 'stats' in agent_info:
                    stats = agent_info['stats']
                    embed.add_field(
                        name="Statistics",
                        value=f"Pages: {stats.get('pages_count', 0)}\n"
                              f"Sources: {stats.get('sources_count', 0)}",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error fetching agent info: {e}")
            await ctx.send("Failed to fetch agent information.")
    
    @commands.command(name='reset')
    async def reset(self, ctx: commands.Context):
        """Reset conversation for this channel"""
        if not self._check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['unauthorized'])
            return
        
        channel_id = str(ctx.channel.id)
        if channel_id in self.customgpt_client._conversation_sessions:
            del self.customgpt_client._conversation_sessions[channel_id]
            await ctx.send("✅ Conversation has been reset for this channel.")
        else:
            await ctx.send("ℹ️ No active conversation to reset.")
    
    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 CustomGPT Discord Bot Help",
            description="Welcome! I'm here to answer your questions using CustomGPT's knowledge base.",
            color=discord.Color.blue()
        )
        
        view = HelpView()
        await ctx.send(embed=embed, view=view)

# Main bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=DISCORD_COMMAND_PREFIX, intents=intents)
bot.remove_command('help')  # Remove default help command

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{DISCORD_COMMAND_PREFIX}help"
        )
    )

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(ERROR_MESSAGES['api_error'])

async def main():
    async with bot:
        await bot.add_cog(CustomGPTBot(bot))
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())