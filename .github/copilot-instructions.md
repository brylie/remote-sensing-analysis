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

## Testing

We use `pytest` for unit testing. When writing tests, follow these guidelines:

### Running tests

Tests can be run using the `pytest` command through `uv run`:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests for a specific module
uv run pytest tests/processors/

# Run a specific test file
uv run pytest tests/processors/test_preprocessing.py
```

### Test structure

1. Place tests in the `tests/` directory, mirroring the structure of the `src/` directory
2. Name test files with the prefix `test_`
3. Name test classes with the prefix `Test`
4. Name test methods with the prefix `test_`

### Test fixtures

Use pytest fixtures for test setup and teardown:

```python
import pytest

@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    return {"key": "value"}

def test_function(sample_data):
    """Test using the fixture"""
    assert sample_data["key"] == "value"
```

### Mocking

Use the `unittest.mock` module for mocking external dependencies. When mocking, be sure to:

1. Only mock what is necessary
2. Correctly configure the mock's return values and behavior
3. Restore the original implementation after the test

```python
from unittest import mock

def test_with_mock():
    with mock.patch("module.function") as mock_function:
        mock_function.return_value = "mocked value"
        # Test code using the mocked function
        assert module.function() == "mocked value"
```

### Test coverage

We use `pytest-cov` to measure test coverage. Aim for at least 80% coverage for new code:

```bash
# Run tests with coverage report
uv run pytest --cov=src

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# View coverage for specific modules
uv run pytest --cov=src.processors --cov=src.statistics
```

After generating the HTML report, open `htmlcov/index.html` in your browser to view detailed coverage information.

### Testing best practices

1. **Test one thing per test**: Each test function should test a single aspect of functionality
2. **Arrange, Act, Assert**: Organize tests into setup, execution, and verification phases
3. **Keep tests independent**: Tests should not depend on the state or results of other tests
4. **Test edge cases**: Include tests for boundary conditions and error scenarios
5. **Use meaningful assertions**: Choose assertions that clearly indicate what is being tested

### Example test

```python
import pytest
from unittest import mock
import numpy as np
from src.statistics.distribution import StatisticsCalculator

class TestStatisticsCalculator:
    """Tests for the StatisticsCalculator class"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)  # Set seed for reproducibility
        return np.random.normal(5, 2, 1000)

    def test_calculate_basic_stats(self, sample_data):
        """Test basic statistics calculation"""
        # Arrange - setup is handled by the fixture

        # Act
        stats = StatisticsCalculator.calculate_basic_stats(sample_data)

        # Assert
        assert "mean" in stats
        assert "median" in stats
        assert abs(stats["mean"] - np.mean(sample_data)) < 1e-10
        assert abs(stats["median"] - np.median(sample_data)) < 1e-10
```
