from ninja import NinjaAPI
from user_auth.api import api_auth as auth_router


api = NinjaAPI(title='Mobile App Api', version='1.0.0',)

api.add_router('/auth/', auth_router)
