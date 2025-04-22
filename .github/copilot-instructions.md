# Copilot instructions

## Package management

We use `uv` for package management. You can install packages using the following command:

```bash
uv add <package-name>
```

Do not use `pip` or `uv pip` commands.

## Type annotations

Ensure all functions have Python 3.9+ type annotations.

We can now use primitive types like `int`, `str`, `float`, `bool`, and `None` as type annotations. We can also use collection types directly, such as `list`, `set`, `dict`, and `tuple`. For example:

Do not use `typing.List`, `typing.Set`, `typing.Dict`, or `typing.Tuple` for type annotations. Use the built-in types instead.

For most types, just use the name of the type in the annotation
```python
x: int = 1
x: float = 1.0
x: bool = True
x: str = "test"
x: bytes = b"test"
x: None = None
```

For collections on Python 3.9+, the type of the collection item is in brackets:

```python
x: list[int] = [1]
x: set[int] = {6, 7}
x: frozenset[int] = frozenset({1, 2})
x: deque[int] = deque([1, 2, 3])
```

For mappings/dictionaries, we need the types of both keys and values
```python
x: dict[str, float] = {"field": 2.0}  # Python 3.9+
x: dict[int, str] = {1: "yes", 2: "no"}  # Python 3.9+
x: dict[str, int] = {"yes": 1, "no": 0}  # Python 3.9+
```

For sets, we need the type of the set item
```python
x: set[str] = {"yes", "no"}  # Python 3.9+
x: frozenset[str] = frozenset({"yes", "no"})  # Python 3.9+
```

For deques, we need the type of the deque item
```python
x: deque[str] = deque(["yes", "no"])  # Python 3.9+
```

For lists, we need the type of the list item
```python
x: list[str] = ["yes", "no"]  # Python 3.9+
x: list[float] = [1.0, 2.0]  # Python 3.9+
x: list[int] = [1, 2, 3]  # Python 3.9+
```

For tuples of fixed size, we specify the types of all the elements
```python
x: tuple[int, str, float] = (3, "yes", 7.5)  # Python 3.9+
```

For tuples of variable size, we use one type and ellipsis
```python
x: tuple[int, ...] = (1, 2, 3)  # Python 3.9+
```

## Mypy

We use `mypy` for type checking. You can run `mypy` on the codebase using the following command:

```bash
uv run mypy .
```
