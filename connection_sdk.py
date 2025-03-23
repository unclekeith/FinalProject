import os

import httpx


async def fetch_openapi_schema(base_url: str):
    """Fetch the OpenAPI schema from the given base URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/openapi.json")
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()


def extract_routes_from_openapi(openapi_schema):
    """Extract routes from the OpenAPI schema."""
    routes = []
    paths = openapi_schema.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            operation_id = details.get("operationId", f"{method}_{path}").replace(
                "-", "_"
            )
            tags = details.get("tags", [])
            for tag in tags:  # Add a route for each tag
                routes.append(
                    {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation_id,
                        "tag": tag,
                        "requestBody": details.get(
                            "requestBody"
                        ),  # Add requestBody information
                    }
                )
    return routes


class ConnectionManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()  # Create a single client instance

    def make_request(self, path: str, method: str, **kwargs):
        """Make an HTTP request to the given path using the specified method."""
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def generate_methods(self, routes):
        """Generate methods for each route and save them to a file."""
        # Group routes by their tags
        grouped_routes = {}
        for route in routes:
            tag = route["tag"]
            if tag not in grouped_routes:
                grouped_routes[tag] = []
            grouped_routes[tag].append(route)

        method_definitions = []

        # Create method definitions for each group
        for tag, routes in grouped_routes.items():
            class_name = f"{tag.capitalize()}Routes"  # Create class name from tag
            method_definitions.append(f"class {class_name}:\n")
            method_definitions.append("    def __init__(self, client):\n")
            method_definitions.append(
                "        self.client = client\n\n"
            )  # Store client instance

            for route in routes:
                method_name = route["operation_id"]

                # Check for parameters in the path
                param_names = []
                path_segments = route["path"].strip("/").split("/")
                for segment in path_segments:
                    if segment.startswith("{") and segment.endswith("}"):
                        param_name = segment[1:-1]  # Extract parameter name
                        param_names.append(param_name)

                # Create method signature with parameters
                if param_names:
                    params_str = ", ".join(param_names)
                    method_definitions.append(
                        f"    def {method_name}(self, {params_str}, **kwargs):\n"
                    )
                else:
                    # No parameters in the path
                    method_definitions.append(
                        f"    def {method_name}(self, **kwargs):\n"
                    )

                # Add request body information to the docstring
                request_body = route.get("requestBody")
                if request_body:
                    media_types = request_body.get("content", {})
                    for media_type, content in media_types.items():
                        schema = content.get("schema", {})
                        method_definitions.append(
                            f"        '''\n        Expected data: {media_type}\n"
                        )
                        method_definitions.append(
                            f"        Schema: {schema}\n        '''\n"
                        )
                        break  # Only show the first media type

                # Add the request code with special logic for 'post_login' and 'logout'
                if method_name == "post_login":
                    # Special logic to save cookies after successful login
                    method_definitions.append(
                        f"        response = self.client.{route['method'].lower()}(f'{{server_url}}{route['path']}', follow_redirects=True, **kwargs)\n"
                        f"        if response.status_code == 200:  # Assuming 200 is a successful login\n"
                        f"            save_cookies(self.client.cookies)\n\n"
                        f"        return response\n\n"
                    )
                elif method_name == "post_logout":
                    # Special logic to clear cookies after successful logout
                    method_definitions.append(
                        f"        response = self.client.{route['method'].lower()}(f'{{server_url}}{route['path']}', follow_redirects=True, **kwargs)\n"
                        f"        if response.status_code == 200:  # Assuming 200 is a successful logout\n"
                        f"            save_cookies({{}})  # Clear the cookies\n\n"
                        f"        return response\n\n"
                    )
                else:
                    # Standard request code
                    method_definitions.append(
                        f"        response =  self.client.{route['method'].lower()}(f'{{server_url}}{route['path']}', follow_redirects=True, **kwargs)\n\n"
                        f"        return response\n\n"
                    )

            method_definitions.append(
                "\n"
            )  # Add a newline for separation between classes

        self.save_methods_to_file(method_definitions)

    def save_methods_to_file(self, method_definitions):
        """Save the generated methods to a file."""
        methods_file_path = os.path.join(
            os.path.dirname(__file__),
            "frontend/libs/applibs/generated_connection_manager.py",
        )
        with open(methods_file_path, "w") as file:
            file.write(
                """
import httpx
from kivy.utils import platform
from libs.applibs.utils import load_cookies, save_cookies  # noqa: F401

online_server_url = "https://embakweaziwe.onrender.com"
offline_server_url = "http://127.0.0.1:8000"

if platform == "android":
    server_url = online_server_url
else:
    server_url = offline_server_url

# Create a Client instance with cookies
def create_client():
    # create a client session (client = create_client()) to use for that session (app lifetime)
    cookies = load_cookies()
    return httpx.Client()


"""
            )
            for method in method_definitions:
                file.write(method)  # Directly write the method definition


# Example usage
async def setup_connection_manager():
    base_url = "http://localhost:8000"
    openapi_schema = await fetch_openapi_schema(base_url)
    routes = extract_routes_from_openapi(openapi_schema)

    connection_manager = ConnectionManager(base_url)
    connection_manager.generate_methods(routes)

    # Instantiate route classes and use the shared client
    # For example: user_routes = UserRoutes(connection_manager.client)


if __name__ == "__main__":
    import asyncio

    asyncio.run(setup_connection_manager())
