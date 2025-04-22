# Copilot instructions

## Package management

We use `uv` for package management. You can install packages using the following command:

```bash
uv add <package-name>
```

Do not use `pip` or `uv pip` commands.

## Type annotations

Ensure all functions have Python 3.9+ type annotations. Use `typing` for standard types and `typing_extensions` for newer types. For example:

We can now use primitive types like `int`, `str`, `float`, `bool`, and `None` as type annotations.

For most types, just use the name of the type in the annotation
Note that mypy can usually infer the type of a variable from its value,
so technically these annotations are redundant
x: int = 1
x: float = 1.0
x: bool = True
x: str = "test"
x: bytes = b"test"

For collections on Python 3.9+, the type of the collection item is in brackets
x: list[int] = [1]
x: set[int] = {6, 7}

For mappings, we need the types of both keys and values
x: dict[str, float] = {"field": 2.0}  # Python 3.9+

For tuples of fixed size, we specify the types of all the elements
x: tuple[int, str, float] = (3, "yes", 7.5)  # Python 3.9+

For tuples of variable size, we use one type and ellipsis
x: tuple[int, ...] = (1, 2, 3)  # Python 3.9+
