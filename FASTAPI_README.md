# HFM RAG Chatbot - FastAPI Application

Clean, production-ready FastAPI application for the HFM RAG chatbot.

## 🚀 Quick Start

### 1. Ensure PostgreSQL is Running

Make sure your PostgreSQL with pgvector is running:

```powershell
# Check if container is running
docker ps

# If not running, start it:
docker run -d --name hfm-postgres -e POSTGRES_USER=avivekanandan -e POSTGRES_PASSWORD=HotForex! -e POSTGRES_DB=hfm_assistant -p 5432:5432 pgvector/pgvector:pg16

# Enable vector extension
docker exec -it hfm-postgres psql -U avivekanandan -d hfm_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Activate Virtual Environment

```powershell
.venv\Scripts\Activate
```

### 3. Run the FastAPI Server

```powershell
python app_main.py
```

The server will start on http://localhost:8000

### 4. Test the API

**Option 1: Interactive API Docs**
- Open browser: http://localhost:8000/docs
- Try the `/query` endpoint

**Option 2: Test Client**
```powershell
# In a new terminal
python test_client.py
```

**Option 3: curl**
```powershell
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\": \"What is leverage?\"}"
```

## 📁 Project Structure

```
abi_hfm/
├── app_main.py              # ✅ Clean FastAPI application
├── test_client.py           # ✅ Test client for the API
├── app/
│   └── services_v1/
│       └── rag_agent_core.py # ✅ RAG agent implementation
├── .env                     # Configuration
├── requirements.txt         # Dependencies
└── qa_pairs.csv            # Knowledge base data
```

## 🔌 API Endpoints

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "service": "HFM RAG Chatbot",
  "agent_ready": true
}
```

### POST /query
Query the RAG agent

**Request:**
```json
{
  "question": "What is leverage?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Leverage is...",
  "question": "What is leverage?",
  "session_id": "optional-session-id"
}
```

### GET /
API information and available endpoints

## 🛠️ Configuration

All configuration is in `.env` file:

```properties
GOOGLE_API_KEY=your-api-key
PGVECTOR_CONNECTION=postgresql://avivekanandan:HotForex!@localhost:5432/hfm_assistant
MODEL_NAME=gemini-2.0-flash-exp
EMBEDDING_MODEL=models/text-embedding-004
```

## 📊 What Happens on Startup

1. FastAPI app starts
2. RAG agent initializes
3. Vector store connects to PostgreSQL
4. CSV files are loaded (if not already in DB)
5. API is ready to accept queries

## 🧪 Testing

**Test with curl:**
```powershell
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d "{\"question\": \"How do I verify my account?\"}"
```

**Test with Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is leverage?"}
)
print(response.json()["answer"])
```

## 🎯 Features

✅ Clean FastAPI structure  
✅ Async RAG agent integration  
✅ Automatic startup/shutdown handling  
✅ CORS enabled  
✅ Interactive API documentation (/docs)  
✅ Health check endpoint  
✅ Error handling  
✅ Type validation with Pydantic  

## 🔧 Troubleshooting

**Error: "RAG agent not initialized"**
- Check PostgreSQL is running
- Check `.env` file has correct `PGVECTOR_CONNECTION`
- Check logs on startup

**Error: "connection refused"**
- Start PostgreSQL: `docker ps` to check
- Enable vector extension

**Slow first query?**
- Normal - first query loads CSV files into database
- Subsequent queries are fast

## 📝 Notes

- Old `app/` folder files are kept for reference
- New clean implementation is in `app_main.py`
- Uses `services_v1/rag_agent_core.py` as the RAG engine
