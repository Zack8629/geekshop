import authapp.views as authapp
from django.urls import path

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.login, name='login'),
    path('logout/', authapp.logout, name='logout'),
    path('user/registration/', authapp.registration, name='registration'),
    path('user/edit/', authapp.edit, name='edit'),
    path('user/verify/<str:email>/<str:activation_key>/', authapp.verify, name='verify'),
]
