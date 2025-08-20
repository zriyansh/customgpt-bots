# Sources

## 1. List a certain agent's sources

Retrieve a list of all sources associated with a given agent (formerly known as project). This endpoint provides a collection of sources that are linked to a specific agent. Sources serve as references or contexts for the agent.

```bash
curl --request GET \
     --url https://app.customgpt.ai/api/v1/projects/projectId/sources \
     --header 'accept: application/json'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "sitemaps": [
      {
        "id": 1,
        "created_at": "2021-01-01 00:00:00",
        "updated_at": "2021-01-01 00:00:00",
        "type": "sitemap",
        "settings": {
          "executive_js": true,
          "data_refresh_frequency": "never",
          "create_new_pages": true,
          "remove_unexist_pages": false,
          "refresh_existing_pages": "never",
          "sitemap_path": "https://example.com/sitemap.xml"
        },
        "pages": [
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
        ]
      }
    ],
    "uploads": {
      "id": 1,
      "created_at": "2021-01-01 00:00:00",
      "updated_at": "2021-01-01 00:00:00",
      "type": "sitemap",
      "settings": {
        "executive_js": true,
        "data_refresh_frequency": "never",
        "create_new_pages": true,
        "remove_unexist_pages": false,
        "refresh_existing_pages": "never",
        "sitemap_path": "https://example.com/sitemap.xml"
      },
      "pages": [
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
      ]
    }
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

## 2. Create a new agent source

Create a new data source for a given agent (formerly known as project), allowing you to add additional context by specifying a sitemap URL or uploading a file. This endpoint enables you to enrich the agent's information by incorporating relevant data sources.

```bash
curl --request POST \
     --url https://app.customgpt.ai/api/v1/projects/projectId/sources \
     --header 'accept: application/json' \
     --header 'content-type: multipart/form-data'
```

### 201 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "type": "sitemap",
    "settings": {
      "executive_js": true,
      "data_refresh_frequency": "never",
      "create_new_pages": true,
      "remove_unexist_pages": false,
      "refresh_existing_pages": "never",
      "sitemap_path": "https://example.com/sitemap.xml"
    },
    "pages": [
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
    ]
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
    "message": "Sitemap URL is empty"
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

## 3. Update agent source settings

Update a data source settings, allowing you to change additional settings.

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/sources/sourceId \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "executive_js": true,
  "data_refresh_frequency": "never",
  "create_new_pages": true,
  "remove_unexist_pages": true,
  "refresh_existing_pages": "never"
}
'
```

### 200 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "type": "sitemap",
    "settings": {
      "executive_js": true,
      "data_refresh_frequency": "never",
      "create_new_pages": true,
      "remove_unexist_pages": false,
      "refresh_existing_pages": "never",
      "sitemap_path": "https://example.com/sitemap.xml"
    },
    "pages": [
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
    ]
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
    "message": "Agent source with id 1 not found"
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

## 4. Delete an agent source
Delete a source for a given agent.

```bash
curl --request DELETE \
     --url https://app.customgpt.ai/api/v1/projects/projectId/sources/sourceId \
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

## 5. Instant sync the specified sitemap

```bash
curl --request PUT \
     --url https://app.customgpt.ai/api/v1/projects/projectId/sources/sourceId/instant-sync \
     --header 'accept: application/json'
```

### 201 Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "created_at": "2021-01-01 00:00:00",
    "updated_at": "2021-01-01 00:00:00",
    "type": "sitemap",
    "settings": {
      "executive_js": true,
      "data_refresh_frequency": "never",
      "create_new_pages": true,
      "remove_unexist_pages": false,
      "refresh_existing_pages": "never",
      "sitemap_path": "https://example.com/sitemap.xml"
    },
    "pages": [
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
    ]
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
    "message": "Agent source with id 1 not found"
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