def tool_workflow_executor(task: str = None, raw_text: str = None, title: str = None, **kwargs): 
    t = task or title or raw_text or "งานใหม่"
    return {"success": True, "task_id": f"TASK-{hash(t)%10000:04d}", "status": "created"}
