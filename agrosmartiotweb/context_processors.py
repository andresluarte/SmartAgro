from .models import EmpresaOFundo

from .models import CustomUser


def empresa_info(request):
    empresa = None
    if request.user.is_authenticated:
        empresa = request.user.empresa
    return {'empresa': empresa}