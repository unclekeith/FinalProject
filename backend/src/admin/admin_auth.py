from typing import Optional

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        # Implement your authentication logic here
        # For example, check against a database of admin users
        return username == "admin" and password == "secure_password"

    async def logout(self, request: Request) -> bool:
        # Implement logout logic if needed
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if not await self.login(request):
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
