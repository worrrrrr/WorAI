import chromadb
import ollama
from pathlib import Path

print("🔥 เริ่มสร้างสมอง RAG ด้วย Ollama Embed แบบไว...")

client = chromadb.PersistentClient(path="./data/vector_db")
collection = client.get_or_create_collection("worai_knowledge")

knowledge_dir = Path("data/knowledge")
docs, metadatas, ids = [], [], []

for md_file in knowledge_dir.glob("*.md"):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        chunks = [content[j:j+800] for j in range(0, len(content), 400)]
        for j, chunk in enumerate(chunks):
            if len(chunk.strip()) > 50:
                docs.append(chunk)
                metadatas.append({"source": md_file.name})
                ids.append(f"{md_file.stem}_{j}")

print(f"📚 เจอไฟล์ความรู้ {len(docs)} chunks")
print("🧠 กำลังแปลงเป็น Vector แบบ Batch...")

embeddings = []
batch_size = 20
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    res = ollama.embed(model='qwen3-embedding:0.6b', input=batch)
    embeddings.extend(res['embeddings'])
    print(f" แปลงแล้ว {min(i+batch_size, len(docs))}/{len(docs)}")

collection.add(embeddings=embeddings, documents=docs, metadatas=metadatas, ids=ids)
print(f"✅ เสร็จแล้ว! WorAI จำความรู้ได้ {len(docs)} ชิ้น ด้วย Ollama")