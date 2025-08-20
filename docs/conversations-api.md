# Conversations

## 1. List all conversations for an agent (formerly known as project)

Retrieve all conversations associated with an agent based on its unique projectId. This endpoint allows you to fetch a collection of conversations related to a specific agent.

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId/conversations?page=1&order=desc&orderBy=id&userFilter=all' \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "current_page": 1,
    "data": [
      {
        "created_at": "2023-04-30 16:43:53",
        "updated_at": "2023-04-30 16:43:53",
        "deleted_at": "2023-04-30 16:43:53",
        "id": 1,
        "name": "Conversation 1",
        "project_id": 1,
        "created_by": 1,
        "session_id": "f1b9aaf0-5e4e-11eb-ae93-0242ac130002"
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

## 2. Create a new conversation
Create a new conversation for an agent (formerly known as project) identified by its unique projectId. This endpoint allows you to initiate a new conversation within a specific agent. A conversation serves as a platform for users to exchange messages regarding agent-related matters. By providing the projectId, you can establish a conversation within the context of the agent allowing you to seamlessly communicate with it. 

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/conversations \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 201 Response

```json
{
  "status": "success",
  "data": {
    "created_at": "2023-04-30 16:43:53",
    "updated_at": "2023-04-30 16:43:53",
    "deleted_at": "2023-04-30 16:43:53",
    "id": 1,
    "name": "Conversation 1",
    "project_id": 1,
    "created_by": 1,
    "session_id": "f1b9aaf0-5e4e-11eb-ae93-0242ac130002"
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

## 3. Update a conversation

Update a conversation within an agent (formerly known as project) identified by its unique projectId and sessionId. This endpoint allows you to modify and update the properties of a specific conversation. By providing the projectId and sessionId, you can target the desired conversation and make changes to its attributes

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "created_at": "2023-04-30 16:43:53",
    "updated_at": "2023-04-30 16:43:53",
    "deleted_at": "2023-04-30 16:43:53",
    "id": 1,
    "name": "Conversation 1",
    "project_id": 1,
    "created_by": 1,
    "session_id": "f1b9aaf0-5e4e-11eb-ae93-0242ac130002"
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

## 4. Delete a conversation

Delete a conversation within an agent (formerly known as project) identified by its unique projectId and sessionId. This endpoint allows you to remove a specific conversation from the agent, permanently deleting all associated messages. By providing the projectId and sessionId, you can target the conversation to be deleted, ensuring the removal of all conversation-related data

```bash
curl --request DELETE \
     --url https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "deleted": true
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

## 5. Retrieve messages that have been sent in a conversation

Retrieve all messages sent within a conversation of an agent (formerly known as project) identified by its unique projectId and sessionId. This endpoint allows you to retrieve a collection of messages exchanged in a specific conversation. Messages contain the content, timestamps, and other relevant information shared during the course of the conversation. By providing the projectId and sessionId, you can access all the messages associated with that particular conversation within the agent context

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId/messages?page=1&order=desc' \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "conversation": {
      "created_at": "2023-04-30 16:43:53",
      "updated_at": "2023-04-30 16:43:53",
      "deleted_at": "2023-04-30 16:43:53",
      "id": 1,
      "name": "Conversation 1",
      "project_id": 1,
      "created_by": 1,
      "session_id": "f1b9aaf0-5e4e-11eb-ae93-0242ac130002"
    },
    "messages": {
      "current_page": 1,
      "data": [
        {
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

## 6. Send a message to a conversation

Send a message to a conversation within an agent (formerly known as project) identified by its unique projectId and sessionId. This endpoint enables you to send a new message to a specific conversation, facilitating seamless communication and collaboration within the agent. By providing the projectId and sessionId, you can target the desired conversation and contribute to the ongoing discussion. This API endpoint supports real-time streaming, allowing for instant message delivery and dynamic updates which enables efficient and interactive communication between the user and agent.

```bash
curl --request POST \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId/conversations/sessionId/messages?stream=false&lang=en' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "response_source": "default"
}
'
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
    "message": "Agent with id 1 not found"
  }
}
```

### 429 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 429,
    "message": "You have exhausted your current query credits. Please contact customer service (https://customgpt.freshdesk.com/support/home) for further assistance."
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

## 7. Send a message to a conversation in openai format

Send a message to a conversation within an agent (formerly known as project) identified by its unique projectId and sessionId. This endpoint enables you to send a new message to a specific conversation, facilitating seamless communication and collaboration within the agent. By providing the projectId and sessionId, you can target the desired conversation and contribute to the ongoing discussion. This API endpoint supports real-time streaming, allowing for instant message delivery and dynamic updates which enables efficient and interactive communication between the user and agent

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/chat/completions \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "stream": false,
  "lang": "en",
  "is_inline_citation": false
}
'
```

### 200 Response

```json
{
  "id": "176",
  "object": "chat.completion",
  "created": 1743037634,
  "model": "string",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
      },
      "logprobs": "string",
      "finish_reason": "stop",
      "index": 0
    }
  ]
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
    "message": "Agent with id 1 not found"
  }
}
```

### 429 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 429,
    "message": "You have exhausted your current query credits. Please contact customer service (https://customgpt.freshdesk.com/support/home) for further assistance."
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

### 501 response:

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 501,
    "message": "audio is not yet supported. Please remove them from your request and try again."
  }
}
```