# Pages Metadata

## 1. Get the Metadata for a certain page
Retrieve the Metadata for a page based on its unique identifier. This endpoint allows you to fetch the metadata associated with a specific page.

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/pages/pageId/metadata \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "url": "https://www.example.com",
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
    "image": "https://www.example.com/image.png"
  }
}
```

### 400 response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "url": "https://www.example.com",
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
    "image": "https://www.example.com/image.png"
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

## 2. Update metadata for a certain page

Update the metadata for a specific page identified by its unique pageId. This endpoint allows you to update the associated metadata of the page.

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/pages/pageId/metadata \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "url": "https://www.example.com",
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
    "image": "https://www.example.com/image.png"
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