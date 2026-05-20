# AI Integration Guide

## Overview
This guide explains how to integrate AI capabilities with the Personal Hub system using the three core agents: Auto-Generation, Self-Healing, and Template Curator.

---

## 1. Auto-Generation Agent Integration

### Use Cases
- Convert user requirements to code
- Generate UI components from design specs
- Create full project scaffolds

### API Endpoint
```http
POST /api/generate
Content-Type: application/json

{
  "request": "Create a personal dashboard with weather widget and task list",
  "preferences": {
    "theme": "dark",
    "layout": "bento-grid",
    "framework": "astro"
  }
}
```

### Response Format
```json
{
  "job_id": "gen_123456",
  "status": "processing",
  "estimated_time": "5s",
  "preview_url": null
}
```

### Polling for Completion
```http
GET /api/status/gen_123456
```

### Example Code (Client-side)
```javascript
async function generateProject(userRequest) {
  // Step 1: Submit generation request
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      request: userRequest,
      preferences: { theme: 'dark', layout: 'bento-grid' }
    })
  });
  
  const { job_id } = await response.json();
  
  // Step 2: Poll for completion
  while (true) {
    const status = await fetch(`/api/status/${job_id}`);
    const data = await status.json();
    
    if (data.status === 'completed') {
      window.open(data.preview_url, '_blank');
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}
```

---

## 2. Self-Healing Agent Integration

### Use Cases
- Automatic error detection and fixing
- Dependency conflict resolution
- Performance issue remediation

### API Endpoint
```http
POST /api/heal
Content-Type: application/json

{
  "error_context": {
    "message": "ModuleNotFoundError: No module named 'rapidfuzz'",
    "file": "/workspace/tools/tech_analyzer.py",
    "line": 15,
    "stack_trace": "..."
  },
  "auto_apply": true
}
```

### Response Format
```json
{
  "diagnosis": "Missing dependency: rapidfuzz",
  "fix_applied": true,
  "changes": [
    {
      "file": "requirements.txt",
      "action": "added",
      "diff": "+ rapidfuzz==3.5.2"
    }
  ],
  "verification": "All tests passed"
}
```

### Webhook for Real-time Notifications
```javascript
// Subscribe to healing events
const ws = new WebSocket('wss://your-hub.com/ws/healing');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Self-healing: ${data.diagnosis}`);
  console.log(`Fix applied: ${data.fix_applied}`);
};
```

---

## 3. Template Curator Agent Integration

### Use Cases
- Discover latest templates
- Update existing templates
- Validate template quality

### API Endpoint
```http
GET /api/templates?category=dashboard&min_score=90
```

### Response Format
```json
{
  "templates": [
    {
      "id": "personal-hub-v1",
      "name": "Personal Hub v1.0",
      "score": 95,
      "tech_stack": ["Astro 5.0", "Tailwind 4.0"],
      "last_updated": "2025-01-15",
      "download_url": "/templates/personal-hub-v1.zip"
    }
  ]
}
```

### Subscribe to Template Updates
```javascript
// Listen for new template notifications
navigator.serviceWorker.addEventListener('message', (event) => {
  if (event.data.type === 'NEW_TEMPLATE') {
    console.log(`New template available: ${event.data.template.name}`);
    // Show notification to user
  }
});
```

---

## 4. Combined Workflow Example

### Scenario: Build, Monitor, and Maintain a Personal Hub

```javascript
class PersonalHubBuilder {
  async createAndMaintain(requirements) {
    // Step 1: Generate initial project
    const generation = await this.generateProject(requirements);
    console.log(`Project created: ${generation.preview_url}`);
    
    // Step 2: Set up monitoring for errors
    this.setupErrorMonitoring(generation.job_id);
    
    // Step 3: Subscribe to template updates
    this.subscribeToTemplateUpdates();
    
    return generation;
  }
  
  async generateProject(requirements) {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request: requirements })
    });
    return await response.json();
  }
  
  setupErrorMonitoring(jobId) {
    // Poll for errors every 30 seconds
    setInterval(async () => {
      const status = await fetch(`/api/status/${jobId}`);
      const data = await status.json();
      
      if (data.errors && data.errors.length > 0) {
        // Trigger self-healing
        await fetch('/api/heal', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            error_context: data.errors[0],
            auto_apply: true
          })
        });
      }
    }, 30000);
  }
  
  subscribeToTemplateUpdates() {
    const ws = new WebSocket('wss://your-hub.com/ws/templates');
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'TEMPLATE_UPDATE_AVAILABLE') {
        const confirm = window.confirm(
          `New template version available: ${data.template.name}. Update now?`
        );
        if (confirm) {
          await this.updateTemplate(data.template.id);
        }
      }
    };
  }
  
  async updateTemplate(templateId) {
    const response = await fetch(`/api/templates/${templateId}/update`, {
      method: 'POST'
    });
    return await response.json();
  }
}

// Usage
const builder = new PersonalHubBuilder();
builder.createAndMaintain(
  'Create a personal hub with bento grid layout, dark mode, and weather widget'
);
```

---

## 5. Best Practices

### For Auto-Generation
- ✅ Be specific in requirements
- ✅ Include design preferences
- ✅ Review generated code before deployment
- ❌ Don't generate overly complex projects in one go

### For Self-Healing
- ✅ Enable auto-apply for known issues
- ✅ Review fix logs regularly
- ✅ Set up alerts for critical failures
- ❌ Don't disable verification tests

### For Template Curation
- ✅ Subscribe to security updates
- ✅ Test template updates in staging first
- ✅ Maintain a template version history
- ❌ Don't update all templates simultaneously

---

## 6. Troubleshooting

### Issue: Generation takes too long
**Solution:** Break down requirements into smaller tasks

### Issue: Self-healing fails repeatedly
**Solution:** Check error logs, may require manual intervention

### Issue: Template update breaks existing features
**Solution:** Rollback to previous version and report issue

---

## 7. Advanced Configuration

### Custom AI Models
```yaml
ai_config:
  default_provider: "anthropic"
  fallback_provider: "openai"
  models:
    code_generation: "claude-3-sonnet"
    error_diagnosis: "gpt-4-turbo"
    template_evaluation: "claude-3-haiku"
  rate_limits:
    requests_per_minute: 60
    tokens_per_day: 100000
```

### Custom Healing Rules
```yaml
custom_healing_rules:
  - pattern: "ImportError.*cannot import.*from '(.*)'"
    action: "check_circular_dependency"
    severity: "high"
    
  - pattern: "TypeError.*NoneType.*is not iterable"
    action: "add_null_check"
    severity: "medium"
```

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-15  
**Support:** docs@personal-hub.ai
