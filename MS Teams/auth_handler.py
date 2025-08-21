"""
Authentication Handler for Microsoft Teams Bot
"""

import logging
from typing import Dict, Any, Optional

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext
)
from botbuilder.schema import Activity
from botframework.connector.auth import (
    AuthenticationConfiguration,
    SimpleCredentialProvider,
    MicrosoftAppCredentials,
    JwtTokenValidation,
    ClaimsIdentity
)

from config import Config

logger = logging.getLogger(__name__)

class TeamsAuthHandler:
    """Handles authentication for Teams bot"""
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        
        # Create credential provider
        self.credential_provider = SimpleCredentialProvider(
            Config.TEAMS_APP_ID,
            Config.TEAMS_APP_PASSWORD
        )
        
        # Create authentication configuration
        self.auth_config = AuthenticationConfiguration()
        
        # Create adapter settings
        self.adapter_settings = BotFrameworkAdapterSettings(
            app_id=Config.TEAMS_APP_ID,
            app_password=Config.TEAMS_APP_PASSWORD,
            auth_configuration=self.auth_config,
            credential_provider=self.credential_provider
        )
        
        # Set up OpenID metadata based on app type
        if Config.TEAMS_APP_TYPE == 'SingleTenant':
            self.openid_metadata = f"https://login.microsoftonline.com/{Config.TEAMS_TENANT_ID}/v2.0/.well-known/openid-configuration"
        else:
            self.openid_metadata = Config.BOT_OPENID_METADATA
    
    def create_adapter(self) -> BotFrameworkAdapter:
        """Create a configured Bot Framework adapter"""
        adapter = BotFrameworkAdapter(self.adapter_settings)
        
        # Configure error handler
        adapter.on_turn_error = self._on_turn_error_handler
        
        return adapter
    
    async def _on_turn_error_handler(self, context: TurnContext, error: Exception) -> None:
        """Handle adapter errors"""
        logger.error(f"Adapter error: {str(error)}")
        
        try:
            # Send error message to user
            await context.send_activity(
                "Sorry, an error occurred while processing your request. Please try again later."
            )
            
            # Delete conversation state on error
            if hasattr(context, 'conversation_state'):
                await context.conversation_state.delete(context)
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")
    
    def create_app_credentials(self) -> MicrosoftAppCredentials:
        """Create Microsoft App credentials for API calls"""
        credentials = MicrosoftAppCredentials(
            app_id=Config.TEAMS_APP_ID,
            password=Config.TEAMS_APP_PASSWORD
        )
        
        # Configure for specific tenant if SingleTenant
        if Config.TEAMS_APP_TYPE == 'SingleTenant' and Config.TEAMS_TENANT_ID:
            credentials.oauth_endpoint = f"https://login.microsoftonline.com/{Config.TEAMS_TENANT_ID}"
        
        return credentials
    
    async def authenticate_request(
        self,
        activity: Activity,
        auth_header: str
    ) -> ClaimsIdentity:
        """Authenticate an incoming request"""
        try:
            # Validate the authentication header
            claims = await JwtTokenValidation.authenticate_request(
                activity,
                auth_header,
                self.credential_provider,
                self.auth_config
            )
            
            # Additional validation for specific app types
            if Config.TEAMS_APP_TYPE == 'SingleTenant' and Config.TEAMS_TENANT_ID:
                # Verify tenant ID matches
                tenant_id = claims.get_claim_value("tid")
                if tenant_id != Config.TEAMS_TENANT_ID:
                    raise ValueError(f"Invalid tenant ID: {tenant_id}")
            
            return claims
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
    
    @staticmethod
    def validate_tenant(activity: Activity) -> bool:
        """Validate that the activity is from an allowed tenant"""
        if not Config.ALLOWED_TENANTS:
            return True
        
        # Extract tenant ID from channel data
        tenant_id = activity.channel_data.get("tenant", {}).get("id") if activity.channel_data else None
        
        if not tenant_id:
            logger.warning("No tenant ID found in activity")
            return False
        
        return Config.is_tenant_allowed(tenant_id)
    
    @staticmethod
    def extract_user_info(activity: Activity) -> Dict[str, Any]:
        """Extract user information from activity"""
        user_info = {
            "id": activity.from_property.id,
            "name": activity.from_property.name,
            "aad_object_id": None,
            "tenant_id": None,
            "team_id": None,
            "channel_id": None
        }
        
        # Extract from channel data if available
        if activity.channel_data:
            tenant_info = activity.channel_data.get("tenant", {})
            team_info = activity.channel_data.get("team", {})
            channel_info = activity.channel_data.get("channel", {})
            
            user_info["tenant_id"] = tenant_info.get("id")
            user_info["team_id"] = team_info.get("id")
            user_info["channel_id"] = channel_info.get("id")
            
            # AAD object ID might be in from_property
            if hasattr(activity.from_property, 'aad_object_id'):
                user_info["aad_object_id"] = activity.from_property.aad_object_id
        
        return user_info
    
    @staticmethod
    def is_from_teams(activity: Activity) -> bool:
        """Check if the activity is from Microsoft Teams"""
        return activity.channel_id == "msteams"
    
    @staticmethod
    def get_team_info(activity: Activity) -> Optional[Dict[str, Any]]:
        """Get team information from activity"""
        if not TeamsAuthHandler.is_from_teams(activity):
            return None
        
        if not activity.channel_data:
            return None
        
        team_info = activity.channel_data.get("team")
        if not team_info:
            return None
        
        return {
            "id": team_info.get("id"),
            "name": team_info.get("name"),
            "aad_group_id": team_info.get("aadGroupId")
        }
    
    @staticmethod
    def get_meeting_info(activity: Activity) -> Optional[Dict[str, Any]]:
        """Get meeting information from activity"""
        if not TeamsAuthHandler.is_from_teams(activity):
            return None
        
        if not activity.channel_data:
            return None
        
        meeting_info = activity.channel_data.get("meeting")
        if not meeting_info:
            return None
        
        return {
            "id": meeting_info.get("id"),
            "type": meeting_info.get("type"),
            "title": meeting_info.get("title")
        }
    
    @staticmethod
    def create_teams_mention(user: ChannelAccount) -> Dict[str, Any]:
        """Create a mention entity for Teams"""
        return {
            "type": "mention",
            "mentioned": {
                "id": user.id,
                "name": user.name
            },
            "text": f"<at>{user.name}</at>"
        }