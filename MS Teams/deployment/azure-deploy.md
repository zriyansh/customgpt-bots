# Azure Deployment Guide for CustomGPT Teams Bot

This guide provides detailed instructions for deploying the CustomGPT Teams Bot to Azure.

## Prerequisites

- Azure subscription (free tier works)
- Azure CLI installed (optional but recommended)
- Git repository with your bot code
- CustomGPT API credentials

## Deployment Methods

### Method 1: Azure Portal (Web Interface)

#### Step 1: Create Bot Channel Registration

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Bot Channels Registration"
4. Click "Create"

Configuration:
- **Bot name**: `customgpt-teams-bot`
- **Subscription**: Your subscription
- **Resource group**: Create new or use existing
- **Location**: Choose nearest to your users
- **Pricing tier**: F0 (free) for testing, S1 for production
- **Messaging endpoint**: `https://[your-app-name].azurewebsites.net/api/messages`
- **Application Insights**: Enable (recommended)
- **Microsoft App ID**: Create new

5. Click "Review + create" then "Create"

#### Step 2: Create Azure Web App

1. In Azure Portal, click "Create a resource"
2. Search for "Web App"
3. Click "Create"

Configuration:
- **Name**: `customgpt-teams-bot` (must be unique)
- **Subscription**: Same as bot
- **Resource Group**: Same as bot
- **Runtime stack**: Python 3.11
- **Operating System**: Linux
- **Region**: Same as bot
- **App Service Plan**: 
  - **F1** (free) for testing
  - **B1** for production (supports always-on)

#### Step 3: Configure Application Settings

1. Go to your Web App in Azure Portal
2. Navigate to "Configuration" → "Application settings"
3. Add the following settings:

```
TEAMS_APP_ID = [from bot registration]
TEAMS_APP_PASSWORD = [from bot registration]
CUSTOMGPT_API_KEY = [your CustomGPT API key]
CUSTOMGPT_PROJECT_ID = [your CustomGPT project ID]
RATE_LIMIT_PER_USER = 20
RATE_LIMIT_PER_CHANNEL = 100
ENABLE_ADAPTIVE_CARDS = true
SCM_DO_BUILD_DURING_DEPLOYMENT = true
```

4. Click "Save" and restart the app

#### Step 4: Deploy Code

Option A - GitHub Actions:
1. In Web App, go to "Deployment Center"
2. Choose "GitHub" as source
3. Authorize and select repository
4. Azure creates GitHub Action workflow automatically

Option B - Local Git:
1. In Web App, go to "Deployment Center"
2. Choose "Local Git"
3. Note the Git URL
4. Deploy:
```bash
git remote add azure [git-url]
git push azure main
```

Option C - ZIP Deploy:
```bash
# Package your app
zip -r deploy.zip . -x "*.git*" -x "venv/*" -x "__pycache__/*"

# Deploy using Azure CLI
az webapp deploy --resource-group [rg-name] --name [app-name] --src-path deploy.zip
```

### Method 2: Azure CLI Deployment

```bash
# Variables
RG_NAME="customgpt-bot-rg"
LOCATION="eastus"
BOT_NAME="customgpt-teams-bot"
APP_NAME="customgpt-teams-bot-app"
PLAN_NAME="customgpt-bot-plan"

# Login to Azure
az login

# Create resource group
az group create --name $RG_NAME --location $LOCATION

# Create App Service Plan
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RG_NAME \
  --sku F1 \
  --is-linux

# Create Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --plan $PLAN_NAME \
  --runtime "PYTHON:3.11"

# Configure app settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings \
    TEAMS_APP_ID="your-app-id" \
    TEAMS_APP_PASSWORD="your-password" \
    CUSTOMGPT_API_KEY="your-api-key" \
    CUSTOMGPT_PROJECT_ID="your-project-id" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Create Bot Channel Registration
az bot create \
  --name $BOT_NAME \
  --resource-group $RG_NAME \
  --kind registration \
  --endpoint "https://$APP_NAME.azurewebsites.net/api/messages" \
  --appid "your-app-id" \
  --location $LOCATION

# Deploy code
az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RG_NAME

# Get deployment URL
az webapp deployment list-publishing-credentials \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --query scmUri \
  --output tsv
```

### Method 3: ARM Template Deployment

Create `azuredeploy.json`:
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "botName": {
      "type": "string",
      "defaultValue": "customgpt-teams-bot"
    },
    "customGptApiKey": {
      "type": "securestring"
    },
    "customGptProjectId": {
      "type": "string"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2021-02-01",
      "name": "[concat(parameters('botName'), '-plan')]",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "F1"
      },
      "properties": {
        "reserved": true
      }
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2021-02-01",
      "name": "[parameters('botName')]",
      "location": "[resourceGroup().location]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/serverfarms', concat(parameters('botName'), '-plan'))]"
      ],
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', concat(parameters('botName'), '-plan'))]",
        "siteConfig": {
          "linuxFxVersion": "PYTHON|3.11",
          "appSettings": [
            {
              "name": "CUSTOMGPT_API_KEY",
              "value": "[parameters('customGptApiKey')]"
            },
            {
              "name": "CUSTOMGPT_PROJECT_ID",
              "value": "[parameters('customGptProjectId')]"
            }
          ]
        }
      }
    }
  ]
}
```

Deploy:
```bash
az deployment group create \
  --resource-group $RG_NAME \
  --template-file azuredeploy.json \
  --parameters \
    customGptApiKey="your-key" \
    customGptProjectId="your-id"
```

## Post-Deployment Configuration

### 1. Configure Startup Command

In Azure Portal:
1. Go to Web App → Configuration → General settings
2. Set Startup command: `gunicorn --bind 0.0.0.0:8000 --timeout 600 app:app`

### 2. Enable Always On (Production)

For production deployments on paid tiers:
1. Go to Web App → Configuration → General settings
2. Set "Always on" to "On"

### 3. Configure Logging

1. Go to Web App → Monitoring → App Service logs
2. Enable:
   - Application logging: On
   - Level: Information
   - Web server logging: On
   - Retention: 30 days

### 4. Set up Application Insights

1. Go to Web App → Application Insights
2. Click "Turn on Application Insights"
3. Create new or use existing
4. Note the Instrumentation Key
5. Add to app settings: `APPLICATION_INSIGHTS_KEY`

### 5. Configure Custom Domain (Optional)

1. Go to Web App → Custom domains
2. Add custom domain
3. Configure SSL certificate
4. Update bot messaging endpoint in Bot Channel Registration

## Monitoring and Maintenance

### View Logs

```bash
# Stream logs
az webapp log tail --name $APP_NAME --resource-group $RG_NAME

# Download logs
az webapp log download --name $APP_NAME --resource-group $RG_NAME
```

### Application Insights Queries

```kusto
// Bot usage by user
customEvents
| where timestamp > ago(7d)
| where name == "BotMessageReceived"
| summarize count() by tostring(customDimensions.userId)
| order by count_ desc

// Error rate
requests
| where timestamp > ago(1h)
| summarize 
    total = count(),
    failed = countif(success == false)
| extend failureRate = failed * 100.0 / total
```

### Scaling

#### Manual Scaling
```bash
# Scale up to B1
az appservice plan update \
  --name $PLAN_NAME \
  --resource-group $RG_NAME \
  --sku B1

# Scale out to 3 instances
az webapp update \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --minimum-instances 1 \
  --maximum-instances 3
```

#### Auto-scaling Rules
1. Go to App Service Plan → Scale out
2. Enable autoscale
3. Add rules based on CPU, memory, or HTTP queue

## Security Best Practices

### 1. Key Vault Integration

```bash
# Create Key Vault
az keyvault create \
  --name "${BOT_NAME}-kv" \
  --resource-group $RG_NAME \
  --location $LOCATION

# Add secrets
az keyvault secret set \
  --vault-name "${BOT_NAME}-kv" \
  --name "CustomGptApiKey" \
  --value "your-api-key"

# Enable Managed Identity
az webapp identity assign \
  --name $APP_NAME \
  --resource-group $RG_NAME

# Grant access
az keyvault set-policy \
  --name "${BOT_NAME}-kv" \
  --object-id [identity-object-id] \
  --secret-permissions get list
```

### 2. Network Security

```bash
# Enable HTTPS only
az webapp update \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --https-only true

# Configure IP restrictions
az webapp config access-restriction add \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --rule-name "AllowTeams" \
  --action Allow \
  --ip-address "52.112.0.0/14" \
  --priority 100
```

### 3. Authentication

Enable Azure AD authentication:
1. Go to Web App → Authentication
2. Add identity provider → Microsoft
3. Configure as needed

## Troubleshooting

### Bot Not Responding

1. Check messaging endpoint in Bot Channel Registration
2. Verify app is running: `https://[app-name].azurewebsites.net/health`
3. Check logs for errors
4. Test in Bot Framework Emulator

### Deployment Failures

1. Check deployment logs in Deployment Center
2. Verify Python version compatibility
3. Check `requirements.txt` for conflicts
4. Enable detailed error messages temporarily

### Performance Issues

1. Check Application Insights for slow requests
2. Enable Always On for production
3. Scale up or out as needed
4. Implement Redis for distributed rate limiting

## Cost Optimization

### Free Tier Limitations
- 60 CPU minutes/day
- 1 GB storage
- No always-on
- No custom domains

### Cost Saving Tips
1. Use B1 instead of S1 for small deployments
2. Enable auto-scaling instead of fixed high tier
3. Use Application Insights sampling
4. Clean up old logs regularly

### Monthly Cost Estimates
- **Development**: $0 (F1 free tier)
- **Small Production**: ~$13/month (B1)
- **Medium Production**: ~$70/month (S1 + Redis)
- **Enterprise**: ~$200+/month (P1V2 + Redis + App Insights)

## Additional Resources

- [Bot Framework Documentation](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Teams App Development](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- [Azure Cost Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)