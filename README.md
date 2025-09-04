> [!WARNING]
> This project is under heavy development. Many things are subject to change, and the API should not be considered stable.

# Nik

Nik is a fullstack Python web framework that allows developing single page web apps without Javascript or HTML.

<div align="center">
  <video src="https://github.com/user-attachments/assets/5ea4e6f5-a62a-4fcf-8dc5-9df78118d5aa" width="400" />
</div>

> _The app in the video is written only with Python and without a single line of JavaScript._

## Main Features

- File based routing.
- Reactivity and state management without JavaScript.
- Nested layouts.
- HTML via Python objects.
- Authentication, Authorisation and Session management.

## Installation

### With uv

```shell
uv add nikweb
```

### With pip

```shell
pip install nikweb
```

### ASGI server

You also need to install an ASGI server, such as uvicorn or daphne. We tested Nik mainly on uvicorn.

```shell
pip install uvicorn
```

## Example Nik app

In your projects root folder create the following files and folders.

```
.
├── app
│   └── routes
│       └── route.py
└── main.py
```

`app` is the folder where your web application related code goes into and `app/routes` is the folder where you define your routes.

By default Nik looks for `routes.py` modules inside the routes folder.

```python
# main.py

from nikweb.server.app import Nik

PROJECT_ROOT = os.path.dirname(__file__)

app = Nik(environment="development", project_root=PROJECT_ROOT)
```

Now create your view in your route.

```python
# app/routes/route.py

from nikweb.views.elements import Div


def view():
    return Div("Hello, world!")
```

and run it via uvicorn

```bash
uvicorn main:app --reload
```

And now you when you make a request to the root path, you will see something like this:

```bash
curl http://127.0.0.1:8000

<fragment id="v_Sq_72h">
  <div>Hello, world!</div>
  <script>
    window.__nik.run({ v_Sq_72h: null });
  </script>
</fragment>
```

## Documentation

We are working hard to create comprehensive documentation for Nik. Until then, you can have a look at the `tests` folder to have an idea of how some things work.

## Road Map to V1

> [!NOTE]  
> Nik is in early stage in its development and is not yet feature complete. Contributions and feedbacks are welcome!

- **Routing**

  - Support for async generator functions and streaming responses in routes.
  - Support for type casting dynamic parameters.
  - Support for explicit http method functions. eg: `def post(body: dict):` for post request handling.

- **HTTP Server**

  - Support for different form content types. eg: multipart/form-data
  - Full file upload support. (eg: base64 encoded string with json, and multipart)
  - Improve error handlers

- **Static Files**

  - None blocking file reads.
  - Streaming support for "bigger" files.
  - Response.file method.
  - File related response headers. eg: last-modified, content-disposition etc.
  - Custom assets folder setting.

- **Views**

  - Empty state (or fallback) for list components.

- **Authentication, Authorisation and Session**

  - SecureCookie key rotation support.
  - Support for JWT and other popular methods.
  - Support for "smarter" permissions values. eg: Classes instead of dictionaries for more granular control.

- **ASGI**

  - Lifespan support (WIP)
  - Websockets and streaming responses. eg: LLM chat completions.
  - Remaining ASGI request features like `root_path`

- **Client Side**

  - Full nested data structure support for reactivity.
  - Sort of GC/reference counting system for obsolete resources.

- **Cli Tool**

  - Running the server in different environments and configurations.
  - Inspection features like dumping available routes, their permissions (or lack thereof).

- **Documentation**
  - General documentation and guidelines.
  - Recipes for most common use cases and examples.

## Special Thanks

Thanks to the [Starlette](https://www.starlette.io/) and [Uvicorn](https://www.uvicorn.org/) teams for their excellent work on these projects, which inspired and helped shape Nik.
