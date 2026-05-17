"""
Knowledge Loader - โหลด.md ทั้งหมดใน data/knowledge
ให้ KRIT ใช้อ้างอิงตอนตอบ
"""
import os
import re
from pathlib import Path
from typing import List, Dict

class KnowledgeBase:
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.docs = {}
        self.load_all()

    def load_all(self):
        """โหลดไฟล์.md ทั้งหมดเข้ามาในหน่วยความจำ"""
        if not self.knowledge_dir.exists():
            print(f"[Warning] ไม่เจอโฟลเดอร์ {self.knowledge_dir}")
            return

        for md_file in self.knowledge_dir.glob("*.md"):
            topic = md_file.stem # common, LIFE, sveltekit, work
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # แตกเป็น chunks ตามหัวข้อ ##
                chunks = re.split(r'\n## ', content)
                self.docs[topic] = [c.strip() for c in chunks if c.strip()]

        print(f"[Knowledge] โหลดแล้ว {len(self.docs)} หมวดหมู่: {list(self.docs.keys())}")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        ค้นหาเนื้อหาที่เกี่ยวข้องกับ query แบบง่าย
        Return: [{'topic': 'LIFE', 'content': '...', 'score': 5}]
        """
        results = []
        query_words = set(query.lower().split())

        for topic, chunks in self.docs.items():
            for chunk in chunks:
                chunk_lower = chunk.lower()
                # นับคำที่ตรงกัน
                score = sum(1 for word in query_words if word in chunk_lower)
                if score > 0:
                    results.append({
                        "topic": topic,
                        "content": chunk[:500], # ตัดมา 500 ตัวแรก
                        "score": score
                    })

        # เรียงตาม score สูงสุด
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_all_topics(self) -> List[str]:
        """ดูว่ามีหมวดหมู่อะไรบ้าง"""
        return list(self.docs.keys())

# ทดสอบ
if __name__ == "__main__":
    kb = KnowledgeBase()
    print(kb.search("ความเครียด ทำงาน"))