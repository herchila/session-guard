from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView

from session_guard.models import DeviceSession
from session_guard.services import revoke_session


class DemoLoginView(LoginView):
    template_name = "accounts/login.html"


class DemoLogoutView(LogoutView):
    next_page = "/login/"


@login_required
def sessions_list(request):
    sessions = (
        DeviceSession.objects.filter(user=request.user, is_active=True)
        .select_related("device")
        .order_by("-last_active")
    )
    return render(request, "accounts/sessions.html", {"sessions": sessions})


@login_required
def sessions_revoke(request, pk):
    ds = get_object_or_404(DeviceSession, pk=pk, user=request.user)
    if request.method == "POST":
        revoke_session(request.user, ds)
        return redirect("sessions_list")
    return render(request, "accounts/sessions_confirm_revoke.html", {"session": ds})
