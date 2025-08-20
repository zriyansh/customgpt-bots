# Agents

## 1. List all agents

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects?page=1&order=desc&orderBy=id&width=100%25&height=auto' \
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
        "id": 1,
        "project_name": "My Agent",
        "sitemap_path": "https://www.example.com/sitemap.xml",
        "is_chat_active": true,
        "user_id": 1,
        "team_id": 1,
        "created_at": "2021-01-01 00:00:00",
        "updated_at": "2021-01-01 00:00:00",
        "deleted_at": "2021-01-01 00:00:00",
        "type": "SITEMAP",
        "is_shared": true,
        "shareable_slug": "1234567890abcdef1234567890abcdef",
        "shareable_link": "string",
        "embed_code": "string",
        "live_chat_code": "string",
        "are_licenses_allowed": true
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

## 2. Create a new agent

Create a new agent by importing data either from a sitemap or an uploaded file. This endpoint enables you to initiate the creation of a new agent by supplying the necessary agent data that will be used as the context. You can choose to import the agent knowledge and content from a sitemap url or upload a specific file format that contains the context can be any text, audio or video format. The system will process the provided data and generate a new agent based on the imported or uploaded information.

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects \
     --header 'accept: application/json' \
     --header 'content-type: multipart/form-data'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "project_name": "My Agent",
    "sitemap_path": "https://www.example.com/sitemap.xml",
    "is_chat_active": true,
    "user_id": 1,
    "team_id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "deleted_at": "2021-01-01 00:00:00",
    "type": "SITEMAP",
    "is_shared": true,
    "shareable_slug": "1234567890abcdef1234567890abcdef",
    "shareable_link": "string",
    "embed_code": "string",
    "live_chat_code": "string",
    "are_licenses_allowed": true
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
    "message": "Agent name can't be empty"
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

## 3. Show a certain agent

Retrieve details of an agent (formerly known as project) based on its unique project ID. This endpoint allows you to fetch specific information about an agent

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId?width=100%25&height=auto' \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "project_name": "My Agent",
    "sitemap_path": "https://www.example.com/sitemap.xml",
    "is_chat_active": true,
    "user_id": 1,
    "team_id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "deleted_at": "2021-01-01 00:00:00",
    "type": "SITEMAP",
    "is_shared": true,
    "shareable_slug": "1234567890abcdef1234567890abcdef",
    "shareable_link": "string",
    "embed_code": "string",
    "live_chat_code": "string",
    "are_licenses_allowed": true
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

## 4. Update a certain agent

Update an agent (formerly known as project) with specific details based on its unique projectId. This endpoint allows you to modify and revise the information associated with a particular agent

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId \
     --header 'accept: application/json' \
     --header 'content-type: multipart/form-data' \
     --form are_licenses_allowed=false
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "project_name": "My Agent",
    "sitemap_path": "https://www.example.com/sitemap.xml",
    "is_chat_active": true,
    "user_id": 1,
    "team_id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "deleted_at": "2021-01-01 00:00:00",
    "type": "SITEMAP",
    "is_shared": true,
    "shareable_slug": "1234567890abcdef1234567890abcdef",
    "shareable_link": "string",
    "embed_code": "string",
    "live_chat_code": "string",
    "are_licenses_allowed": true
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

## 5. Delete a certain agent
Delete an agent (formerly known as project) by its unique project ID. This endpoint allows you to remove an existing agent from the system based on its ID

```bash
curl --request DELETE \
     --url https://app.customgpt.ai/api/v1/projects/projectId \
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

## 6. Replicate agent by given ID

Replicate an agent (formerly known as project) by copying the agent info, settings, sitemap sources and uploaded files. This endpoint enables you to initiate the replication of an agent by supplying the necessary ID. The system will process the replicated data and generate a new agent based on the information of existing agent.

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/replicate \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "project_name": "My Agent",
    "sitemap_path": "https://www.example.com/sitemap.xml",
    "is_chat_active": true,
    "user_id": 1,
    "team_id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "deleted_at": "2021-01-01 00:00:00",
    "type": "SITEMAP",
    "is_shared": true,
    "shareable_slug": "1234567890abcdef1234567890abcdef",
    "shareable_link": "string",
    "embed_code": "string",
    "live_chat_code": "string",
    "are_licenses_allowed": true
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
    "message": "Agent name can't be empty"
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

## 7. Get the stats for a certain agent
Retrieve statistical data for an agent (formerly known as project) using its unique projectId. This endpoint provides extensive statistics about the agent's performance, activity, or other relevant metrics

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/stats \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "pages_found": 100,
    "pages_crawled": 100,
    "pages_indexed": 100,
    "crawl_credits_used": 100,
    "query_credits_used": 100,
    "total_queries": 100,
    "total_words_indexed": 100,
    "total_storage_credits_used": 100
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