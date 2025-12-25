# Barrot API Documentation

## Overview

The Barrot API provides endpoints for managing users, chat messages, recordings, and sessions. The API is RESTful and returns JSON responses.

## Base URL

```
http://localhost:3000/api
```

For production:
```
https://barrot-agent.vercel.app/api
```

## Authentication

Currently, the API uses a simple user ID-based authentication. In production, you should implement proper JWT-based authentication.

## Response Format

All successful responses follow this format:
```json
{
  "data": { ... },
  "message": "Success message"
}
```

Error responses:
```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "ok",
  "message": "Barrot API is running"
}
```

---

### Chat Messages

#### Send Message

Send a message to the Barrot AI and receive a response.

**Endpoint:** `POST /api/chat/message`

**Request Body:**
```json
{
  "message": "How do I start streaming?",
  "userId": 1
}
```

**Response:**
```json
{
  "id": 1,
  "message": "How do I start streaming?",
  "response": "To start streaming, navigate to the Streaming section...",
  "timestamp": "2024-12-20T23:20:00.000Z"
}
```

#### Get Chat History

Retrieve chat message history for a user.

**Endpoint:** `GET /api/chat/history`

**Query Parameters:**
- `userId` (optional): Filter by user ID
- `limit` (optional, default: 50): Maximum number of messages

**Response:**
```json
{
  "messages": [
    {
      "id": 1,
      "user_id": 1,
      "message": "How do I start streaming?",
      "response": "To start streaming...",
      "created_at": "2024-12-20T23:20:00.000Z"
    }
  ]
}
```

---

### Users

#### Create User

Create a new user account.

**Endpoint:** `POST /api/users`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Error Codes:**
- `409`: User already exists

#### Get User

Retrieve user information by ID.

**Endpoint:** `GET /api/users/:id`

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-12-20T23:20:00.000Z"
}
```

---

### Recordings

#### Save Recording

Save metadata for a new recording.

**Endpoint:** `POST /api/recordings`

**Request Body:**
```json
{
  "userId": 1,
  "filename": "my-recording.webm",
  "filePath": "/recordings/recording-123.webm",
  "duration": 120
}
```

**Response:**
```json
{
  "id": 1,
  "filename": "my-recording.webm",
  "filePath": "/recordings/recording-123.webm",
  "duration": 120
}
```

#### Get Recordings

Retrieve list of recordings.

**Endpoint:** `GET /api/recordings`

**Query Parameters:**
- `userId` (optional): Filter by user ID
- `limit` (optional, default: 50): Maximum number of recordings

**Response:**
```json
{
  "recordings": [
    {
      "id": 1,
      "user_id": 1,
      "filename": "my-recording.webm",
      "file_path": "/recordings/recording-123.webm",
      "duration": 120,
      "created_at": "2024-12-20T23:20:00.000Z"
    }
  ]
}
```

---

### Sessions

#### Create Session

Create a new user session.

**Endpoint:** `POST /api/sessions`

**Request Body:**
```json
{
  "userId": 1
}
```

**Response:**
```json
{
  "sessionId": 1,
  "sessionToken": "abc123def456...",
  "expiresAt": "2024-12-21T23:20:00.000Z"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Missing or invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider adding rate limiting to prevent abuse.

## CORS

CORS is enabled for all origins in development. In production, configure specific allowed origins.

## Example Usage

### JavaScript (Fetch API)

```javascript
// Send a chat message
async function sendChatMessage(message) {
  const response = await fetch('http://localhost:3000/api/chat/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      userId: 1
    })
  });
  
  const data = await response.json();
  return data;
}

// Get chat history
async function getChatHistory(userId) {
  const response = await fetch(`http://localhost:3000/api/chat/history?userId=${userId}`);
  const data = await response.json();
  return data.messages;
}
```

### cURL

```bash
# Health check
curl http://localhost:3000/api/health

# Send chat message
curl -X POST http://localhost:3000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I start streaming?","userId":1}'

# Create user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com"}'

# Get recordings
curl "http://localhost:3000/api/recordings?userId=1&limit=10"
```

## Future Enhancements

- JWT-based authentication
- WebSocket support for real-time chat
- File upload endpoints for recordings
- User profile management
- Recording playback streaming
- Advanced search and filtering
- Rate limiting
- API versioning

## Support

For issues or questions, please open an issue on GitHub or contact the maintainers.
