# System Architecture Specification

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (Web Dashboard / CLI / API Gateway)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestration Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Auto-Gen     │  │ Self-Healing │  │ Template     │       │
│  │ Agent        │  │ Agent        │  │ Curator      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Skills Execution Layer                    │
│  [Tech Analyzer] [Stack Validator] [Code Generator] ...     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data & Storage Layer                      │
│  [SQLite/WASM] [Cache] [Vector DB] [File System]            │
└─────────────────────────────────────────────────────────────┘
```

## 2. Technology Stack

### Frontend (Personal Hub)
- **Framework:** Astro 5.0+
  - Islands Architecture for zero-bundle-size components
  - SSR/SSG hybrid rendering
  - Built-in image optimization
  
- **Styling:** Tailwind CSS 4.0
  - Rust-based engine for fast compilation
  - CSS Variables for theming
  - Dark mode support out-of-the-box
  
- **UI Components:** 
  - Shadcn/ui (Astro-compatible)
  - Custom Bento Grid components
  - Glassmorphism effects with backdrop-filter

- **State Management:** 
  - Nano Stores (lightweight, framework-agnostic)
  - Persistent storage with IndexedDB

### Backend (Edge Functions)
- **Runtime:** Hono on Cloudflare Workers / Vercel Edge
  - Ultra-fast cold starts (<50ms)
  - Global distribution
  - TypeScript native
  
- **API Design:** REST + GraphQL hybrid
  - REST for simple CRUD
  - GraphQL for complex queries with relationships

### Database
- **Primary:** SQLite via WASM (client-side)
  - Zero network latency for local data
  - Full SQL support
  - Automatic sync when online
  
- **Sync Backend:** Turso (libSQL)
  - Edge-distributed SQLite
  - Real-time replication
  - Pay-per-use pricing

### AI Integration
- **On-Device:** WebLLM (for simple tasks)
  - No API costs
  - Privacy-first
  - Works offline
  
- **Cloud AI:** Vercel AI SDK
  - Streaming responses
  - Multiple provider support (OpenAI, Anthropic, etc.)
  - Built-in rate limiting

### DevOps & Deployment
- **CI/CD:** GitHub Actions
  - Automated testing
  - Preview deployments
  - Performance budget checks
  
- **Hosting:** Vercel / Cloudflare Pages
  - Edge deployment
  - Automatic HTTPS
  - DDoS protection

## 3. Data Flow Architecture

### Request Processing Pipeline
```
1. User Input → Input Validation → Intent Classification
2. Intent → Skill Selection → Parameter Extraction
3. Parameters → Skill Execution → Result Aggregation
4. Results → Response Formatting → Output Delivery
5. Interaction → Logging → Analytics Update
```

### Caching Strategy
```yaml
layers:
  - L1: Memory Cache (LRU, 100MB max)
    ttl: 5 minutes
    items: ["recent_queries", "skill_results"]
    
  - L2: Disk Cache (SQLite)
    ttl: 24 hours
    items: ["generated_code", "tech_analysis"]
    
  - L3: CDN Cache (Edge)
    ttl: 7 days
    items: ["static_assets", "templates"]
```

## 4. Agent System Design

### Auto-Generation Agent
**Responsibilities:**
- Parse user requirements into structured specs
- Select appropriate templates from library
- Generate code using skill_code_gen
- Validate output against design.md
- Deploy to preview environment

**Workflow:**
```python
def auto_generate(user_request):
    # Step 1: Analyze request
    specs = ai_parse(user_request, context=["design.md", "skill.md"])
    
    # Step 2: Select template
    template = template_curator.find_best_match(specs.requirements)
    
    # Step 3: Generate code
    files = code_generator.generate(
        template=template,
        specs=specs,
        design_tokens=load_design_tokens()
    )
    
    # Step 4: Validate
    validation = stack_validator.validate(files.dependencies)
    if not validation.compatible:
        return self_healing_agent.fix(validation.issues)
    
    # Step 5: Deploy
    deployment = deploy_to_preview(files)
    
    return {
        "preview_url": deployment.url,
        "files": files,
        "instructions": generate_setup_guide(files)
    }
```

### Self-Healing Agent
**Responsibilities:**
- Monitor error logs and test failures
- Diagnose root causes using pattern matching
- Apply fixes automatically
- Verify fixes with test suite
- Document learnings for future prevention

**Healing Strategies:**
```yaml
error_patterns:
  - pattern: "ModuleNotFoundError"
    diagnosis: "Missing dependency"
    action: "Add to package.json and reinstall"
    
  - pattern: "Type mismatch in {file}"
    diagnosis: "TypeScript type error"
    action: "Infer correct type from usage context"
    
  - pattern: "CORS policy blocked"
    diagnosis: "API endpoint misconfiguration"
    action: "Update CORS settings in edge function"
    
  - pattern: "Database locked"
    diagnosis: "Concurrent write conflict"
    action: "Implement optimistic locking with retry"
```

### Template Curator Agent
**Responsibilities:**
- Scan GitHub, npm for trending templates
- Evaluate templates against quality metrics
- Update existing templates with latest practices
- Maintain compatibility matrix
- Version control all templates

**Evaluation Criteria:**
```json
{
  "performance_score": "Lighthouse score > 90",
  "accessibility_score": "axe-core score > 95",
  "best_practices": "ESLint + Prettier compliant",
  "documentation": "README with setup instructions",
  "test_coverage": "> 80% unit tests",
  "maintenance": "Updated within last 3 months"
}
```

## 5. File Structure

```
/workspace
├── docs/
│   ├── design.md          # Design system specification
│   ├── skill.md           # Skills registry
│   └── architect.md       # This file
├── agents/
│   ├── auto_generator.py  # Auto-generation logic
│   ├── self_healer.py     # Self-healing logic
│   └── template_curator.py # Template management
├── tools/
│   ├── tech_analyzer.py
│   ├── stack_validator.py
│   ├── code_generator.py
│   └── perf_optimizer.py
├── templates/
│   ├── personal-hub-v1/
│   ├── dashboard-v1/
│   └── portfolio-v1/
├── logs/
│   ├── agent_actions.log
│   ├── errors.log
│   └── performance.log
└── cache/
    ├── config_cache.pkl
    ├── rule_index.json
    └── generated_code/
```

## 6. Communication Protocols

### Internal Agent Communication
- **Format:** JSON-RPC 2.0
- **Transport:** In-memory message queue (for single-process)
- **Serialization:** MessagePack for efficiency

### External API
- **REST Endpoints:**
  - `POST /api/generate` - Trigger auto-generation
  - `GET /api/status/{job_id}` - Check job status
  - `POST /api/heal` - Trigger self-healing
  - `GET /api/templates` - List available templates
  
- **WebSocket:**
  - Real-time progress updates
  - Live preview streaming
  - Collaborative editing support

## 7. Security Considerations

### Code Generation Safety
- Sandboxed execution environment (Firecracker microVMs)
- No network access during code generation
- Dependency scanning for vulnerabilities (npm audit, pip-audit)
- Rate limiting to prevent abuse

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- GDPR compliance for user data
- Automatic data purging after 30 days

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key rotation every 90 days
- OAuth 2.0 for third-party integrations

## 8. Scalability Plan

### Horizontal Scaling
- Stateless agent design for easy replication
- Load balancing with consistent hashing
- Distributed caching with Redis Cluster
- Database sharding by user ID

### Performance Targets
| Metric | Target | Current |
|--------|--------|---------|
| Cold Start | < 100ms | 78ms ✅ |
| Code Generation | < 5s | - |
| Self-Healing Detection | < 1s | - |
| Template Search | < 50ms | - |
| API Response (p95) | < 200ms | - |

## 9. Monitoring & Observability

### Metrics Collection
- Prometheus for time-series data
- Custom exporters for agent-specific metrics
- Real-time dashboards with Grafana

### Logging
- Structured logging (JSON format)
- Correlation IDs for request tracing
- Log aggregation with Loki

### Alerting
- PagerDuty integration for critical alerts
- Slack notifications for warnings
- Automatic incident creation

## 10. Version Control & Evolution

### Versioning Strategy
- Semantic Versioning (MAJOR.MINOR.PATCH)
- Backward compatibility for minor versions
- Deprecation notices 6 months in advance

### Migration Path
```yaml
version: "2.0"
breaking_changes: []
deprecations:
  - feature: "legacy_template_format"
    removal_date: "2025-06-01"
    migration_guide: "/docs/migrations/v2-templates.md"
new_features:
  - "fuzzy_matching_v2"
  - "multi_agent_orchestration"
```

## 11. Future Roadmap

### Q1 2025
- [ ] Implement fuzzy matching with rapidfuzz
- [ ] Add LRU caching for query results
- [ ] Build interactive blueprint builder

### Q2 2025
- [ ] Integrate WebLLM for offline AI
- [ ] Launch template marketplace
- [ ] Add collaborative editing features

### Q3 2025
- [ ] ML-based trend prediction model
- [ ] Advanced self-healing with reinforcement learning
- [ ] Multi-language support (i18n)

---

**Document Info:**
- Version: 1.0.0
- Last Updated: 2025-01-15
- Maintained By: System Architecture Team
- Review Cycle: Quarterly
