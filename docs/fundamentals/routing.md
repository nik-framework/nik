Nik uses a file-based routing system. This means the structure of your files and directories inside `app/routes` determines the URL structure of your application.

## Defining Routes

Routes are defined by creating `route.py` files within the `app/routes` directory. The path to the `route.py` file maps directly to the URL path.

During application startup, Nik scans the `app/routes` directory and generates a `_routesgen.py` file in your `app` folder. This file contains the compiled route configurations. It is recommended to commit this file to your version control system.

- A file at `app/routes/route.py` corresponds to the `/` path.
- A file at `app/routes/dashboard/settings/route.py` corresponds to the `/dashboard/settings` path.

### Dynamic Segments

To create routes with dynamic segments, create a directory with a name wrapped in underscores. For example, to create a route like `/todos/:id`, where `id` is a dynamic parameter, your directory structure should be:

```
app/routes/todos/_id_/route.py
```

Nik will capture the value from the URL at that position and make it available as the `id` parameter to your route functions.

## Route Functions

Each `route.py` module must export at least one route function: `view` or `action`. These functions handle requests and are central to Nik's SPA navigation and reactivity features.

### `view()`

The `view` function handles `GET` requests for a route. It is responsible for rendering the user interface.

```python
# app/routes/about/route.py
def view():
    return Div("This is the about page.")
```

### `action()`

The `action` function handles data mutations, typically from form submissions. It processes `POST`, `PUT`, `PATCH`, or `DELETE` requests.

```python
# app/routes/todos/route.py
def action(body: dict):
    print(f"Creating a new todo with data: {body}")
    # ... logic to create a new todo ...
```

### `partial()`

The `partial` function allows you to update a specific portion of a page instead of reloading the entire view. This is useful for features like dynamically loading tab content, paginating table data, or implementing search filters.

A `partial` function must be used in conjunction with a `view` function. The `view` function defines the overall page structure, and the `children` argument marks the placeholder where the content from `partial` will be rendered.

```python
# app/routes/products/route.py
def partial():
    # This function can fetch and return just the table data
    return Table(
        # ... Table data for the current page ...
    )

def view(children):
    # The view provides the surrounding page layout
    return Div(
        H1("Products"),
        children,  # The content from partial() is rendered here
        Div("Pagination controls")
    )
```

On the client-side, you can use Nik's partial loading functionality to invoke the `partial` function and replace only the content within the layout, enabling efficient and dynamic page updates.

For more details, see the _View System_ and _Partial Loading_ documentation.

## Accessing Request Data

Nik can inject request data and other useful objects into your route functions by defining them as parameters.

### Dynamic Route Segments

If a route contains dynamic segments (e.g., `_id_`), you can access their values by adding a parameter with the same name to your route function.

For a route at `app/routes/meetings/_meeting_id_/participants/_participant_id_/route.py`:

```python
def view(meeting_id: str, participant_id: str):
    print(f"Meeting ID: {meeting_id}")
    print(f"Participant ID: {participant_id}")
```

### `query`

The `query` parameter is a dictionary containing the URL's query string parameters. It supports both single and multiple values for the same key.

For a URL like `/search?name=nik&tags=spa&tags=web`, the `query` object will be:

```python
{
    "name": "nik",
    "tags": ["spa", "web"]
}
```

It can be passed to `view`, `action`, or `partial` functions.

### `body`

The `body` parameter contains the parsed request body from a form submission or API call. It is available only in `action` functions.

```python
def action(body: dict):
    # ... process form data ...
```

### `cookies`

The `cookies` parameter provides access to a `Cookies` object. You can use it to read cookies from the request and set cookies on the response.

See the _Cookies_ documentation for more information.

### `session`

If you have configured authentication, the `session` parameter provides a `Session` object. This gives you access to session data, such as the user's ID and roles.

See the _Authentication and Authorization_ documentation for more information.

### `page`

The `page` parameter is an object that holds metadata for the current page, such as the title or loading state. You can use it to communicate information between your route functions and the page's head or other components.

See the _Page_ documentation for more information.

### `children`

The `children` parameter is used in layout components and `view` functions that wrap a `partial`. It represents the rendered output of a child route or a `partial` function. Nik renders views from the inside out, allowing you to create nested layouts.

For more information, see the _View System_ documentation.
