# Pages API

## 1. List all pages that belong to an agent

Retrieve a list of all pages associated with an agent (formerly known as project). This endpoint allows you to fetch agent details and a collection of pages that belong to a specific agent. Each page object includes information such as the page ID, URL, hash of the URL, agent ID, crawl status, index status, file details (if applicable), creation and update timestamps, and other relevant attributes

```bash
curl --request GET \
     --url 'https://app.customgpt.ai/api/v1/projects/projectId/pages?page=1&limit=20&order=desc&crawl_status=all&index_status=all' \
     --header 'accept: application/json'
```

### 200 response:

```json
{
  "status": "success",
  "data": {
    "project": {
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
    },
    "pages": {
      "current_page": 1,
      "data": [
        {
          "id": 1,
          "page_url": "https://example.com",
          "page_url_hash": "d41d8cd98f00b204e9800998ecf8427e",
          "project_id": 1,
          "s3_path": "project-1/page-1/file.pdf",
          "crawl_status": "queued",
          "index_status": "queued",
          "is_file": true,
          "is_refreshable": true,
          "is_file_kept": true,
          "filename": "file.pdf",
          "filesize": 100,
          "created_at": "2021-01-01 00:00:00",
          "updated_at": "2021-01-01 00:00:00",
          "deleted_at": "2021-01-01 00:00:00"
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

### 400 response:

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

### 500 response

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

## 2. Delete a certain page that belongs to a certain agent
Delete a specific page within an agent (formerly known as project) based on its unique projectId and pageId. This endpoint allows you to remove a particular page from the agent, permanently deleting its associated context

```bash
curl --request DELETE \
     --url https://app.customgpt.ai/api/v1/projects/projectId/pages/pageId \
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

## 3. Reindex a certain page that belongs to a certain agent
Reindex a specific page within an agent (formerly known as project) based on its unique projectId and pageId. This endpoint allows you to refresh a particular page from the agent. Our system will crawl and index page content newly

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/pages/pageId/reindex \
     --header 'accept: application/json'
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

### 403 response

```json
{
  "status": "error",
  "url": "https://app.customgpt.ai/api/v1/projects/1",
  "data": {
    "code": 400,
    "message": "The Document with the id 1 couldn't have been updated"
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

## 4. Preview file from citation

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/preview/id \
     --header 'accept: application/json'
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
    "message": "Page with id 1 not found"
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