#!/usr/bin/env bash
# script to run FastAPI server locally
echo"Starting RAG Bot API server..."
uvicorn src.rag_bot.api:app --host 0.0.0.0 --port 8000 --reload
