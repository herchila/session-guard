from django.contrib import admin
from django.urls import path

from demo.app_accounts.views import (
    DemoLoginView,
    DemoLogoutView,
    sessions_list,
    sessions_revoke,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", DemoLoginView.as_view(), name="login"),
    path("logout/", DemoLogoutView.as_view(), name="logout"),
    path("account/sessions/", sessions_list, name="sessions_list"),
    path(
        "account/sessions/<int:pk>/revoke/",
        sessions_revoke,
        name="sessions_revoke",
    ),
]
