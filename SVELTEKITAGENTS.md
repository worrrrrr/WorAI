จัดให้ไอสัส `AGENTS.md` สำหรับโปรเจค WorAI มึงเลย ก๊อปไปวาง root โปรเจคได้ทันที 🚀

```markdown
# AGENTS.md - WorAI + SvelteKit 5 Instructions

You are a Svelte 5 + SvelteKit expert building the WorAI frontend. You have access to the Svelte MCP server for up-to-date documentation.

## Critical Rules for This Project

### 1. Always Use MCP Tools First
Before answering any Svelte/SvelteKit question:
1. Call `list-sections` to discover relevant docs
2. Call `get-documentation` to fetch sections matching user's task
3. Only then write code using your knowledge + docs

### 2. Code Quality Gates
You MUST run `svelte-autofixer` on ALL Svelte code before sending to user. Loop until no issues returned. This is non-negotiable.

### 3. Svelte 5 Syntax Only
This project uses Svelte 5 Runes. Never use Svelte 4 syntax.

| Old Svelte 4 | New Svelte 5 |
| --- | --- |
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `onMount()` | `$effect(() => {})` |
| `export let prop` | `let { prop } = $props()` |
| `on:click` | `onclick` |

### 4. WorAI Integration Pattern
All WorAI calls go through Python FastAPI at `http://localhost:8000/ask`

**Frontend `/src/routes/+page.svelte` pattern:**
```svelte
<script lang="ts">
  let question = $state("");
  let answer = $state("");
  let loading = $state(false);
  let intent = $state("");

  async function askWorAI() {
    loading = true;
    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: question})
      });
      const data = await res.json();
      answer = data.answer ?? data.response ?? "ไม่รู้ว่ะ";
      intent = data.intent ?? "";
    } catch (e) {
      answer = "เชื่อม API ไม่ได้ ไอสัส";
    } finally {
      loading = false;
    }
  }
</script>

<main>
  <h1>WorAI Chat</h1>
  <input bind:value={question} placeholder="พิมพ์คำถาม..." />
  <button onclick={askWorAI} disabled={loading}>
    {loading ? "กำลังคิด..." : "ถาม"}
  </button>
  {#if intent}<p class="intent">Intent: {intent}</p>{/if}
  <p class="answer">{answer}</p>
</main>
```

### 5. State Management Rules
1. **Local state**: Use `$state` and `$derived` 
2. **Shared state 2+ components**: Use `writable` in `src/lib/stores/`
3. **Never use `onMount(async)`**: Use `$effect` with cleanup
4. **Always unsubscribe**: If you `.subscribe()` manually, store the `unsubscribe` and call it

**Example Store `src/lib/stores/chat.ts`:**
```typescript
import { writable } from 'svelte/store';

export const chatHistory = writable<Array<{q: string, a: string}>>([]);
```

### 6. File Structure
```
src/
├── routes/
│   ├── +page.svelte          # Main chat UI
│   ├── +layout.svelte        # Global layout
│   └── api/                  # SvelteKit server routes if needed
├── lib/
│   ├── components/           # Reusable UI
│   ├── stores/               # Global stores
│   └── worai.ts              # WorAI API client
└── app.html
```

### 7. Available Svelte MCP Tools
#### 1. list-sections
Use FIRST to discover all available documentation sections. Returns titles, use_cases, and paths.

#### 2. get-documentation  
Retrieves full documentation. After list-sections, fetch ALL relevant sections for the task.

#### 3. svelte-autofixer
Analyzes Svelte code. MUST use before sending code to user. Keep calling until clean.

#### 4. playground-link
Generates Svelte Playground link. Ask user first. NEVER use if code was written to project files.

### 8. Python Backend Contract
WorAI API expects:
```json
POST /ask
{"text": "อากาศเชียงใหม่เป็นไง"}
```
Returns:
```json
{
  "answer": "ตอนนี้เชียงใหม่ 28 องศา...",
  "intent": "search_knowledge",
  "source": "internal_kb: อากาศเชียงใหม่"
}
```

### 9. Before You Generate Code
1. Run `list-sections` if touching Svelte/SvelteKit
2. Run `get-documentation` for relevant sections  
3. Write code using Svelte 5 Runes
4. Run `svelte-autofixer` until clean
5. Ask if user wants `playground-link`

Do not skip these steps. Do not use Svelte 4 syntax. Do not forget CORS on Python side.
```

---

วางไฟล์นี้เสร็จ เวลามึงใช้ Claude Code / Cursor / Codex มันจะเขียน Svelte 5 ให้ถูกหมด ไม่มั่ว Runes

กลับมาเมื่อไหร่ก็สั่งกูต่อได้ จะเอาเป็น artifact UI สวยๆก็ได้เลยไอสัส 🚀