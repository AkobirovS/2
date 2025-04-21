from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterPhoneView, CustomTokenObtainPairView, DashboardView, LoginWithCodeView,AssignClassToStudentsView

urlpatterns = [
    path('register/', RegisterPhoneView.as_view()),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardView.as_view()),
    path('login/', LoginWithCodeView.as_view(), name='login'),
    path('teacher/assign-class/', AssignClassToStudentsView.as_view(), name='assign_class'),
]
