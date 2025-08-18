# Users

## 1. Show the user's profile

Retrieve the profile information of the current user. This endpoint allows you to fetch the details and attributes associated with the user's profile, providing valuable information about the user's account and preferences.

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/user \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "created_at": "2023-04-30 16:43:53",
    "email": "user@domain.com",
    "id": 1,
    "current_team_id": 1,
    "name": "John Doe",
    "profile_photo_url": "https://app.customgpt.ai/user/1/profile_photo_url",
    "updated_at": "2023-04-30 16:43:53"
  }
}
```

### 400 response

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

## 2. Update the user's profile

Update the profile of the current user. This endpoint allows the user to modify and update their profile information and preferences within the application or system

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/user \
     --header 'accept: application/json' \
     --header 'content-type: multipart/form-data'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "created_at": "2023-04-30 16:43:53",
    "email": "user@domain.com",
    "id": 1,
    "current_team_id": 1,
    "name": "John Doe",
    "profile_photo_url": "https://app.customgpt.ai/user/1/profile_photo_url",
    "updated_at": "2023-04-30 16:43:53"
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