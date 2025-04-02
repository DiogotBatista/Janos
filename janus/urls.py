
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from chaves.views import custom_login, view_index
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', view_index, name="index" ),
    path('janos_painel/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('janus/', include('chaves.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]

