import os
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG chatbot")

@app.get("/")
def home():
    return {"home page":"home page"}

@app.get("/health")
def health():
    return {"status": "ok"}
