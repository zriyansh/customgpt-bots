# Citations

## 1. Get the Open Graph data for a citation

Retrieve the Open Graph data for a citation based on its unique identifier. This endpoint allows you to fetch the Open Graph metadata associated with a specific citation.

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/citations/citationId \
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