from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Auth"])
class MyTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=["Auth"])
class MyTokenRefreshView(TokenRefreshView):
    pass
