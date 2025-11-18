"""
Test client for HFM Deep Agent Chatbot API
Tests both RAG and SQL agents
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", json.dumps(response.json(), indent=2))


def test_query(question: str, label: str = ""):
    """Test query endpoint"""
    print(f"\n{'='*70}")
    if label:
        print(f"[{label}]")
    print(f"❓ Question: {question}")
    print(f"{'='*70}")
    
    payload = {"question": question}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"💡 Answer:\n{result['answer']}\n")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("HFM Deep Agent Chatbot - Test Client")
    print("=" * 70)
    
    # Test health
    test_health()
    
    print("\n" + "="*70)
    print("Testing RAG Agent (Knowledge Questions)")
    print("="*70)
    
    # Test RAG agent queries
    test_query("What is leverage?", "RAG Agent Test 1")
    test_query("How do I verify my account?", "RAG Agent Test 2")
    test_query("What is a zero spread account?", "RAG Agent Test 3")
    
    print("\n" + "="*70)
    print("Testing SQL Agent (Trading Data Queries)")
    print("="*70)
    
    # Test SQL agent queries (these will work when SQL agent DB is set up)
    test_query("Show my total profit", "SQL Agent Test 1")
    test_query("What is my win rate?", "SQL Agent Test 2")
    
    print("\n" + "="*70)
    print("Testing Combined Queries (Both Agents)")
    print("="*70)
    
    # Test combined queries
    test_query("Show my trading performance and explain if it's good", "Combined Test")
    
    print("\n" + "="*70)
    print("Tests Complete")
    print("="*70)
