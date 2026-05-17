# Python Basics

## ติดตั้ง Python และ IDE
- Windows: โหลด installer จาก python.org ติ๊ก “Add to PATH”
- Mac: ติดตั้งผ่าน Homebrew (`brew install python`)
- IDE แนะนำ: VS Code (ฟรี, ลง extension Python), PyCharm Community, Jupyter Notebook สำหรับ Data

## ตัวอย่างโค้ดพื้นฐาน
```python
# Hello World
print("Hello, World!")

# ตัวแปรและชนิดข้อมูล
name = "WorAI"        # str
age = 1               # int
pi = 3.14159          # float
is_ai = True          # bool

# List
fruits = ["apple", "banana", "cherry"]
fruits.append("date")

# Dictionary
user = {"name": "WorAI", "version": 1.0}
print(user["name"])

# ฟังก์ชัน
def greet(name):
    return f"สวัสดี {name}!"

# อ่าน CSV แล้วหาค่าเฉลี่ย
import pandas as pd
df = pd.read_csv('data.csv')
print(df['ราคา'].mean())
```

## โครงสร้างควบคุม
- `if / elif / else` สำหรับเงื่อนไข
- `for` loop สำหรับวนลูป
- `while` loop สำหรับเงื่อนไขซ้ำ
- `try / except` สำหรับจัดการ Error

## สายงานที่ใช้ Python
- Data Scientist, Backend Developer, Automation QA, DevOps, AI/ML Engineer

# Python OOP

## คลาสและออบเจกต์
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

dog = Dog("Buddy")
print(dog.speak())
```

## หลักการ OOP
- **Encapsulation**: ซ่อนข้อมูลด้วย private attribute (`_name`)
- **Inheritance**: สืบทอดคลาสแม่
- **Polymorphism**: คลาสลูก override method ของแม่
- **Abstraction**: ใช้ abstract base class กำหนด interface

# Python Advanced

## Decorators
```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

## Generators
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
```

## Context Managers
```python
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

## Async / Await
```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

# Python Libraries สำหรับ AI

## ไลบรารีสำคัญ
- **NumPy**: คำนวณ array ขนาดใหญ่
- **Pandas**: จัดการ DataFrame
- **Scikit-learn**: Machine Learning พื้นฐาน
- **TensorFlow / PyTorch**: Deep Learning
- **FastAPI**: สร้าง API แบบ async
- **Requests**: เรียก HTTP API
- **BeautifulSoup**: Scraping เว็บ

## ตัวอย่าง FastAPI
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Hello from WorAI"}

@app.post("/ask")
def ask_ai(query: AskRequest):
    return {"answer": f"คุณถามว่า: {query.text}"}
```

# Python Best Practices

## PEP 8 สไตล์ไกด์
- ใช้ snake_case สำหรับชื่อตัวแปรและฟังก์ชัน
- ใช้ CamelCase สำหรับชื่อคลาส
- บรรทัดไม่เกิน 79 ตัวอักษร (แนะนำ 88 สำหรับ Black formatter)
- เว้นบรรทัดระหว่างฟังก์ชัน 2 บรรทัด
- ใช้ docstring อธิบายฟังก์ชันและคลาส

## แหล่งฝึกโจทย์ฟรี
- Codewars (ปรับระดับได้)
- LeetCode (เน้นสัมภาษณ์งาน)
- HackerRank (มีโจทย์เรียงลำดับ)
