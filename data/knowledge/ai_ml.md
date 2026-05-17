# LLM Prompting

## Prompt Engineering พื้นฐาน
- **Clear Instructions**: บอก AI ต้องการอะไรชัดเจน
- **Context**: ให้ข้อมูลพื้นหลังที่จำเป็น
- **Examples (Few-shot)**: ให้ตัวอย่าง 1-3 ตัวอย่างก่อนคำถามจริง
- **Role Assignment**: "คุณคือผู้เชี่ยวชาญด้าน..." ช่วยให้ AI ตอบตรงจุด
- **Chain of Thought**: "คิดทีละขั้นตอน" ช่วยให้ตอบถูกต้องขึ้น

## Prompt Templates
```markdown
# System Prompt
คุณคือผู้ช่วย AI ที่เชี่ยวชาญด้านการเขียนโปรแกรม 
ตอบเป็นภาษาไทย ให้ตัวอย่างโค้ดประกอบเสมอ

# Few-shot Prompt
แปลประโยคต่อไปนี้เป็นภาษาอังกฤษ:
1. สวัสดี → Hello
2. ขอบคุณ → Thank you
3. ลาก่อน → 

# Chain of Thought
ถ้ามีแอปเปิ้ล 3 ลูก กินไป 1 ลูก 
ซื้อเพิ่ม 2 ลูก ตอนนี้มีกี่ลูก?
คิดทีละขั้นตอน:
```

## Prompt Patterns สำคัญ
- **ReAct (Reasoning + Acting)**: คิด → ทำ → สังเกต → วนลูป
- **Tree of Thoughts**: สำรวจหลายทางเลือก แล้วเลือกดีที่สุด
- **Self-Consistency**: ถามหลายครั้ง แล้วเลือกคำตอบที่สุดมากที่สุด

# RAG Pipeline

## คืออะไร
RAG (Retrieval-Augmented Generation) = ดึงข้อมูลที่เกี่ยวข้องจากฐานความรู้ → ใส่ใน prompt → ให้ LLM ตอบตามข้อมูลนั้น

## ขั้นตอน
```
1. Ingest: อ่านเอกสาร (PDF, Web, Markdown)
2. Chunk: แบ่งเป็น chunks (500-1000 tokens)
3. Embed: แปลง chunks เป็น vectors ด้วย embedding model
4. Store: เก็บใน Vector Database
5. Retrieve: รับคำถาม → แปลงเป็น vector → หา chunks ใกล้เคียงสุด
6. Generate: เอา chunks + คำถาม → ส่งให้ LLM → ได้คำตอบ
```

## ตัวอย่าง RAG (Python)
```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI

# 1. โหลดเอกสาร
loader = TextLoader('knowledge.txt')
docs = loader.load()

# 2. แบ่ง chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 3-4. สร้าง vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 5-6. สร้าง QA chain
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(k=3)
)

result = qa.run("ข้อมูลสำคัญในเอกสารคืออะไร?")
```

# Vector Databases

## เปรียบเทียบ Vector DB
| ฐานข้อมูล | ข้อดี | ใช้เมื่อไหร |
|-----------|--------|-------------|
| **Chroma** | ติดตั้งง่าย, ใช้ใน local ได้ | Prototype, small project |
| **Pinecone** | Managed, scale ง่าย | Production, ไม่ต้องดูแล server |
| **Weaviate** | Hybrid search, GraphQL | ต้องการ filter + semantic search |
| **Qdrant** | เร็ว, เปิดเผย source | Self-hosted, high performance |
| **pgvector** | ใช้ PostgreSQL ที่มีอยู่ | มี Postgres อยู่แล้ว |

## Embedding Models
- **OpenAI text-embedding-ada-002**: แพงแต่ดี, 1536 dimensions
- **Sentence Transformers (all-MiniLM-L6-v2)**: ฟรี, เร็ว, 384 dimensions
- **Cohere embed**: รองรับหลายภาษา
- **BGE (BAAI)**: ดีสำหรับภาษาไทยและจีน

# Fine-tuning LLM

## เมื่อไหร่ควร Fine-tune
- ต้องการให้ LLM ตอบใน style ที่เฉพาะเจาะจง
- มีข้อมูลเฉพาะทางที่ LLM ทั่วไปไม่รู้
- ต้องการลด cost (model ที่ fine-tune มักเล็กกว่า but ตอบดีกว่า)
- **ไม่ควร fine-tune** ถ้าแค่ต้องการให้รู้ข้อมูลใหม่ → ใช้ RAG ดีกว่า

## ขั้นตอน Fine-tuning
```python
# 1. เตรียมข้อมูล (JSONL format)
{"messages": [
  {"role": "system", "content": "คุณคือผู้ช่วย..."},
  {"role": "user", "content": "สวัสดี"},
  {"role": "assistant", "content": "สวัสดีครับ มีอะไรให้ช่วยไหม?"}
]}

# 2. ใช้ OpenAI API หรือ HuggingFace Trainer
# 3. ประเมินผลด้วย benchmark
# 4. Deploy model ที่ fine-tune แล้ว
```

## Parameter-Efficient Fine-Tuning (PEFT)
- **LoRA (Low-Rank Adaptation)**: แก้ไขเฉพาะบาง layer ประหยัด VRAM
- **QLoRA**: LoRA + 4-bit quantization ใช้ GPU น้อยลงมาก
- **Prefix Tuning**: เพิ่ม prefix vectors แทนการแก้ไข weights

# AI Agents

## สถาปัตยกรรม Agent
```
Input → Planning → Tool Selection → Action → Observation → ... → Output
```

## Tools ที่ Agent ใช้ได้
- **Search**: Google Search, Wikipedia, ฐานข้อมูล
- **Code Execution**: Python REPL, รันโค้ด
- **API Calls**: เรียก API ภายนอก
- **File Operations**: อ่าน/เขียนไฟล์
- **Memory**: จดจำบทสนทนาก่อนหน้า

## Frameworks สำหรับสร้าง Agent
- **LangChain**: สร้าง chain และ agent ได้ยืดหยุ่น
- **LangGraph**: สร้าง workflow แบบ graph (cycles ได้)
- **AutoGPT**: Agent อัตโนมัติแบบ autonomous
- **CrewAI**: Multi-agent ทำงานร่วมกันเป็นทีม

## ตัวอย่าง LangChain Agent
```python
from langchain.agents import Tool, AgentType, initialize_agent
from langchain_openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="ใช้ค้นหาข้อมูลล่าสุดบนอินเทอร์เน็ต"
    )
]

llm = OpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

agent.run("อากาศกรุงเทพวันนี้เป็นอย่างไร?")
```

# AI Evaluation

## วัดผล LLM
- **BLEU / ROUGE**: เปรียบเทียบกับคำตอบ reference
- **BERTScore**: ใช้ embedding วัดความคล้าย
- **Human Evaluation**: ให้คนให้คะแนน relevance, accuracy, fluency
- **LLM-as-Judge**: ใช้ GPT-4 ตรวจคำตอบของ model อื่น

## RAG Evaluation
- **Context Precision**: เนื้อหาที่ retrieve มาตรงกับคำถามไหม
- **Context Recall**: เนื้อหาสำคัญถูก retrieve ครบไหม
- **Faithfulness**: คำตอบตรงกับเนื้อหาที่ให้ไหม (ไม่ hallucinate)
- **Answer Relevance**: คำตอบตรงกับคำถามไหม

# AI Ethics and Safety

## ข้อควรระวัง
- **Hallucination**: LLM อาจตอบข้อมูลเท็จด้วยความมั่นใจ → ต้องมี fact-checking
- **Bias**: ข้อมูล training อาจมีอคติทางเพศ, เชื้อชาติ, อายุ
- **Privacy**: อย่าส่ง PII (ชื่อ, เลขบัตรประชาชน) ไปยัง public API
- **Copyright**: ผลลัพธ์จาก AI อาจละเมิดลิขสิทธิ์
- **Jailbreaking**: ผู้ใช้อาจหลอกให้ AI ตอบสิ่งที่ไม่เหมาะสม

## วิธีป้องกัน
- ใช้ system prompt กำหนดขอบเขตชัดเจน
- กรอง input/output ด้วย content moderation API
- ทำ output validation ก่อนส่งให้ user
- เก็บ log การใช้งานเพื่อตรวจสอบย้อนกลับ
- แจ้ง user เสมอว่าเป็น AI-generated content
