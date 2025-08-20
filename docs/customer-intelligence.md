# Customer Intelligence

## Get customer intelligence analytics data for a project

Retrieves comprehensive customer intelligence data including user interactions, emotions, intents, feedback, and behavioral analytics for the specified project.

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId/reports/intelligence?page=1&limit=100' \
     --header 'accept: application/json'
```

### 1. 200 Response

```json
{
  "status": "success",
  "data": {
    "current_page": 1,
    "data": [
      {
        "prompt_id": 0,
        "conversation_id": 0,
        "project_id": 0,
        "user_query": "string",
        "ai_response": "string",
        "created_at": "string",
        "content_source": "string",
        "user_emotion": "string",
        "user_intent": "string",
        "language": "string",
        "feedback": "string",
        "user_location": "string",
        "chatbot_deployment": "string",
        "browser": "string"
      }
    ],
    "first_page_url": "https://app.customgpt.ai/api/v1/users?page=1",
    "from": 1,
    "last_page": 1,
    "last_page_url": "https://app.customgpt.ai/api/v1/users?page=1",
    "next_page_url": "https://app.customgpt.ai/api/v1/users?page=1",
    "path": "https://app.customgpt.ai/api/v1/users?page=1",
    "per_page": 10,
    "prev_page_url": "https://app.customgpt.ai/api/v1/users?page=1",
    "to": 1,
    "total": 1
  }
}
```

### 400 Response

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

### 401 Response

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

### 500 Response

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
