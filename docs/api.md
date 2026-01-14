# AI Krushi Mitra – API Documentation

Base URL:
http://localhost:8000

---

## Health Check API

Endpoint:
GET /health

Description:
Checks whether backend is running.

Response:
{
"status": "ok",
"message": "Backend healthy"
}

---

## Ask Question API

Endpoint:
POST /ask

Description:
Accepts a farmer question and returns AI-generated advice.

Request Body:
{
"question": "Stunted growth and pale leaves in cotton "
}

Response:
{
"question": "Stunted growth and pale leaves in cotton",
"answer": "Problem: ...\nReason: ...\nSolution: ...\nPrevention: ..."
}

Notes:

- Supports Telugu, Hindi, and English
- Includes safety disclaimer
