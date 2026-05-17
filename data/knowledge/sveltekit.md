อัพเดทให้แล้วไอสัส ตาม `svelte.dev/docs/ai/instructions` ล่าสุด 17/5/2026 🔥

ตอนนี้ Svelte 5 มี **MCP Server** ไว้ให้ AI ช่วยเขียนโค้ดโดยตรง ไม่ต้องเดา docs เก่าแล้ว

### **1. ติดตั้ง Svelte MCP Server ไว้ใช้กับ AI**

#### **แบบ Auto ติดตั้งพร้อมโปรเจค**
```bash
npx sv create my-app
npx sv add mcp
```
มันจะตั้ง `AGENTS.md` ให้เลย AI จะรู้ tools ทั้งหมด

#### **แบบ Manual Remote Setup**
ถ้าจะใช้กับ Claude Code / Gemini / Copilot CLI:
```bash
# Claude Code
claude mcp add -t http -s project svelte https://mcp.svelte.dev/mcp

# Gemini CLI
gemini mcp add -t http -s project svelte https://mcp.svelte.dev/mcp

# VS Code
Command Palette > "MCP: Add Server..." > ใส่ `npx -y @sveltejs/mcp`
```

### **2. Tools ที่ AI จะใช้ได้ มี 4 ตัวหลัก**

| Tool | ใช้ตอนไหน | คำสั่ง |
| --- | --- | --- |
| `list-sections` | **ใช้ก่อนเลย** หา docs ที่เกี่ยวกับงานที่ทำ | `npx @sveltejs/mcp list-sections` |
| `get-documentation` | ดึง docs เต็มของ section ที่เลือก ใช้หลัง `list-sections` | `npx @sveltejs/mcp get-documentation "$state,$derived"` |
| `svelte-autofixer` | **บังคับใช้ทุกครั้ง** ก่อนส่งโค้ด Svelte ให้ user เช็คจนไม่มี error | `npx @sveltejs/mcp svelte-autofixer <file>` |
| `playground-link` | สร้างลิงก์ Svelte Playground ถาม user ก่อนใช้ | `npx @sveltejs/mcp playground-link` |


### **3. Prompt ที่ต้องใส่ใน `AGENTS.md` หรือ `CLAUDE.md`**
ก๊อปอันนี้ไปวาง AI จะใช้ MCP ถูกวิธี

```
You are able to use the Svelte MCP server, where you have access to comprehensive Svelte 5 and SvelteKit documentation. Here's how to use the available tools effectively:

## Available Svelte MCP Tools:
### 1. list-sections
Use this FIRST to discover all available documentation sections. Returns a structured list with titles, use_cases, and paths.
When asked about Svelte or SvelteKit topics, ALWAYS use this tool at the start of the chat to find relevant sections.

### 2. get-documentation
After calling the list-sections tool, you MUST analyze the returned documentation sections and then use the get-documentation tool to fetch ALL documentation sections that are relevant for the user's task.

### 3. svelte-autofixer
You MUST use this tool whenever writing Svelte code before sending it to the user. Keep calling it until no issues or suggestions are returned.

### 4. playground-link
After completing the code, ask the user if they want a playground link. Only call this tool after user confirmation.
```

### **4. ต่อกับ WorAI Python มึง**

#### **SvelteKit เรียก API Python**
`src/routes/+page.svelte`
```svelte
<script lang="ts">
  let q = $state("");
  let a = $state("");

  async function ask() {
    // ก่อนส่งให้ user ต้องรัน svelte-autofixer เช็คก่อน
    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      body: JSON.stringify({text: q})
    });
    const data = await res.json();
    a = data.answer;
  }
</script>

<input bind:value={q} />
<button onclick={ask}>ถาม WorAI</button>
<p>{a}</p>
```
Svelte 5 ใช้ `$state` แทน `let`

#### **Python FastAPI เหมือนเดิม**
```python
from fastapi import FastAPI
from src.main import WorAI

app = FastAPI()
ai = WorAI()

@app.post("/ask")
def ask_ai(query: dict):
    return ai.run(query["text"])
```

### **5. กฎสำคัญสำหรับ AI เขียน Svelte 2026**

1. **Stores > Props** ถ้า state ใช้เกิน 2 component ให้ยัดลง `writable` ใน `src/lib/stores/`
2. **ห้าม `onMount async`** จะ memory leak ถ้า user navigate ไว
3. **Unsubscribe store** ถ้าใช้ `store.subscribe()` ใน `.ts` ต้องเก็บ `unsubscribe` แล้วเรียกตอนเลิกใช้
4. **ใช้ `$state`, `$derived`, `$effect`** ของ Svelte 5 แทน `writable` ถ้าเป็น local state



## Board
<!-- src/routes/+page.svelte -->
<script lang="typescript">
    // ==========================================
    // 1. TYPE DEFINITIONS & ARCHITECTURE
    // ==========================================
    type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

    interface Task {
        id: string;
        title: string;
        description: string;
        status: TaskStatus;
        createdAt: Date;
    }

    interface BoardColumn {
        id: TaskStatus;
        title: string;
        bgClass: string;
        borderClass: string;
    }

    // ==========================================
    // 2. STATE MANAGEMENT (Svelte 5 Runes)
    // ==========================================
    // Reactive State สำหรับเก็บรายการ Task ทั้งหมด
    let tasks = $state<Task[]>([
        { 
            id: '1', 
            title: 'Setup Svelte 5 Runes', 
            description: 'Migrate legacy codebase to state, derived, and effect architectures.', 
            status: 'TODO', 
            createdAt: new Date() 
        },
        { 
            id: '2', 
            title: 'Implement Project Board', 
            description: 'Combine reactive state with strict type-safety in a single view.', 
            status: 'IN_PROGRESS', 
            createdAt: new Date() 
        }
    ]);

    // Local State สำหรับควบคุม Form การกรอก Task ใหม่
    let newTitle = $state('');
    let newDescription = $state('');

    // Derived States (คำนวณอัตโนมัติเมื่อ tasks เปลี่ยนแปลง)
    let todoTasks = $derived(tasks.filter(t => t.status === 'TODO'));
    let inProgressTasks = $derived(tasks.filter(t => t.status === 'IN_PROGRESS'));
    let doneTasks = $derived(tasks.filter(t => t.status === 'DONE'));

    // Configuration สำหรับการ Render แต่ละคอลัมน์
    const columns: BoardColumn[] = [
        { id: 'TODO', title: 'To Do', bgClass: 'bg-slate-900/40', borderClass: 'border-slate-800' },
        { id: 'IN_PROGRESS', title: 'In Progress', bgClass: 'bg-indigo-950/20', borderClass: 'border-indigo-900/50' },
        { id: 'DONE', title: 'Done', bgClass: 'bg-emerald-950/10', borderClass: 'border-emerald-900/30' }
    ];

    // ==========================================
    // 3. BUSINESS LOGIC & UTILITIES
    // ==========================================
    function handleAddTask(e: SubmitEvent) {
        e.preventDefault();
        if (!newTitle.trim()) return;

        const newTask: Task = {
            id: crypto.randomUUID(),
            title: newTitle.trim(),
            description: newDescription.trim(),
            status: 'TODO',
            createdAt: new Date()
        };

        tasks.push(newTask);
        
        // Reset Inputs
        newTitle = '';
        newDescription = '';
    }

    function handleMoveTask(id: string, direction: 'forward' | 'backward') {
        const currentTask = tasks.find(t => t.id === id);
        if (!currentTask) return;

        const statusOrder: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'DONE'];
        const currentIndex = statusOrder.indexOf(currentTask.status);
        const nextIndex = direction === 'forward' ? currentIndex + 1 : currentIndex - 1;

        if (nextIndex >= 0 && nextIndex < statusOrder.length) {
            currentTask.status = statusOrder[nextIndex];
        }
    }

    function handleDeleteTask(id: string) {
        tasks = tasks.filter(t => t.id !== id);
    }

    // Helper Function สำหรับจับคู่ Derived State กับ Column ID
    function getTasksByColumnId(status: TaskStatus): Task[] {
        if (status === 'TODO') return todoTasks;
        if (status === 'IN_PROGRESS') return inProgressTasks;
        return doneTasks;
    }

    // Effect ทำหน้าที่ Track การเปลี่ยนแปลงของ State (มาแทนที่ $: console.log)
    $effect(() => {
        console.log(`[Board Monitor] Active Task Count: ${tasks.length}`);
    });
</script>

<!-- ==========================================
     4. USER INTERFACE LAYER (TailwindCSS)
     ========================================== -->
<main class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-6 md:p-12 text-slate-100 font-sans antialiased">
    
    <!-- Header Section -->
    <header class="mb-10 max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
            <h1 class="text-3xl md:text-4xl font-black tracking-tight bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
                Svelte 5 Reactive Board
            </h1>
            <p class="text-slate-400 text-sm mt-1">Single Component Architecture Driven by Svelte 5 Runes.</p>
        </div>
        <div class="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs font-mono">
            <span class="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Total Active Tasks: {tasks.length}
        </div>
    </header>

    <!-- Project Board Grid -->
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {#each columns as column (column.id)}
            <section class="flex flex-col rounded-2xl border {column.borderClass} {column.bgClass} p-5 h-[calc(100vh-240px)] min-h-[500px] backdrop-blur-sm transition-all duration-300">
                
                <!-- Column Title -->
                <div class="flex items-center justify-between mb-4 pb-2 border-b border-slate-800/60">
                    <div class="flex items-center gap-2">
                        <h3 class="font-bold text-slate-200 text-base tracking-wide">{column.title}</h3>
                        <span class="text-xs bg-slate-800 px-2 py-0.5 rounded-full font-semibold text-slate-400">
                            {getTasksByColumnId(column.id).length}
                        </span>
                    </div>
                </div>
                
                <!-- Tasks List Area -->
                <div class="flex flex-col gap-3 flex-1 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-800">
                    {#each getTasksByColumnId(column.id) as task (task.id)}
                        <!-- Task Card Item -->
                        <article class="p-4 bg-slate-900/90 rounded-xl border border-slate-800 hover:border-indigo-500/50 flex flex-col gap-3 shadow-lg group transition-all duration-200 hover:-translate-y-0.5">
                            <div class="flex justify-between items-start gap-2">
                                <h4 class="font-semibold text-slate-100 text-sm leading-snug tracking-wide group-hover:text-white transition-colors">
                                    {task.title}
                                </h4>
                                <button 
                                    onclick={() => handleDeleteTask(task.id)} 
                                    class="text-xs text-slate-500 hover:text-red-400 p-1 rounded-md hover:bg-red-500/10 transition-all"
                                    aria-label="Delete permanent task"
                                >
                                    ✕
                                </button>
                            </div>
                            
                            {#if task.description}
                                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                                    {task.description}
                                </p>
                            {/if}
                            
                            <div class="flex justify-between items-center mt-1 pt-3 border-t border-slate-800/80">
                                <span class="text-[10px] font-mono text-slate-500">
                                    {task.createdAt.toLocaleDateString()}
                                </span>
                                
                                <div class="flex gap-1.5">
                                    {#if task.status !== 'TODO'}
                                        <button 
                                            onclick={() => handleMoveTask(task.id, 'backward')}
                                            class="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md transition-colors font-medium"
                                            aria-label="Move back"
                                        >
                                            ←
                                        </button>
                                    {/if}
                                    {#if task.status !== 'DONE'}
                                        <button 
                                            onclick={() => handleMoveTask(task.id, 'forward')}
                                            class="px-2.5 py-1 text-xs bg-indigo-600 hover:bg-indigo-500 text-white rounded-md transition-colors font-medium shadow-sm shadow-indigo-600/20"
                                            aria-label="Move forward"
                                        >
                                            →
                                        </button>
                                    {/if}
                                </div>
                            </div>
                        </article>
                    {:else}
                        <!-- Empty State Inside Column -->
                        <div class="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-slate-800/60 rounded-xl px-4 h-full">
                            <p class="text-xs text-slate-500 font-medium tracking-wide">No tasks available</p>
                        </div>
                    {/each}
                </div>

                <!-- Footer Context (เฉพาะคอลัมน์ TODO เท่านั้น สำหรับเพิ่มข้อมูล) -->
                {#if column.id === 'TODO'}
                    <div class="mt-4 pt-4 border-t border-slate-800/80">
                        <form onsubmit={handleAddTask} class="flex flex-col gap-2.5">
                            <input 
                                type="text" 
                                bind:value={newTitle} 
                                placeholder="Task Title..." 
                                class="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                                required
                            />
                            <textarea 
                                bind:value={newDescription} 
                                placeholder="Add detailed description..." 
                                class="w-full px-3 py-2 text-xs rounded-lg bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none"
                                rows="2"
                            ></textarea>
                            <button 
                                type="submit" 
                                class="w-full py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold rounded-lg transition-all shadow-md shadow-indigo-900/30 active:scale-[0.98]"
                            >
                                + Add New Task
                            </button>
                        </form>
                    </div>
                {/if}

            </section>
        {/each}
    </div>
</main>





## Kanban

<script>
	// --- Props Definition (Svelte 5 Runes) ---
	// รับข้อมูล Columns และ Tasks แบบ Two-way Binding ($bindable)
	let {
		columns = $bindable([
			{ id: 'todo', title: 'To Do' },
			{ id: 'in-progress', title: 'In Progress' },
			{ id: 'done', title: 'Done' }
		]),
		tasks = $bindable([
			{ id: '1', columnId: 'todo', title: 'ออกแบบ UI ของระบบ', description: 'วาด Wireframe และกำหนด Color Palette' },
			{ id: '2', columnId: 'todo', title: 'เขียนโครงสร้าง Board.svelte', description: 'ใช้ Svelte 5 Runes ในการจัดการ State' },
			{ id: '3', columnId: 'in-progress', title: 'ทดสอบระบบ Drag & Drop', description: 'ลองรันและขยับการ์ดงานใน REPL' },
			{ id: '4', columnId: 'done', title: 'สร้าง Box Component', description: 'เสร็จสิ้นและพร้อมใช้งาน' }
		])
	} = $props();

	// --- Internal State ---
	let draggedTaskId = $state(null);
	let newCardTitles = $state({}); // เก็บค่า Input ของการ์ดใหม่ตามแต่ละ Column

	// --- Drag and Drop Logic ---
	function handleDragStart(taskId) {
		draggedTaskId = taskId;
	}

	function handleDragOver(event) {
		event.preventDefault(); // จำเป็นต้องมีเพื่อให้เกิดการ Drop ได้
	}

	function handleDrop(columnId) {
		if (!draggedTaskId) return;
		
		// อัปเดต columnId ของ Task ที่ถูกลากด้วย Svelte 5 Mutated State
		tasks = tasks.map(task => {
			if (task.id === draggedTaskId) {
				return { ...task, columnId };
			}
			return task;
		});
		
		draggedTaskId = null;
	}

	// --- Task Management Logic ---
	function addTask(columnId) {
		const title = newCardTitles[columnId]?.trim();
		if (!title) return;

		const newTask = {
			id: crypto.randomUUID(),
			columnId,
			title,
			description: 'คลิกเพื่อแก้ไขคำอธิบาย...'
		};

		tasks = [...tasks, newTask];
		newCardTitles[columnId] = ''; // ล้างช่องกรอกข้อมูล
	}

	function deleteTask(taskId) {
		tasks = tasks.filter(t => t.id !== taskId);
	}
</script>

<div class="kanban-board">
	{#each columns as column}
		<!-- Column Container -->
		<div 
			class="kanban-column"
			ondragover={handleDragOver}
			ondrop={() => handleDrop(column.id)}
		>
			<div class="column-header">
				<h3>{column.title}</h3>
				<span class="task-count">
					{tasks.filter(t => t.columnId === column.id).length}
				</span>
			</div>

			<!-- Tasks List -->
			<div class="task-list">
				{#each tasks.filter(t => t.columnId === column.id) as task (task.id)}
					<!-- Task Card (Draggable) -->
					<div 
						class="task-card" 
						draggable="true"
						ondragstart={() => handleDragStart(task.id)}
					>
						<div class="card-header">
							<h4>{task.title}</h4>
							<button class="delete-btn" onclick={() => deleteTask(task.id)} aria-label="Delete task">×</button>
						</div>
						{#if task.description}
							<p class="card-desc">{task.description}</p>
						{/if}
					</div>
				{/each}
			</div>

			<!-- Add Task Form -->
			<div class="add-task-form">
				<input 
					type="text" 
					placeholder="+ เพิ่มการ์ดงานใหม่..." 
					bind:value={newCardTitles[column.id]}
					onkeydown={(e) => e.key === 'Enter' && addTask(column.id)}
				/>
				{#if newCardTitles[column.id]?.trim()}
					<button onclick={() => addTask(column.id)}>เพิ่ม</button>
				{/if}
			</div>
		</div>
	{/each}
</div>

<style>
	/* --- Scoped CSS สำหรับ REPL --- */
	.kanban-board {
		display: flex;
		gap: 16px;
		padding: 16px;
		background-color: #f8fafc;
		border-radius: 12px;
		overflow-x: auto;
		font-family: system-ui, -apple-system, sans-serif;
		align-items: flex-start;
		min-height: 500px;
	}

	.kanban-column {
		flex: 1;
		min-width: 280px;
		background-color: #f1f5f9;
		border-radius: 8px;
		padding: 12px;
		box-shadow: 0 1px 3px rgba(0,0,0,0.05);
		display: flex;
		flex-direction: column;
		max-height: 100%;
	}

	.column-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 12px;
		padding: 0 4px;
	}

	.column-header h3 {
		margin: 0;
		font-size: 16px;
		font-weight: 600;
		color: #334155;
	}

	.task-count {
		background-color: #cbd5e1;
		color: #475569;
		font-size: 12px;
		font-weight: bold;
		padding: 2px 8px;
		border-radius: 9999px;
	}

	.task-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-height: 100px; /* ยืดพื้นที่เพื่อให้ Drop วางได้ง่ายเมื่อคอลัมน์ว่าง */
		overflow-y: auto;
	}

	.task-card {
		background-color: #ffffff;
		padding: 12px;
		border-radius: 6px;
		box-shadow: 0 1px 2px rgba(0,0,0,0.1);
		cursor: grab;
		transition: transform 0.1s, box-shadow 0.1s;
		border: 1px solid #e2e8f0;
	}

	.task-card:active {
		cursor: grabbing;
		transform: scale(0.98);
		box-shadow: 0 4px 6px rgba(0,0,0,0.05);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 8px;
	}

	.card-header h4 {
		margin: 0;
		font-size: 14px;
		font-weight: 500;
		color: #1e293b;
	}

	.delete-btn {
		background: none;
		border: none;
		color: #94a3b8;
		font-size: 18px;
		cursor: pointer;
		padding: 0 4px;
		line-height: 1;
	}

	.delete-btn:hover {
		color: #ef4444;
	}

	.card-desc {
		margin: 4px 0 0 0;
		font-size: 12px;
		color: #64748b;
	}

	.add-task-form {
		margin-top: 12px;
		display: flex;
		gap: 4px;
	}

	.add-task-form input {
		flex: 1;
		padding: 8px;
		border: 1px solid #cbd5e1;
		border-radius: 6px;
		font-size: 13px;
		background-color: #ffffff;
	}

	.add-task-form input:focus {
		outline: none;
		border-color: #3b82f6;
	}

	.add-task-form button {
		background-color: #2563eb;
		color: white;
		border: none;
		padding: 0 12px;
		border-radius: 6px;
		font-size: 13px;
		cursor: pointer;
	}

	.add-task-form button:hover {
		background-color: #1d4ed8;
	}
</style>

# SvelteKit Routing

## File-based Routing
```
src/routes/
├── +page.svelte        # / (home)
├── +layout.svelte      # layout หลัก
├── about/
│   └── +page.svelte    # /about
├── blog/
│   ├── +page.svelte    # /blog (list)
│   ├── +page.server.ts # load data ฝั่ง server
│   └── [slug]/
│       └── +page.svelte # /blog/:slug
└── api/
    └── hello/
        └── +server.ts  # API endpoint
```

## Loading Data
```typescript
```typescript
// +page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
  const post = await fetch(`/api/posts/${params.slug}`);
  return { post: await post.json() };
};
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  let { data } = $props();  // data มาจาก load function
</script>

<h1>{data.post.title}</h1>
```
```

## Server Endpoints (+server.ts)
```typescript
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  return json({ message: 'Hello from API' });
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  return json({ received: body }, { status: 201 });
};
```

# SvelteKit Forms

## Progressive Enhancement Forms
```svelte
<!-- +page.svelte -->
```svelte
<script lang="ts">
  let { form } = $props();
</script>

<form method="POST" action="?/create">
  <input name="title" required />
  <textarea name="content"></textarea>
  <button type="submit">สร้าง</button>
</form>

{#if form?.success}
  <p class="text-green-600">สร้างสำเร็จ!</p>
{/if}
```

<!-- +page.server.ts -->
```typescript
import { fail } from '@sveltejs/kit';

export const actions = {
  create: async ({ request }) => {
    const data = await request.formData();
    const title = data.get('title');
    
    if (!title) {
      return fail(400, { error: 'Title is required' });
    }
    
    // บันทึกลง database
    return { success: true };
  }
};
```
```

## Form Validation
- ใช้ Zod สำหรับ validate schema: `z.string().min(3).email()`
- แยก validation logic เป็น utility function
- แสดง error กลับไปที่ form ด้วย `fail()`

# SvelteKit SSR and CSR

## SSR (Server-Side Rendering)
- `+page.server.ts` = รันที่ server ก่อนส่ง HTML
- ดีสำหรับ SEO, โหลดเร็วครั้งแรก
- ไม่มี access ถึง browser APIs (window, document)

## CSR (Client-Side Rendering)
- `+page.ts` = รันที่ client และ server
- ใช้สำหรับ data ที่ไม่ต้องการ SEO
- มี access ถึง browser APIs ฝั่ง client

## Streaming
```typescript
// ส่ง HTML ทีละส่วนโดยไม่รอทั้งหมด
export const load = async () => {
  return {
    streamed: {
      slowData: new Promise(resolve => {
        setTimeout(() => resolve('loaded!'), 2000);
      })
    }
  };
};
```

# SvelteKit Stores and State

## When to use what
| ใช้ | เมื่อไหร |
|-----|----------|
| `$state` | State ภายใน component |
| `$derived` | คำนวณจาก state อื่น |
| `$effect` | Side effects (console, fetch, DOM) |
| `writable` store | แชร์ state ข้ามหลาย component |
| `derived` store | คำนวณจาก store อื่น |

## Writable Store Example
```typescript
// src/lib/stores/counter.ts
import { writable } from 'svelte/store';

export const count = writable(0);
```

```svelte
<!-- Component A -->
<script>
  import { count } from '$lib/stores/counter';
  
  function increment() {
    count.update(n => n + 1);
  }
</script>
<button onclick={increment}>+</button>
```

```svelte
<!-- Component B -->
<script>
  import { count } from '$lib/stores/counter';
</script>
<p>Count: {$count}</p>
```

## Context API (ส่งข้อมูลลงลูก)
```svelte
<!-- Parent.svelte -->
<script>
  import { setContext } from 'svelte';
  setContext('user', { name: 'WorAI', role: 'admin' });
</script>
```

```svelte
<!-- Child.svelte -->
<script>
  import { getContext } from 'svelte';
  const user = getContext('user');
</script>
```

## Snippets (Svelte 5)
```svelte
{#snippet card(title, content)}
  <div class="card">
    <h3>{title}</h3>
    <p>{content}</p>
  </div>
{/snippet}

{@render card('Hello', 'World')}
```

# SvelteKit Deployment

## Adapter Options
- **@sveltejs/adapter-auto**: ตรวจจับ platform อัตโนมัติ
- **@sveltejs/adapter-node**: สำหรับ Node.js server
- **@sveltejs/adapter-static**: สำหรับ static hosting (Netlify, Vercel)
- **@sveltejs/adapter-vercel**: ใช้ serverless functions
- **@sveltejs/adapter-netlify**: ใช้ Netlify functions

## Environment Variables
```typescript
// .env
PUBLIC_API_URL=https://api.example.com
PRIVATE_DATABASE_URL=postgresql://...

// +page.svelte
import { PUBLIC_API_URL } from '$env/static/public';

// +page.server.ts
import { PRIVATE_DATABASE_URL } from '$env/static/private';
```

# SvelteKit Middleware and Hooks

## Hooks (server side)
```typescript
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  // ตรวจสอบ authentication
  const token = event.cookies.get('session');
  event.locals.user = await getUserFromToken(token);
  
  const response = await resolve(event);
  return response;
};
```

## Error Handling
```typescript
// src/hooks.server.ts
export const handleError = ({ error, event }) => {
  console.error('Error:', error);
  return {
    message: 'เกิดข้อผิดพลาด กรุณาลองใหม่',
    code: error.code || 'UNKNOWN'
  };
};
```

## Middleware Pattern
- `sequence()` สำหรับรวมหลาย hooks
- เรียงตามลำดับ: auth → logging → resolve
