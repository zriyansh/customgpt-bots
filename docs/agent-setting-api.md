# Agent Setting

## 1. Get agent settings
Retrieve the agent (formerly known as project) settings for a specific agent. This endpoint allows you to fetch the configuration and settings associated with the project

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/settings \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "chatbot_avatar": "https://example.com/agent_avatar.png",
    "chatbot_background_type": "image",
    "chatbot_background": "https://example.com/agent_background.png",
    "chatbot_background_color": "#F5F5F5",
    "default_prompt": "How can I help you?",
    "example_questions": [
      "How do I get started?"
    ],
    "response_source": "own_content",
    "chatbot_msg_lang": "en",
    "chatbot_color": "#000000",
    "chatbot_toolbar_color": "#000000",
    "persona_instructions": "You are a custom agent assistant called CustomGPT.ai, a friendly lawyer who answers questions based on the given context.",
    "citations_answer_source_label_msg": "Where did this answer come from?",
    "citations_sources_label_msg": "Sources",
    "hang_in_there_msg": "Hang in there! I'm thinking..",
    "chatbot_siesta_msg": "Oops! The agent is taking a siesta. We are aware of this and will get it back soon! Please try again later.",
    "is_loading_indicator_enabled": true,
    "enable_citations": 3,
    "enable_feedbacks": true,
    "citations_view_type": "user",
    "image_citation_display": "default",
    "no_answer_message": "Sorry, I don't have an answer for that.",
    "ending_message": "Please email us for further support",
    "try_asking_questions_msg": "Try asking these questions...",
    "view_more_msg": "View more",
    "view_less_msg": "View less",
    "remove_branding": false,
    "private_deployment": false,
    "enable_recaptcha_for_public_chatbots": false,
    "chatbot_model": "gpt-4-o",
    "is_selling_enabled": false,
    "license_slug": true,
    "selling_url": "string",
    "can_share_conversation": false,
    "can_export_conversation": false,
    "hide_sources_from_responses": true,
    "input_field_addendum": "",
    "user_avatar": "avatar.png",
    "spotlight_avatar_enabled": false,
    "spotlight_avatar": "spotlight_avatar.png",
    "spotlight_avatar_shape": "rectangle",
    "spotlight_avatar_type": "default",
    "user_avatar_orientation": "agent-left-user-right",
    "chatbot_title": "",
    "chatbot_title_color": "#000000",
    "enable_inline_citations_api": false,
    "conversation_time_window": false,
    "conversation_retention_period": "year",
    "conversation_retention_days": 180,
    "enable_agent_knowledge_base_awareness": true,
    "markdown_enabled": true
  }
}
```

### 400 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 400,
    "message": "Agent id must be integer"
  }
}
```

### 401 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 400,
    "message": "Agent id must be integer"
  }
}
```

### 404 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 404,
    "message": "Agent with id 1 not found"
  }
}
```

### 500 response:

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 500,
    "message": "Internal Server Error"
  }
}
```

## 2. Update agent settings

Update the agent (formerly known as project) settings for a specific agent. This endpoint allows you to update the configuration and settings associated with the agent

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/settings \
     --header 'accept: application/json' \
     --header 'content-type: multipart/form-data' \
     --form is_loading_indicator_enabled=true \
     --form enable_citations=3 \
     --form enable_feedbacks=true \
     --form citations_view_type=user \
     --form image_citation_display=default \
     --form 'no_answer_message=I'\''m sorry, I don'\''t know the answer' \
     --form 'try_asking_questions_msg=Try asking these questions...' \
     --form 'view_more_msg=View more' \
     --form 'view_less_msg=View less' \
     --form remove_branding=false \
     --form enable_recaptcha_for_public_chatbots=false \
     --form is_selling_enabled=false \
     --form can_share_conversation=false \
     --form can_export_conversation=false \
     --form hide_sources_from_responses=true \
     --form spotlight_avatar_enabled=false \
     --form spotlight_avatar=spotlight_avatar.png \
     --form spotlight_avatar_shape=rectangle \
     --form spotlight_avatar_type=default \
     --form user_avatar_orientation=agent-left-user-right \
     --form 'chatbot_title_color=#000000' \
     --form enable_inline_citations_api=false \
     --form conversation_time_window=false \
     --form conversation_retention_period=year \
     --form conversation_retention_days=0 \
     --form enable_agent_knowledge_base_awareness=true \
     --form markdown_enabled=true
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "updated": true
  }
}
```

### 400 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 400,
    "message": "Please upload a valid image file for avatar"
  }
}
```

### 401 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 401,
    "message": "API Token is either missing or invalid"
  }
}
```

### 500 response:

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 500,
    "message": "Internal Server Error"
  }
}
```