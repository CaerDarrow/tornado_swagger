from .._base.handler import BaseHandler, Swagger
from .._base.model import BaseResponse
from model import UserModel
from uuid import UUID
from pydantic import ValidationError


class TestHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET', 'POST')
    SWAGGED = True

    @Swagger(
        query=('filter', 'idk'),
        responses=(
            BaseResponse(status_code=200, reason='user_found', data=UserModel),
            BaseResponse(status_code=422, reason='validation error'),
            BaseHandler.ERROR_RESPONSE
        )
    )
    async def get(self, user_id: UUID):
        """
        summary: Получение информации о пользователе по id
        description: тест
        """
        try:
            user = dict(
                name='samuel colvin',
                username='scolvin',
                password1='zxcvbn',
                password2='zxcvbn',
            )
            user = UserModel(**user)
            return self.finish_with_ok(BaseResponse(status_code=200, reason='user_found', data=user.json()))
        except ValidationError as e:
            return self.finish_with_error(BaseResponse(status_code=422, reason='validation error'))

    @Swagger(
        body=UserModel,
        responses=(
            BaseResponse(status_code=200, reason='user_created', data=UserModel),
        )
    )
    async def post(self, user_id=None):
        """
        summary: Создать пользователя
        description: тест
        """
        user = self.get_body(UserModel)
        try:
            user = UserModel(**user)
        except ValidationError as e:
            return self.finish_with_error()
        try:
            user_id = await self.application.db.users.create(user)
        except Exception as e:  # DatabaseException
            return self.finish_with_error()
        return self.finish_with_ok(BaseResponse(status_code=200, reason='user_created', data=user_id))


