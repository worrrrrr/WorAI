# Clean Code

## หลักการเขียนโค้ดสะอาด
- **Meaningful Names**: ตั้งชื่อตัวแปร/ฟังก์ชันให้บอกความหมาย เช่น `calculateTotalPrice()` แทน `calc()`
- **Single Responsibility**: ฟังก์ชันหนึ่งทำงานเดียว ไม่เกิน 20-30 บรรทัด
- **DRY (Don't Repeat Yourself)**: ถ้าโค้ดซ้ำ 3 ครั้ง ให้แยกเป็น function
- **KISS (Keep It Simple, Stupid)**: ง่ายที่สุดที่ทำงานได้
- **YAGNI (You Aren't Gonna Need It)**: อย่าเพิ่มฟีเจอร์ที่ยังไม่จำเป็น

## ตัวอย่าง Before / After
```python
# Before (ไม่ดี)
def calc(a, b, c):
    if c == 1:
        return a + b
    elif c == 2:
        return a - b
    elif c == 3:
        return a * b

# After (ดี)
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
```

## Comments ที่ดี
- อธิบาย "ทำไม" ไม่ใช่ "อะไร" (โค้ดบอกอะไร คอมเมนต์บอกทำไม)
- อย่าปล่อยโค้ดที่ comment ไว้ (dead code) ใน repository
- ใช้ docstring / JSDoc อธิบายฟังก์ชันที่ซับซ้อน

# Data Structures and Algorithms

## โครงสร้างข้อมูลพื้นฐาน
| โครงสร้าง | เวลาเข้าถึง | เวลาเพิ่ม | ใช้เมื่อไหร |
|-----------|-----------|-----------|-------------|
| Array | O(1) | O(n) | ข้อมูลตายตัว ต้องการ index |
| Linked List | O(n) | O(1) | ต้องการเพิ่ม/ลบบ่อยต้น/ท้าย |
| Stack | O(1) top | O(1) | LIFO, undo, backtracking |
| Queue | O(1) front | O(1) | FIFO, BFS, task queue |
| Hash Map | O(1) | O(1) | ค้นหาด้วย key, cache |
| Tree | O(log n) | O(log n) | ข้อมูลมีลำดับ, file system |
| Graph | V+E | V+E | เครือข่าย, shortest path |

## อัลกอริทึมสำคัญ
- **Binary Search**: ค้นหาใน sorted array O(log n)
- **Quick Sort / Merge Sort**: เรียงลำดับ O(n log n)
- **BFS / DFS**: ค้นหาในกราฟ
- **Dynamic Programming**: แก้ปัญหาซ้ำซ้อน (Fibonacci, Knapsack)
- **Two Pointers / Sliding Window**: ปัญหาบน array
- **Greedy Algorithm**: เลือกที่ดีที่สุดในแต่ละขั้น

## ตัวอย่าง Binary Search
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

# Git

## คำสั่งพื้นฐานที่ใช้ทุกวัน
```bash
# เริ่มต้น
git init
git clone <url>

# ทำงาน
git status                    # ดูสถานะ
git add .                     # เพิ่มทั้งหมด
git add <file>                # เพิ่มเฉพาะไฟล์
git commit -m "feat: add login"  # commit
git push origin main          # push

# ดูประวัติ
git log --oneline --graph     # ดู history สวยๆ
git diff                      # ดูความเปลี่ยนแปลง

# แก้ไข
git checkout -b feature/x     # สร้าง branch ใหม่
git checkout main             # เปลี่ยน branch
git merge feature/x           # merge
git rebase main               # rebase

# ย้อนกลับ
git reset --soft HEAD~1       # ยกเลิก commit ล่าสุด (เก็บโค้ด)
git reset --hard HEAD~1       # ยกเลิก commit ล่าสุด (ลบโค้ด)
git revert <commit_hash>      # สร้าง commit ใหม่ย้อนกลับ
```

## Git Flow / Trunk Based
- **Git Flow**: main, develop, feature/*, release/*, hotfix/*
- **Trunk Based**: ทุกคน push ไป main branch บ่อยๆ ใช้ feature flags
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## .gitignore สำคัญ
```gitignore
node_modules/
__pycache__/
*.pyc
.env
.DS_Store
dist/
build/
.vscode/
.idea/
```

# Testing

## หลักการทดสอบ
- **Unit Test**: ทดสอบฟังก์ชันเดี่ยว เร็ว แยกอิสระ
- **Integration Test**: ทดสอบการทำงานร่วมกันของหลาย module
- **E2E Test**: ทดสอบตั้งแต่ UI ถึง database (Cypress, Playwright)
- **TDD (Test-Driven Development)**: เขียน test ก่อน แล้วค่อยเขียนโค้ดให้ผ่าน

## Unit Test ตัวอย่าง (Python pytest)
```python
# test_calculator.py
import pytest
from calculator import add, divide

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
```

## Coverage
- เป้าหมาย: coverage >= 80%
- แต่ coverage สูง ≠ โค้ดดี ต้อง test quality ด้วย
- ใช้ mutation testing เพื่อตรวจสอบว่า test จริงจังแค่ไหน

# Debugging

## เทคนิค Debugging
1. **Reproduce**: ทำให้ bug เกิดซ้ำได้เสมอ
2. **Isolate**: ย่อยปัญหาให้เล็กที่สุด
3. **Check Assumptions**: ตรวจสอบว่าตัวแปรมีค่าที่คาดไว้จริงไหม
4. **Binary Search**: comment ครึ่งโค้ด ดูว่า bug อยู่ครึ่งไหน
5. **Read Error Carefully**: อ่าน stack trace ให้ละเอียด

## Tools
- **Print / Console.log**: เร็วที่สุด ดูค่าตัวแปร
- **Debugger**: pdb (Python), VS Code debugger, Chrome DevTools
- **Logging**: ใช้ระดับ DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Linting**: ESLint, Pylint, Ruff (จับข้อผิดพลาดก่อนรัน)

## ตัวอย่าง Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info('เริ่มประมวลผล')
logging.debug(f'ค่าตัวแปร x = {x}')
logging.error('เกิดข้อผิดพลาด!', exc_info=True)
```

# Design Patterns

## Patterns สำคัญ
- **Singleton**: มี instance เดียวในโปรแกรม (database connection)
- **Factory**: สร้าง object โดยไม่ระบุ class ตรงๆ
- **Observer / Pub-Sub**: เมื่อสิ่งหนึ่งเปลี่ยน สิ่งอื่นแจ้งเตือนอัตโนมัติ
- **Strategy**: เปลี่ยน algorithm ได้ระหว่างรันไทม์
- **Decorator**: เพิ่มพฤติกรรมให้ object โดยไม่แก้ไข class
- **MVC / MVVM**: แยก Model, View, Controller/ViewModel

## ตัวอย่าง Singleton (Python)
```python
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

# Code Review

## Checklist สำหรับการรีวิวโค้ด
- [ ] โค้ดทำงานได้จริง (run ผ่าน)
- [ ] มี test ครอบคลุม
- [ ] ตั้งชื่อตัวแปร/ฟังก์ชันเข้าใจง่าย
- [ ] ไม่มีโค้ดซ้ำซ้อน
- [ ] จัดการ error ครบถ้วน
- [ ] ไม่มี security issue (SQL injection, XSS)
- [ ] ประสิทธิภาพ acceptable (ไม่มี N+1 query)
- [ ] มี docstring / comment สำหรับส่วนที่ซับซ้อน
