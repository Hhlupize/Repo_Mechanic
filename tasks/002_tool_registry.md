# Task 002 — Tool Registry
Implement safe subprocess wrapper and adapters:
- shell.run(cmd:list, cwd:Path, timeout:int) -> {code, out, err}
- pytest_tool.run(path) -> {code, failures:[{file,line,msg}]}
- ruff_tool.run(path), black_tool.run(path, check:bool)
- uv_tool.ensure_env(path, requirements:optional)
- git_tool.init_and_commit(msg)

Add basic type hints and unit tests for receipts error handling.

