# HTML CSS Fundamentals

## HTML5 สิ่งที่ต้องรู้
- **Semantic Tags**: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- **Form Elements**: `<input type="email">`, `<textarea>`, `<select>`, `required` attribute
- **Accessibility**: `alt` ใน `<img>`, `aria-label`, `role`, `tabindex`
- **Meta Tags**: `viewport` สำหรับ responsive, `charset="UTF-8"`

## CSS สมัยใหม่
```css
/* Flexbox */
.container {
  display: flex;
  justify-content: center;  /* แนวนอน */
  align-items: center;      /* แนวตั้ง */
  gap: 1rem;
}

/* Grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
}

/* CSS Variables */
:root {
  --primary: #3b82f6;
  --radius: 8px;
}
.button {
  background: var(--primary);
  border-radius: var(--radius);
}
```

## Tailwind CSS (แนะนำ)
```html
<!-- ใช้ utility classes แทนการเขียน CSS -->
<div class="flex items-center justify-center min-h-screen bg-gray-50 p-4">
  <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-6">
    <h2 class="text-xl font-bold text-gray-800">Login</h2>
    <input class="w-full mt-4 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" />
  </div>
</div>
```

# REST API Design

## HTTP Methods
| Method | ใช้ทำอะไร | Idempotent |
|--------|-----------|------------|
| GET | ดึงข้อมูล | Yes |
| POST | สร้างข้อมูลใหม่ | No |
| PUT | แทนที่ข้อมูลทั้งหมด | Yes |
| PATCH | แก้ไขบาง field | No |
| DELETE | ลบข้อมูล | Yes |

## Status Codes
- **2xx Success**: 200 OK, 201 Created, 204 No Content
- **3xx Redirect**: 301 Moved, 304 Not Modified
- **4xx Client Error**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable
- **5xx Server Error**: 500 Internal Error, 502 Bad Gateway, 503 Service Unavailable

## JSON Response Format
```json
// สำเร็จ
{
  "success": true,
  "data": { "id": 1, "name": "WorAI" }
}

// ล้มเหลว
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required"
  }
}
```

## API Versioning
- URL: `/api/v1/users`, `/api/v2/users`
- Header: `Accept: application/vnd.api+json;version=2`

# Database

## SQL vs NoSQL
| | SQL (PostgreSQL, MySQL) | NoSQL (MongoDB, Redis) |
|---|---|---|
| ข้อมูล | Structured, table | Flexible, document/key-value |
| การ query | JOIN ซับซ้อน | Simple lookups |
| ความสอดคล้อง | ACID (strong) | Eventual consistency |
| ใช้เมื่อ | ข้อมูลมีความสัมพันธ์ซับซ้อน | ข้อมูลเปลี่ยนรูปบ่อย, scale สูง |

## SQL Basics
```sql
-- CRUD
SELECT * FROM users WHERE age > 18 ORDER BY name;
INSERT INTO users (name, email) VALUES ('WorAI', 'wor@ai.com');
UPDATE users SET name = 'WorAI v2' WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- JOIN
SELECT orders.id, users.name 
FROM orders 
JOIN users ON orders.user_id = users.id;

-- Indexing (เพิ่มความเร็ว)
CREATE INDEX idx_users_email ON users(email);
```

## ORM (Prisma / SQLAlchemy)
```python
# SQLAlchemy (Python)
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
```

# Authentication and Security

## JWT (JSON Web Token)
```
Header: { "alg": "HS256", "typ": "JWT" }
Payload: { "sub": "user_id", "exp": 1234567890 }
Signature: HMACSHA256(base64url(header) + "." + base64url(payload), secret)
```

## OAuth 2.0 / SSO
1. User กด "Login with Google"
2. Redirect ไป Google Authorization Server
3. User ยินยอม → ได้ Authorization Code
4. ส่ง Code + Client Secret ไปแลก Access Token
5. ใช้ Access Token เรียก Google API ดึงข้อมูล user

## Security Best Practices
- เก็บ password ด้วย bcrypt / Argon2 (ไม่เก็บ plain text)
- ใช้ HTTPS ทุก endpoint (Let's Encrypt ฟรี)
- Rate limiting: จำกัด requests ต่อ IP (เช่น 100 req/min)
- Input validation: ตรวจสอบทุก input จาก client
- CORS: กำหนด origin ที่อนุญาต
- Sanitize output: ป้องกัน XSS ด้วย escaping HTML
- SQL Parameterized Queries: ป้องกัน SQL Injection
- ใช้ `.env` เก็บ secrets (ไม่ commit ขึ้น git)

# Deployment

## Docker พื้นฐาน
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t worai-app .
docker run -p 8000:8000 worai-app
```

## Docker Compose
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...@
  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

## Cloud Deployment Options
- **Vercel**: ฟรี tier ดีมาก, deploy ง่าย, สำหรับ frontend + serverless
- **Railway**: Deploy ง่าย, มี database ในตัว
- **Render**: ฟรี tier, รองรับ web service + PostgreSQL
- **AWS / GCP / Azure**: สำหรับ production ใหญ่, มี managed services
- **Fly.io**: Deploy container ง่าย ใกล้ user (edge)

## CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
```

# Web Performance

## Core Web Vitals
- **LCP (Largest Contentful Paint)**: < 2.5s (โหลดข้อมูลหลัก)
- **INP (Interaction to Next Paint)**: < 200ms (ตอบสนอง interaction)
- **CLS (Cumulative Layout Shift)**: < 0.1 (ไม่มี layout กระโดด)

## วิธีเพิ่มความเร็ว
- **Lazy Loading**: โหลดรูปเมื่อ scroll ถึง (`loading="lazy"`)
- **Code Splitting**: แยก bundle ตาม route (dynamic import)
- **Caching**: Service Worker, HTTP Cache Headers
- **Image Optimization**: ใช้ WebP, responsive images
- **Minification**: ลดขนาด JS/CSS/HTML
- **CDN**: Cloudflare, Vercel Edge, AWS CloudFront
