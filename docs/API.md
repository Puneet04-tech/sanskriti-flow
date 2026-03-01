# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (development mode).

---

## Endpoints

### Health Check

#### `GET /health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

### Create Localization Job

#### `POST /api/v1/localize/`
Submit a video for localization.

**Request Body:**
```json
{
  "video_url": "https://example.com/lecture.mp4",
  "target_language": "hi",
  "enable_quiz": true,
  "enable_vision_sync": true,
  "enable_lip_sync": false,
  "enable_swar": false,
  "enable_drishti": false,
  "preserve_technical_terms": true
}
```

**Parameters:**
- `video_url` (string, optional): URL of video to process
- `video_file` (string, optional): Local path to video file
- `target_language` (string, required): Language code (hi, ta, te, bn, mr, gu, kn, ml, pa, or)
- `enable_quiz` (boolean): Generate interactive quizzes
- `enable_vision_sync` (boolean): Add vision-sync overlays
- `enable_lip_sync` (boolean): Apply lip-sync
- `enable_swar` (boolean): Add assistive audio
- `enable_drishti` (boolean): Enable rural/edge mode
- `preserve_technical_terms` (boolean): Keep technical terms in English

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Job queued for processing. Target language: hi"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing parameters)
- `500`: Server error

---

### Upload Video

#### `POST /api/v1/localize/upload`
Upload video file directly.

**Form Data:**
- `file` (file, required): Video file
- `target_language` (string, required): Language code
- `enable_quiz` (boolean): Generate quizzes
- `enable_vision_sync` (boolean): Add overlays
- `enable_lip_sync` (boolean): Apply lip-sync

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "message": "Video uploaded and queued. Target language: hi"
}
```

---

### Get Job Status

#### `GET /api/v1/jobs/{job_id}`
Check the status of a localization job.

**Path Parameters:**
- `job_id` (string, required): Job identifier

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45.5,
  "stage": "Translating transcript",
  "eta_seconds": 120,
  "result_url": null,
  "error": null
}
```

**Status Values:**
- `queued`: Job is waiting to start
- `processing`: Job is being processed
- `completed`: Job finished successfully
- `failed`: Job encountered an error

---

### Cancel Job

#### `DELETE /api/v1/jobs/{job_id}`
Cancel a running job.

**Path Parameters:**
- `job_id` (string, required): Job identifier

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Job cancelled"
}
```

---

### List All Jobs

#### `GET /api/v1/jobs/`
List all jobs (admin/debugging).

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "progress": 100
    }
  ],
  "total": 1
}
```

---

## Language Codes

| Code | Language |
|------|----------|
| `hi` | Hindi (हिंदी) |
| `ta` | Tamil (தமிழ்) |
| `te` | Telugu (తెలుగు) |
| `bn` | Bengali (বাংলা) |
| `mr` | Marathi (मराठी) |
| `gu` | Gujarati (ગુજરાતી) |
| `kn` | Kannada (ಕನ್ನಡ) |
| `ml` | Malayalam (മലയാളം) |
| `pa` | Punjabi (ਪੰਜਾਬੀ) |
| `or` | Odia (ଓଡ଼ିଆ) |

---

## Error Handling

All endpoints return standard HTTP status codes:

**400 Bad Request:**
```json
{
  "detail": "Either video_url or video_file must be provided"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "Translation service unavailable"
}
```

---

## Rate Limiting

Not currently implemented. In production:
- 100 requests per minute per IP
- 10 concurrent jobs per user

---

## Examples

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/localize/",
    json={
        "video_url": "https://example.com/lecture.mp4",
        "target_language": "hi",
        "enable_quiz": True,
    }
)

job_id = response.json()["job_id"]
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/localize/" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/lecture.mp4",
    "target_language": "hi",
    "enable_quiz": true
  }'
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/localize/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_url: 'https://example.com/lecture.mp4',
    target_language: 'hi',
    enable_quiz: true,
  }),
});

const { job_id } = await response.json();
```

---

## Interactive Documentation

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI documentation.
