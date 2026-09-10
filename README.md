# N?XIS API Gateway

A lightweight, OpenRouter-style API gateway that exposes a unified, OpenAI-compatible API while routing requests to 14 public upstream AI endpoints.

## Architecture

```
Client -> N?XIS Gateway -> Upstream Provider
                              |-- AI Detector
                              |-- Gemini
                              |-- DALL-E
                              |-- GPT-3
                              |-- Bible AI
                              |-- DeepSeek R1
                              |-- DeepSeek V3
                              |-- Cohere
                              |-- Llama Meta
                              |-- Qwen
                              |-- GPT-5
                              |-- Deep AI
                              |-- GPTLogic
                              |-- Copilot
```

The gateway normalizes all upstream responses into a consistent OpenAI-compatible format.

## Project Structure

```
noxis-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── config.py           # Environment configuration
│   ├── auth.py             # API key authentication
│   ├── schemas.py          # Pydantic models
│   ├── router.py           # Provider routing + fallback
│   ├── normalizer.py       # Response normalization
│   └── providers/
│       ├── __init__.py
│       ├── base.py         # Base adapter
│       ├── ai_detector.py
│       ├── gemini.py
│       ├── dalle.py
│       ├── gpt3.py
│       ├── bible_ai.py
│       ├── deepseek_r1.py
│       ├── deepseek_v3.py
│       ├── cohere.py
│       ├── llama_meta.py
│       ├── qwen.py
│       ├── gpt5.py
│       ├── deep_ai.py
│       ├── gptlogic.py
│       └── copilot.py
├── web/
│   └── index.html          # API directory page
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── Dockerfile
├── README.md
└── test_gateway.py
```

## Installation

```bash
git clone <repo-url>
cd noxis-gateway
cp .env.example .env
pip install -r requirements.txt
```

## Local Execution

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit `http://127.0.0.1:8000` for the endpoint directory.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NOXIS_API_KEYS` | (empty) | Comma-separated API keys. Empty = auth disabled |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `UPSTREAM_TIMEOUT` | `45` | Upstream request timeout in seconds |
| `MAX_PROVIDER_ATTEMPTS` | `3` | Max fallback attempts for `auto` model |
| `DAS_APIA_BASE` | `https://das-apia.netlify.app` | Upstream base URL |

## Authentication

Set `NOXIS_API_KEYS` to enable API key authentication:

```bash
NOXIS_API_KEYS=my-secret-key
# or multiple
NOXIS_API_KEYS=key1,key2,key3
```

Clients authenticate with:

```
Authorization: Bearer YOUR_NOXIS_API_KEY
```

If `NOXIS_API_KEYS` is empty, authentication is disabled (useful for local development).

**For public deployments, always enable authentication.**

## API Examples

### Chat Completions

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v3",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### List Models

```bash
curl http://127.0.0.1:8000/v1/models
```

### Image Generation

```bash
curl http://127.0.0.1:8000/v1/images/generations \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a futuristic black AI interface"}'
```

### AI Detection

```bash
curl "http://127.0.0.1:8000/v1/detect?text=This+is+some+text+to+check"
```

### Bible AI

```bash
curl "http://127.0.0.1:8000/v1/bible?query=Who+is+Jesus"
```

## Model Names

| Model Name | Provider |
|---|---|
| `ai-detector` | AI Detector |
| `gemini` | Google Gemini |
| `dall-e` | DALL-E |
| `gpt3` | GPT-3 |
| `bible-ai` | Bible AI |
| `deepseek-r1` | DeepSeek R1 |
| `deepseek-v3` | DeepSeek V3 |
| `cohere` | Cohere |
| `llama-meta` | Llama Meta |
| `qwen` | Qwen |
| `gpt-5` | GPT-5 |
| `deep-ai` | Deep AI |
| `gptlogic` | GPTLogic |
| `copilot` | Copilot |
| `auto` | Fallback chain |

## Provider Mapping

Each provider adapter defines:
- Provider name
- Upstream path
- Query parameter name
- Optional additional parameters

Providers use HTTPX async requests with configurable timeouts.

## Render Deployment

1. Push this repo to GitHub
2. Create a new Web Service on Render
3. Connect your repo
4. Render will auto-detect `render.yaml`
5. Set `NOXIS_API_KEYS` in the Render dashboard
6. Deploy

Your gateway will be at `https://your-service.onrender.com`

## Docker Deployment

```bash
docker build -t noxis-gateway .
docker run -p 8000:8000 -e NOXIS_API_KEYS=your-key noxis-gateway
```

## Endpoint Directory

Visit the root URL (`/`) to see the N?XIS API Directory page with all endpoints and copy buttons.

## Running Tests

```bash
NOXIS_URL=http://127.0.0.1:8000 NOXIS_API_KEY=your-key python test_gateway.py
```

## Troubleshooting

- **401 Unauthorized**: Set `NOXIS_API_KEY` or check `NOXIS_API_KEYS`
- **502 Upstream Error**: The upstream provider may be down
- **504 Timeout**: Upstream took too long; increase `UPSTREAM_TIMEOUT`
- **Connection refused**: Ensure the server is running on the expected port

## Limitations

- Streaming is not supported (upstream providers don't support it)
- Upstream availability is not guaranteed
- The gateway is a routing/normalization layer, not an AI provider
- Response times depend on upstream providers

## Security

- Never commit `.env` files
- Always enable `NOXIS_API_KEYS` in production
- API keys, auth headers, and cookies are never logged
- User prompts are not logged in production
