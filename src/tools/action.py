def tool_action_executor(command: str = None, raw_text: str = None, **kwargs): 
    return {"success": True, "status": "executed", "command": command or raw_text}
