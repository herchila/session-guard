from django.http import HttpResponse
from django.urls import path


def dummy_sessions_view(request):
    return HttpResponse("OK /account/sessions/")


urlpatterns = [
    path("account/sessions/", dummy_sessions_view, name="sessions_list"),
]
