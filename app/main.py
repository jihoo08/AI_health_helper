# requirements.txt (핵심)
# fastapi uvicorn requests pydantic python-multipart sentence-transformers faiss-cpu pymongo pdfplumber python-dotenv

# file: app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import requests, os, json
from typing import Optional, List
from vector_store import VectorStore  # 아래에 구현
from utils import extract_text_from_pdf, chunk_text

APP = FastAPI(title="CommunityHealthBot")

AUGUST_BASE = os.environ.get("AUGUST_BASE_URL", "https://api.meetaugust.ai/v1")
AUGUST_KEY = os.environ.get("AUGUST_API_KEY", "replace_with_real_key")

def call_august(prompt: str, user_id: Optional[str]=None):
    headers = {"Authorization": f"Bearer {AUGUST_KEY}", "Content-Type":"application/json"}
    payload = {"prompt": prompt, "user_id": user_id}
    # NOTE: endpoint path is illustrative — replace with actual August API path
    resp = requests.post(f"{AUGUST_BASE}/chat", headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="August API error")
    return resp.json()

# init vector store (FAISS wrapper)
vector_store = VectorStore("/data/faiss_index", model_name="sentence-transformers/all-MiniLM-L6-v2")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    meta: Optional[dict] = None

@app.post("/chat")
def chat(req: ChatRequest):
    # 1) semantic retrieve
    contexts = vector_store.search(req.message, top_k=4)
    # 2) compose prompt with retrieved contexts + user meta
    prompt = "You are a medical assistant. Use ONLY the following sources (verbatim). If no clear answer, say '정보가 부족합니다' and recommend clinician.\n\n"
    for i,c in enumerate(contexts):
        prompt += f"[[SOURCE {i+1}]]\n{c['text']}\n\n"
    prompt += f"Patient meta: {json.dumps(req.meta or {})}\n\nQuestion: {req.message}\nAnswer concisely, note uncertainties, and recommend next steps."
    # 3) call August
    res = call_august(prompt, user_id=req.user_id)
    return {"answer": res}

@app.post("/upload_pdf")
async def upload_pdf(user_id: str, file: UploadFile = File(...)):
    contents = await file.read()
    # save temp
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(contents)
    text = extract_text_from_pdf(path)
    chunks = chunk_text(text, chunk_size=800)
    for i, chunk in enumerate(chunks):
        vector_store.add_document({"id": f"{file.filename}_{i}", "text": chunk, "source": file.filename})
    return {"status":"ok", "chunks": len(chunks)}
