import discord
from typing import List, Optional
import asyncio

class StarterQuestionsView(discord.ui.View):
    """View for displaying starter questions as buttons"""
    
    def __init__(self, questions: List[str], bot_instance):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot_instance
        
        # Add buttons for each question (max 5 due to Discord limitations)
        for i, question in enumerate(questions[:5]):
            button = QuestionButton(question, i)
            self.add_item(button)

class QuestionButton(discord.ui.Button):
    """Button for a starter question"""
    
    def __init__(self, question: str, index: int):
        # Truncate question if too long for button label
        label = question[:80] if len(question) > 80 else question
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=label,
            custom_id=f"question_{index}"
        )
        self.question = question
    
    async def callback(self, interaction: discord.Interaction):
        # Acknowledge the interaction
        await interaction.response.defer()
        
        # Get the bot's cog to process the question
        cog = interaction.client.get_cog('CustomGPTBot')
        if cog:
            # Process the question as if the user typed it
            await cog.process_message(interaction.channel, interaction.user, self.question)

class PaginationView(discord.ui.View):
    """View for paginating through long responses"""
    
    def __init__(self, pages: List[str], original_author: discord.User):
        super().__init__(timeout=300)
        self.pages = pages
        self.current_page = 0
        self.original_author = original_author
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.children[0].disabled = self.current_page == 0  # Previous button
        self.children[1].disabled = self.current_page == len(self.pages) - 1  # Next button
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_author:
            await interaction.response.send_message("Only the original requester can navigate pages.", ephemeral=True)
            return
            
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        
        embed = discord.Embed(
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_author:
            await interaction.response.send_message("Only the original requester can navigate pages.", ephemeral=True)
            return
            
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        self.update_buttons()
        
        embed = discord.Embed(
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")
        
        await interaction.response.edit_message(embed=embed, view=self)

class CitationView(discord.ui.View):
    """View for showing citations"""
    
    def __init__(self, citations: List[dict], message_content: str):
        super().__init__(timeout=60)
        self.citations = citations
        self.message_content = message_content
        self.showing_citations = False
    
    @discord.ui.button(label="📚 Show Sources", style=discord.ButtonStyle.secondary)
    async def toggle_citations(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.showing_citations = not self.showing_citations
        
        if self.showing_citations:
            button.label = "📚 Hide Sources"
            # Create citations embed
            embed = discord.Embed(
                title="Sources",
                color=discord.Color.green()
            )
            
            for i, citation in enumerate(self.citations[:5]):  # Limit to 5 citations
                title = citation.get('title', f'Source {i+1}')
                url = citation.get('url', '')
                description = citation.get('description', '')
                
                field_value = f"[{url}]({url})" if url else "No URL available"
                if description:
                    field_value += f"\n{description[:100]}..."
                
                embed.add_field(
                    name=title[:256],
                    value=field_value[:1024],
                    inline=False
                )
            
            await interaction.response.edit_message(content=self.message_content, embed=embed, view=self)
        else:
            button.label = "📚 Show Sources"
            await interaction.response.edit_message(content=self.message_content, embed=None, view=self)

class HelpView(discord.ui.View):
    """View for help command with categorized buttons"""
    
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="🤖 Bot Commands", style=discord.ButtonStyle.primary)
    async def commands_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="!ask [question]",
            value="Ask a question to the CustomGPT agent",
            inline=False
        )
        embed.add_field(
            name="!help",
            value="Show this help message",
            inline=False
        )
        embed.add_field(
            name="!info",
            value="Show information about the connected agent",
            inline=False
        )
        embed.add_field(
            name="!reset",
            value="Reset your conversation with the agent",
            inline=False
        )
        embed.add_field(
            name="!starters",
            value="Show starter questions",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❓ How to Use", style=discord.ButtonStyle.secondary)
    async def usage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="How to Use the Bot",
            description="Follow these steps to interact with the bot:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="1. Start a conversation",
            value="Use `!ask` followed by your question",
            inline=False
        )
        embed.add_field(
            name="2. Continue the conversation",
            value="The bot remembers your conversation context",
            inline=False
        )
        embed.add_field(
            name="3. Use starter questions",
            value="Type `!starters` to see suggested questions",
            inline=False
        )
        embed.add_field(
            name="4. Rate limits",
            value="There are rate limits to prevent abuse",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⚙️ Settings Info", style=discord.ButtonStyle.secondary)
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Bot Settings",
            description="Current bot configuration:",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="Rate Limits",
            value="10 queries per minute per user\n30 queries per minute per channel",
            inline=False
        )
        embed.add_field(
            name="Features",
            value="✅ Conversation memory\n✅ Source citations\n✅ Starter questions\n✅ Rate limiting",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)