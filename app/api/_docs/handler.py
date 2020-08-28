import json
from .._base.handler import BaseHandler


class SwaggerHomeHandler(BaseHandler):
    SWAGGED = False

    async def get(self):
        return await self.render('swagger.html', SWAGGER_SCHEMA=json.dumps(self.application.SWAGGER_SCHEMA))
