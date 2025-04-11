# generator/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse('admin:login')

    def __call__(self, request):
        path = request.path_info
        if path.startswith(self.login_url) or path.startswith('/admin/') or path.startswith('/static/'):
            return self.get_response(request)
        if not request.user.is_authenticated:
            return redirect(f"{self.login_url}?next={path}")
        return self.get_response(request)
