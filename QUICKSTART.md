# 🚀 Quick Start Guide - HFM Deep Agent Chatbot

## Start the API in 3 Steps:

### Step 1: Ensure PostgreSQL is Running
```powershell
# Check if running
docker ps

# If not running, start it:
docker run -d --name hfm-postgres -e POSTGRES_USER=avivekanandan -e POSTGRES_PASSWORD=HotForex! -e POSTGRES_DB=hfm_assistant -p 5432:5432 pgvector/pgvector:pg16

# Enable vector extension (first time only)
docker exec -it hfm-postgres psql -U avivekanandan -d hfm_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Step 2: Activate Virtual Environment
```powershell
.venv\Scripts\Activate
```

### Step 3: Run the Server
```powershell
python app_main.py
```

✅ Server running at: http://localhost:8000

## Test the API:

### Option 1: Interactive Docs (Recommended)
Open in browser: **http://localhost:8000/docs**

Try the `/query` endpoint with:
- "What is leverage?" (RAG Agent)
- "What is a zero spread account?" (RAG Agent)

### Option 2: Run Test Client
```powershell
# In a new terminal
python test_client.py
```

### Option 3: curl
```powershell
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\": \"What is leverage?\"}"
```

## What You Have:

✅ **Deep Agent** - Intelligent orchestrator  
✅ **RAG Agent** - Answers knowledge questions from CSV files  
✅ **SQL Agent** - Ready to analyze trading data (needs forex_trades table)  
✅ **FastAPI** - Production-ready REST API  
✅ **Auto Docs** - Interactive API documentation at /docs  

## Example Queries:

**Knowledge Questions (RAG Agent):**
- "What is leverage?"
- "How do I verify my account?"
- "What is a zero spread account?"
- "Explain margin trading"

**Data Questions (SQL Agent - when DB is set up):**
- "Show my total profit"
- "What is my win rate?"
- "Analyze my trades"

**Combined Questions:**
- "Show my performance and explain if it's good"

## Architecture:

```
User Query → FastAPI → Deep Agent → Routes to:
                                    ├─ RAG Agent (knowledge)
                                    ├─ SQL Agent (data)
                                    └─ Both (combined)
```

## Files:

- `app_main.py` - FastAPI application ✅
- `test_client.py` - Test client ✅
- `app/services_v1/rag_agent_core.py` - RAG agent ✅
- `app/services_v1/sql_agent_core.py` - SQL agent ✅
- `app/services_v1/constants.py` - Deep agent prompt ✅

## Troubleshooting:

**"Deep agent not initialized"**
- Check PostgreSQL is running: `docker ps`
- Check `.env` has correct credentials
- Check startup logs for errors

**"No CSV files loaded"**
- First query is slow (loading CSVs)
- Subsequent queries are fast
- Check `qa_pairs.csv` exists in project root

---

**You're all set! 🎉**
