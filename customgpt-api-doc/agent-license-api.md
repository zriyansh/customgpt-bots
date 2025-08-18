# Agent License

## 1. Returns a list of licenses for a specific agent

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/licenses \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": [
    {
      "name": "My License",
      "key": "123e4567-e89b-12d3-a456-426614174000",
      "project_id": 7,
      "created_at": "2021-01-01 00:00:00",
      "updated_at": "2021-01-01 00:00:00"
    }
  ]
}
```

### 400 response

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

## 2. Create a new license for an agent
Creates a new license for a specific agent.

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/licenses \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 201 Response

```json
{
  "status": "success",
  "data": {
    "license": {
      "name": "My License",
      "key": "123e4567-e89b-12d3-a456-426614174000",
      "project_id": 7,
      "created_at": "2021-01-01 00:00:00",
      "updated_at": "2021-01-01 00:00:00"
    },
    "licenseKey": "123e4567-e89b-12d3-a456-426614174000"
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

### 422 response

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

## 3. Get a license for an agent
Returns a specific license that belongs to a specific agent.

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/licenses/licenseId \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "license": {
    "name": "My License",
    "key": "123e4567-e89b-12d3-a456-426614174000",
    "project_id": 7,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00"
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
    "message": "Agent license with id 1 not found"
  }
}
```

### 422 response

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

## 4. Update a license for an agent

Updates the name of a specific license that belongs to a specific agent.

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/licenses/licenseId \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "license": {
    "name": "My License",
    "key": "123e4567-e89b-12d3-a456-426614174000",
    "project_id": 7,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00"
  }
}
```

### 400 response

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
    "message": "Agent license with id 1 not found"
  }
}
```

### 422 response

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

## 5. Delete a license for an agent

Deletes a specific license that belongs to a specific agent.

```bash
curl --request DELETE \
     --url https://app.customgpt.ai/api/v1/projects/projectId/licenses/licenseId \
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
    "message": "Agent license with id 1 not found"
  }
}
```

### 422 response

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