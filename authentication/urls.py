from .views import RegistrationView,UsernamevalidationView,EmailvalidationView, LoginView,VerificationView,LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/',RegistrationView.as_view(),name="register"),
    path('login/', LoginView.as_view(),name="login"),
    path('logout/', LogoutView.as_view(),name="logout"),
    path('validate-username',csrf_exempt(UsernamevalidationView.as_view()),name='validate-username'),
    path('validate-email',csrf_exempt(EmailvalidationView.as_view()),name='validate-email'),
    path('activate/<uidb64>/<token>/',VerificationView.as_view(),name="activate")
]

