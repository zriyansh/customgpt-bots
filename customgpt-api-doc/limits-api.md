# Limits

## 1. Get user's agents, words and queries limit

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/limits/usage \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "max_projects_num": 10,
    "current_projects_num": 10,
    "max_total_storage_credits": 10,
    "current_total_storage_credits": 10,
    "max_queries": 10,
    "current_queries": 10
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