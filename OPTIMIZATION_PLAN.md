# 🚀 WorAI Performance Optimization Plan

## สถานะปัจจุบัน (Current Status)
- **Startup Time**: ~0.12s (Excellent ✅)
- **Lazy Loading**: Implemented ใน ToolRegistry ✅
- **Tool Registry**: Singleton pattern พร้อม lazy loading ✅
- **Router**: Priority-based rule matching ✅

---

## 📊 การวิเคราะห์ Bottleneck ที่เหลือ

### 1. Router Initialization
**ปัญหา**: โหลด rules ทั้งหมด 512 lines ตอนเริ่มต้น
**ผลกระทบ**: ต้อง compile regex ทุกรูปแบบทันที

### 2. YAML Parsing
**ปัญหา**: อ่านและ parse intents.yaml (399 lines) และ rules.yaml ทุกครั้ง
**ผลกระทบ**: I/O overhead + YAML parsing time

### 3. Memory Footprint
**ปัญหา**: เก็บ intent rules ทั้งหมดใน memory แม้ไม่ได้ใช้
**ผลกระทบ**: ใช้ memory มากเกินจำเป็น

### 4. Pattern Matching
**ปัญหา**: วนลูปทุก rule จนกว่าจะ match
**ผลกระทบ**: O(n) complexity สำหรับแต่ละ request

---

## 🎯 แผนการเพิ่มเติม (Additional Optimizations)

### Phase 1: Quick Wins (High Impact, Low Effort)

#### 1.1 Cache Compiled Patterns
```python
# src/core/router.py
class IntentRouter:
    _pattern_cache = {}  # Class-level cache
    
    def _compile_pattern(self, pattern_str: str):
        if pattern_str not in self._pattern_cache:
            self._pattern_cache[pattern_str] = re.compile(pattern_str, re.IGNORECASE)
        return self._pattern_cache[pattern_str]
```
**Expected Gain**: 10-15% faster classification

#### 1.2 Early Exit for Direct Routes
```python
# เพิ่ม direct route detection ก่อน rule matching
DIRECT_PATTERNS = {
    'สวัสดี': 'greeting',
    'หวัดดี': 'greeting',
    'ขอบคุณ': 'gratitude',
    'บ๊ายบาย': 'farewell',
}

def classify(self, text: str):
    # Check direct patterns first (O(1))
    for pattern, intent in DIRECT_PATTERNS.items():
        if pattern in text.lower():
            return self._create_direct_route(intent)
    # Fall back to rule matching
```
**Expected Gain**: 20-30% faster for common queries

#### 1.3 Lazy Load Rules
```python
# โหลด rules เฉพาะเมื่อต้องการ
class IntentRouter:
    def __init__(self):
        self._rules_loaded = False
        self.intent_rules = []
        
    def _ensure_rules_loaded(self):
        if not self._rules_loaded:
            self._load_rules()
            self._rules_loaded = True
            
    def classify(self, text: str):
        self._ensure_rules_loaded()
        # ... matching logic
```
**Expected Gain**: Faster initial startup

---

### Phase 2: Medium Term (Medium Impact, Medium Effort)

#### 2.1 Rule Indexing with Keyword Map
```python
# สร้าง inverted index สำหรับ keyword -> rules
class IntentRouter:
    def __init__(self):
        self.keyword_index = {}  # {"ดวง": [rule1, rule2], "คำนวณ": [rule3]}
    
    def _build_keyword_index(self):
        for rule in self.intent_rules:
            keywords = self._extract_keywords(rule['patterns'])
            for kw in keywords:
                self.keyword_index.setdefault(kw, []).append(rule)
    
    def classify(self, text: str):
        # Extract keywords from text
        keywords = self._extract_text_keywords(text)
        
        # Get candidate rules from index
        candidates = set()
        for kw in keywords:
            candidates.update(self.keyword_index.get(kw, []))
        
        # Only match against candidates
        for rule in sorted(candidates, key=lambda r: -r['priority']):
            if self._match_rule(rule, text):
                return self._create_route(rule)
```
**Expected Gain**: 40-50% faster for long-tail queries

#### 2.2 Trie-based Pattern Matching
```python
# ใช้ Trie สำหรับ prefix matching
from pyahocorasick import Automaton

class IntentRouter:
    def __init__(self):
        self.automaton = Automaton()
        
    def _build_automaton(self):
        for rule in self.intent_rules:
            for pattern in rule['simple_patterns']:
                self.automaton.add_word(pattern, (pattern, rule))
        self.automaton.make_automaton()
    
    def classify(self, text: str):
        # Aho-Corasick algorithm: O(n + m + z)
        matches = list(self.automaton.iter(text.lower()))
        # Process matches...
```
**Expected Gain**: 60-70% faster pattern matching

#### 2.3 Config Caching
```python
# แคช parsed config เป็น pickle/json
import pickle, hashlib

class ConfigCache:
    CACHE_DIR = ".cache"
    
    def __init__(self):
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def _get_cache_key(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def load(self, file_path: str):
        cache_key = self._get_cache_key(file_path)
        cache_file = f"{self.CACHE_DIR}/{cache_key}.pkl"
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        # Parse and cache
        data = self._parse_yaml(file_path)
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        return data
```
**Expected Gain**: 50-80% faster config loading

---

### Phase 3: Long Term (High Impact, High Effort)

#### 3.1 Async Initialization
```python
# โหลด components แบบ async ขนานกัน
import asyncio

async def initialize_system():
    tasks = [
        asyncio.create_task(load_tools()),
        asyncio.create_task(load_router()),
        asyncio.create_task(load_planner()),
        asyncio.create_task(warmup_cache()),
    ]
    await asyncio.gather(*tasks)
```
**Expected Gain**: Parallel loading reduces total init time

#### 3.2 Rule Clustering with ML
```python
# ใช้ clustering จัดกลุ่ม rules ที่คล้ายกัน
from sklearn.cluster import KMeans

class SmartRouter:
    def __init__(self):
        self.clusters = {}
        self.cluster_model = None
    
    def train_clusters(self):
        # Embed patterns -> cluster similar rules
        embeddings = self._embed_patterns()
        self.cluster_model = KMeans(n_clusters=10)
        self.cluster_model.fit(embeddings)
    
    def classify(self, text: str):
        # Predict cluster first
        cluster_id = self.cluster_model.predict([text_embedding])[0]
        
        # Only search within cluster
        candidates = self.clusters[cluster_id]
        return self._match_best(candidates, text)
```
**Expected Gain**: 70-80% faster for large rule sets

#### 3.3 JIT Compilation for Hot Paths
```python
# ใช้ numba หรือ cython สำหรับ critical paths
from numba import jit

@jit(nopython=True)
def match_patterns(text: str, patterns: list) -> int:
    # Optimized pattern matching
    for i, pattern in enumerate(patterns):
        if pattern in text:
            return i
    return -1
```
**Expected Gain**: 2-5x faster for compute-intensive operations

---

### Phase 4: Infrastructure Optimizations

#### 4.1 Connection Pooling
```python
# ถ้ามี external API calls
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3,
    pool_block=False
)
session.mount('http://', adapter)
```

#### 4.2 Memory Profiling & Optimization
```bash
# ติดตั้ง memory profiler
pip install memory-profiler

# รัน profiling
python -m memory_profiler main.py
```

#### 4.3 Benchmarking Suite
```python
# tests/performance/test_benchmark.py
import pytest
import time

@pytest.mark.benchmark
def test_startup_time(benchmark):
    start = time.time()
    # Import and initialize
    from main import main
    elapsed = time.time() - start
    assert elapsed < 0.5  # Target: <500ms

@pytest.mark.benchmark
def test_classification_latency(benchmark):
    router = IntentRouter()
    
    def classify():
        return router.classify("ดูดวงให้หน่อย เกิด 8/8/1992")
    
    result = benchmark(classify)
    assert result.confidence > 0.9
```

---

## 📈 Expected Performance Gains

| Optimization | Current | After Opt | Improvement |
|-------------|---------|-----------|-------------|
| Startup Time | 0.12s | 0.05s | 2.4x faster |
| Classification | ~5ms | ~1ms | 5x faster |
| Memory Usage | ~50MB | ~20MB | 2.5x less |
| Cold Start | 0.12s | 0.02s | 6x faster |

---

## 🛠️ Implementation Priority

### Immediate (This Week)
1. ✅ Pattern caching (15 min)
2. ✅ Direct route shortcuts (30 min)
3. ✅ Config caching (1 hour)

### Short Term (Next Sprint)
4. Keyword indexing (4 hours)
5. Lazy rule loading (2 hours)
6. Benchmarking suite (3 hours)

### Medium Term (Next Month)
7. Aho-Corasick automation (1 day)
8. Async initialization (1 day)
9. Memory optimization (2 days)

### Long Term (Next Quarter)
10. ML-based clustering (1 week)
11. JIT compilation (3 days)
12. Full performance test suite (1 week)

---

## 📝 Monitoring & Metrics

```python
# เพิ่ม performance monitoring
from functools import wraps
import time

def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        if elapsed > 0.1:  # Log slow operations
            logger.warning(f"Slow operation: {func.__name__} took {elapsed:.3f}s")
        
        return result
    return wrapper

# Apply to critical functions
@measure_performance
def classify(self, text: str):
    # ...
```

---

## ✅ Success Criteria

- [ ] Startup time < 0.05s
- [ ] Classification latency < 2ms (p95)
- [ ] Memory usage < 30MB at idle
- [ ] Zero cold-start delays
- [ ] All optimizations backward compatible
- [ ] Comprehensive benchmark tests passing

---

## 🔧 Quick Start Implementation

```bash
# 1. Install dependencies
pip install pyahocorasick memory-profiler pytest-benchmark

# 2. Run baseline benchmarks
pytest tests/performance/ --benchmark-only

# 3. Implement Phase 1 optimizations
# Edit src/core/router.py and src/tools/registry.py

# 4. Verify improvements
pytest tests/performance/ --benchmark-only

# 5. Profile memory usage
python -m memory_profiler main.py
```

---

**เอกสารนี้สร้างเมื่อ**: $(date)
**ผู้เขียน**: WorAI Performance Team
**สถานะ**: พร้อมดำเนินการ
