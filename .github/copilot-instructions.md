# Copilot Instructions

This document provides guidance for AI coding agents to effectively contribute to the Nik framework.

## Project Overview

Nik is a full-stack Python web framework for building single-page applications (SPAs) without writing JavaScript. It uses a file-based routing system and allows developers to define HTML structures using Python objects. The backend is built on ASGI, making it compatible with servers like Uvicorn.

Key directories:

- `src/nik`: The core framework source code.
- `src/nik/server`: The ASGI server implementation, request/response handling, and routing.
- `src/nik/views`: Components for building UI, including HTML elements and reactivity.
- `docs/`: Project documentation.
- `tests/`: Unit and functional tests.

## Architecture

### File-Based Routing

Nik uses a file-based routing system. The framework scans the `app/routes` directory for `route.py` files. The path to a `route.py` file determines its URL.

- `app/routes/route.py` -> `/`
- `app/routes/todos/route.py` -> `/todos`
- `app/routes/todos/_id_/route.py` -> `/todos/:id` (dynamic segment)

A `view()` function within a `route.py` file is responsible for rendering the content for that route.

### UI as Python Objects

HTML is generated using Python classes from `nik.views.elements`. For example, `Div("Hello")` creates a `<div>Hello</div>` element.

### Layouts

Shared page structures are defined in `layout.py` files. A root layout is typically placed at `app/routes/layout.py`. Layouts are functions that accept a `children` argument, which is a reference to the nested view (either another layout or the route's view).

Example `app/routes/layout.py`:

```python
from nik.views.elements import Body, Children, Head, Html, Title

def layout(children: Children):
    return Html(
        Head(Title("My App")),
        Body(children)
    )
```

### Route Generation

In development and test environments, Nik automatically generates a `_routesgen.py` file in the `app` directory. This file contains all discovered route definitions. It is recommended to commit this file to version control.

## Development Workflow

### Setup

1.  Install dependencies using `uv`:
    ```bash
    uv install
    ```
2.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

### Documentation

The project uses `MkDocs` for generating documentation.

- **Source Files**: Documentation source files and assets are located in the `docs/` directory.
- **Development Server**: To run the documentation development server, use the following command:
  ```bash
  ./scripts/docs
  ```

### Testing

Tests are written using `pytest` and are located in the `tests/` directory. The test module structure mirrors the source module structure (e.g., `src/nik/somemodule.py` -> `tests/nik/test_somemodule.py`).

- To run all tests, use the provided script or `pytest`:
  ```bash
  ./scripts/test
  # or
  pytest
  ```
- To run a specific test file with arguments:
  ```bash
  pytest tests/server/test_app.py -k "some_test_name"
  ```

#### Test Dependencies

Key test dependencies are defined in `pyproject.toml` under `[dependency-groups.tests]`:

- `pytest`: The testing framework.
- `pytest-asyncio`: For testing asynchronous code.
- `httpx`: For making HTTP requests in functional tests.
- `pytest-cov`: For code coverage measurement.

#### Test Structure and Conventions

- **Function-based tests:** The project prefers simple, function-based tests (e.g., `def test_some_feature():`) over class-based ones.
- **Asynchronous tests:** Use `async def` for testing asynchronous features, which are run with `pytest-asyncio`.
- **Fixtures:** `pytest` fixtures are used extensively for setting up test data and application instances. Common fixtures are in `tests/conftest.py`.
- **Functional Tests:** Located in `tests/server/test_functional.py`, these tests use an `httpx.AsyncClient` to make real HTTP requests to the application.
- **Unit Tests:** Found in various files under `tests/`, these tests focus on individual components, often using `unittest.mock` and `monkeypatch`.
- **Parametrization:** `pytest.mark.parametrize` is used to efficiently test multiple scenarios with different inputs.

## Conventions

- **Type Hinting & Static Analysis**: The codebase uses type hints extensively and is statically checked with `pyright`. Ensure all new code is fully type-hinted. The configuration is in `pyproject.toml`.
- **Code Style & Linting**: Code is formatted and linted with `ruff`. Before committing, run `./scripts/lint` to check for issues. Ensure your changes adhere to the existing style. The configuration is in `pyproject.toml`.
- **Dependencies**: Project dependencies are managed in `pyproject.toml`. Use `uv` to add or update dependencies.
- **Asynchronous Code**: The core server and routing components are asynchronous. Use `async` and `await` where appropriate, especially for I/O operations.

### Quality Assurance

- **Run all tests**: After making changes, ensure that all existing tests pass by running the full test suite:
  ```bash
  ./scripts/test
  ```
- **Check for errors**: Ensure there are no type or lint errors by running:
  ```bash
  ./scripts/lint
  ```
