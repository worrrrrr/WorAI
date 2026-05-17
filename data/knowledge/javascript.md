# JavaScript Basics

## ES6+ สิ่งที่ต้องรู้
- `let` และ `const` แทน `var` (block scope)
- Arrow function: `(x) => x * 2`
- Template literals: `` `Hello ${name}` ``
- Destructuring: `const {name, age} = user`
- Spread operator: `[...arr1, ...arr2]`
- Default parameters: `function greet(name = "Guest")`

## ตัวอย่างโค้ดพื้นฐาน
```javascript
// ตัวแปร
const PI = 3.14159;
let count = 0;

// ฟังก์ชัน
const greet = (name) => `สวัสดี ${name}`;

// Array methods
const nums = [1, 2, 3, 4, 5];
const doubled = nums.map(n => n * 2);
const evens = nums.filter(n => n % 2 === 0);
const sum = nums.reduce((acc, n) => acc + n, 0);

// Object
const person = {
  name: "WorAI",
  age: 1,
  greet() {
    return `ฉันคือ ${this.name}`;
  }
};

// Promises
fetch('/api/data')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

# JavaScript Async Await

## การทำงานแบบ async
```javascript
async function getUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error('Not found');
    const user = await res.json();
    return user;
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
}

// เรียกใช้
getUser(1).then(user => console.log(user));

// Promise.all สำหรับเรียกพร้อมกัน
const [users, posts] = await Promise.all([
  fetch('/api/users').then(r => r.json()),
  fetch('/api/posts').then(r => r.json())
]);
```

# TypeScript Fundamentals

## ชนิดข้อมูลพื้นฐาน
```typescript
// Primitive types
let name: string = "WorAI";
let age: number = 1;
let isActive: boolean = true;

// Array
let scores: number[] = [90, 85, 95];
let names: Array<string> = ["A", "B", "C"];

// Object / Interface
interface User {
  id: number;
  name: string;
  email?: string;  // optional
  readonly createdAt: Date;  // แก้ไขไม่ได้
}

const user: User = {
  id: 1,
  name: "WorAI",
  createdAt: new Date()
};

// Function
function add(a: number, b: number): number {
  return a + b;
}

// Generic
function identity<T>(arg: T): T {
  return arg;
}
const output = identity<string>("myValue");

// Union Type
function printId(id: number | string) {
  console.log(id);
}

// Enum
enum Status {
  Pending,
  Approved,
  Rejected
}
```

## TypeScript Advanced
```typescript
// Type alias
type Point = { x: number; y: number };

// Utility types
type PartialUser = Partial<User>;      // ทุก field optional
type RequiredUser = Required<User>;      // ทุก field required
type UserPreview = Pick<User, 'id' | 'name'>;  // เลือกบาง field
type UserWithoutId = Omit<User, 'id'>;   // ตัดบาง field

// Interface สืบทอด
interface Admin extends User {
  role: 'admin';
  permissions: string[];
}
```

# JavaScript DOM Manipulation

## การจัดการ DOM
```javascript
// หา element
const button = document.getElementById('btn');
const items = document.querySelectorAll('.item');

// Event listener
button.addEventListener('click', (e) => {
  e.preventDefault();
  console.log('Clicked!');
});

// สร้าง element
const div = document.createElement('div');
div.className = 'card';
div.innerHTML = '<h3>Title</h3>';
document.body.appendChild(div);

// เปลี่ยน style
button.style.backgroundColor = '#3b82f6';
button.classList.toggle('active');
```

# JavaScript Testing

## Jest พื้นฐาน
```javascript
// test.js (ใช้ ESM ต้องตั้งค่า "type": "module" ใน package.json หรือใช้ .mjs)
import { add, greet } from './utils';

test('adds 1 + 2 to equal 3', () => {
  expect(add(1, 2)).toBe(3);
});

test('greet returns correct string', () => {
  expect(greet('WorAI')).toBe('สวัสดี WorAI');
});

// Mock
jest.mock('./api');
```

# JavaScript Best Practices

## สิ่งที่ควรทำ
- ใช้ `===` แทน `==` เสมอ (strict equality)
- หลีกเลี่ยง global variables
- ใช้ `const` เป็นค่าเริ่มต้น ใช้ `let` เมื่อต้องเปลี่ยนค่า
- จัดการ error ด้วย try/catch ใน async function
- ใช้ early return แทน nested if
- แยกโค้ดเป็นโมดูล (ES Modules) แทนไฟล์ยาวๆ

## สิ่งที่ไม่ควรทำ
- อย่าใช้ `var`
- อย่าแก้ไข array/object โดยตรง (ใช้ immutable update)
- อย่าลืม cleanup event listeners
- อย่าใช้ `eval()`
