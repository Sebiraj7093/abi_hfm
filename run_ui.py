#!/usr/bin/env python3
"""
Simple script to run the chatbot UI
"""
import uvicorn
import os

if __name__ == "__main__":
    print("🚀 Starting SQL Agent Chatbot UI...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("💬 The chatbot interface will be available at the root URL")
    print("\n" + "="*50)
    
    # Set environment variables if needed
    os.environ.setdefault("PYTHONPATH", "/home/avivekanandan/sql-agent-hf-api")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down chatbot UI...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure all dependencies are installed and configured properly")