# Messeges

## 1. Get a message by message ID

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId/messages/promptId \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "user_query": "What is the meaning of life?",
    "openai_response": "The meaning of life is to be happy.",
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "conversation_id": 1,
    "citations": [
      1,
      2,
      3
    ],
    "metadata": {
      "user_ip": "127.0.0.1",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
      "external_id": "ext_id_1234567890",
      "request_source": "web"
    },
    "response_feedback": {
      "created_at": "2024-08-27T21:07:20.000000Z",
      "updated_at": "2024-08-27T21:07:20.000000Z",
      "user_id": 1,
      "reaction": "liked"
    }
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
    "code": 401,
    "message": "API Token is either missing or invalid"
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
    "message": "Conversation message with id 1 not found"
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

## 2. Update the reaction for a specific message

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId/messages/promptId/feedback \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "user_query": "What is the meaning of life?",
    "openai_response": "The meaning of life is to be happy.",
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "conversation_id": 1,
    "citations": [
      1,
      2,
      3
    ],
    "metadata": {
      "user_ip": "127.0.0.1",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
      "external_id": "ext_id_1234567890",
      "request_source": "web"
    },
    "response_feedback": {
      "created_at": "2024-08-27T21:07:20.000000Z",
      "updated_at": "2024-08-27T21:07:20.000000Z",
      "user_id": 1,
      "reaction": "liked"
    }
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
    "code": 401,
    "message": "API Token is either missing or invalid"
  }
}
```

### 404 response

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
    "code": 401,
    "message": "API Token is either missing or invalid"
  }
}
```