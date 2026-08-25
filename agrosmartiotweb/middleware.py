from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import Resolver404, resolve


class LoginRequiredMiddleware:
    """Exige sesión iniciada para cualquier vista nueva o existente por defecto.

    Sólo quedan afuera las rutas listadas en settings.LOGIN_EXEMPT_URL_NAMES /
    LOGIN_EXEMPT_PATH_PREFIXES (login, recuperar contraseña, admin, estáticos,
    y los endpoints que llaman los sensores/dispositivos IoT). Así un enlace
    compartido a cualquier vista protegida redirige a login en vez de mostrarla.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info

            if path.startswith(settings.LOGIN_EXEMPT_PATH_PREFIXES):
                return self.get_response(request)

            try:
                match = resolve(path)
            except Resolver404:
                # URL inexistente: se deja pasar para que handler404 la maneje.
                return self.get_response(request)

            if match.url_name not in settings.LOGIN_EXEMPT_URL_NAMES:
                return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)

        return self.get_response(request)
