import json
from semantic_text_splitter import TextSplitter
import torch
from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
import uvicorn
from fastapi import FastAPI
import os
import dotenv

dotenv.load_dotenv()

# read data
if not os.path.exists("reddit_posts.json"):
    print("Downloading dataset...")
    os.system('curl -L "https://drive.google.com/uc?export=download&id=1Dm3N8BCZvF5yNZc2tbT3NJXeeCzEuyVQ" -o reddit_posts.json')

with open("reddit_posts.json", "r") as f:
    posts = json.load(f)

for post in posts:
    post["comments"].sort(key=lambda x: x["score"], reverse=True)

# split into chunks
splitter = TextSplitter(capacity=512, overlap=64)
post_chunks = []
for index, post in enumerate(posts):
    post_text = post["title"] + " " + post["body"]
    for chunk in splitter.chunks(post_text):
        post_chunks.append({"text": chunk, "metadata": {"index": index}})

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
post_texts = [chunk["text"] for chunk in post_chunks]
post_embeddings = model.encode(post_texts, convert_to_numpy=True, device=device)

# populate vector store
client = chromadb.Client()
post_collection = client.create_collection("posts")
batch_size = 5000
def populate_collection(collection, chunks, embeddings):
  for i in range(0, len(chunks), batch_size):
    batch_emb = embeddings[i:i+batch_size]
    batch_docs = [c["text"] for c in chunks[i:i+batch_size]]
    batch_meta = [c["metadata"] for c in chunks[i:i+batch_size]]
    batch_ids = [str(i+j) for j in range(len(batch_docs))]

    collection.add(
        embeddings=batch_emb.tolist(),
        documents=batch_docs,
        metadatas=batch_meta,
        ids=batch_ids,
    )
populate_collection(post_collection, post_chunks, post_embeddings)

# initialize chat client
chat_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_context_from_posts(relevant_posts):
    context = ""
    for post in relevant_posts:
        context += f'Q: {post["title"]}\n{post["body"]}\n\n'
        for comment in post["comments"]:
            context += f'score: {comment["score"]}, answer: {comment["body"]}\n'
        context += '---\n'
    return context

def chat_with_rag(query):
    q_emb = model.encode([query])
    results = post_collection.query(query_embeddings=q_emb, n_results=5)
    relevant_posts_idxs = [metadata["index"] for metadata in results["metadatas"][0]]
    relevant_posts = [posts[idx] for idx in relevant_posts_idxs]
    context = get_context_from_posts(relevant_posts)
    prompt = f"""You will play the role of an experienced student at Purdue University to answer questions.
    Your knowledge is based on the following questions and answers from reddit as context to answer the user's query.

    {context}

    You know this information from your experience, do not mention reddit or directly quote the context in your response.
    Question: {query}
    Answer:"""
    response = chat_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

# fast api endpoint for chat_with_rag
app = FastAPI()

@app.post("/chat")
def chat(query: str):
    return chat_with_rag(query)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)