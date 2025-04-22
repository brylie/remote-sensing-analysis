# Copilot instructions

## Package management

We use `uv` for package management. You can install packages using the following command:

```bash
uv add <package-name>
```

Do not use `pip` or `uv pip` commands.

## Type annotations

Ensure all functions have Python 3.10+ type annotations. Use `typing` for standard types and `typing_extensions` for newer types. For example:

We can now use primitive types like `int`, `str`, `float`, `bool`, and `None` as type annotations.