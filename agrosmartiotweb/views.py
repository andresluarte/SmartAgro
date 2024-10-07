from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from .models import Procesos ,Trabajador,Jornada,Sector,Huerto,Lote,JornadaPorTrato
from .forms import ContactoForm,ProcesoForm,ProcesoModificarForm,TrabajadorForm,FormatoForm,TrabajadorModificarForm,JornadaModificarForm,SectorModificarForm,HuertoModificarForm,LoteModificarForm
from django.contrib import messages
from .serializers import ProcesoSerializer
from rest_framework.generics import ListAPIView
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
#llamada de filtros
from .forms import FiltroEstado
from .filters import ProcesoFilter,TrabajadorFilter,JornadaFilter,JornadaPorTratoFilter
#List view
from django.views.generic.list import ListView
from django.views import View
#paginador 

from django.core.paginator import Paginator

#resource exportar excel
from .admin import ProcesosResource,JornadasResource,TrabajadorResource


from django.shortcuts import render
from .models import EmpresaOFundo

def home(request):
    empresa = None
    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        empresa = EmpresaOFundo.objects.filter(created_by=request.user).first()
    
    # Renderizar el template con la empresa en el contexto
    return render(request, 'agrosmart/home.html', {'empresa': empresa})




class ProcesoListView(ListView):
    queryset = Procesos.objects.all()
    form_class = FormatoForm
    template_name = 'agrosmart/gestiondetareas.html'
    context_object_name = 'procesos'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProcesoFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filterset.form
        return context
    
#exportar tarea (proceso)       
class ExportToExcelViewProceso(View):
    def get(self, request):
        queryset = ProcesoFilter(request.GET, queryset=Procesos.objects.all()).qs
        dataset = ProcesosResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="procesos.xls"'
        return response

    def post(self, request):
        queryset = ProcesoFilter(request.POST, queryset=Procesos.objects.all()).qs
        dataset = ProcesosResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="procesos.xls"'
        return response
    
#exportar excel jornada
class ExportToExcelViewJornada(View):
    def get(self, request):
        queryset = JornadaFilter(request.GET, queryset=Jornada.objects.all()).qs
        dataset = JornadasResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada.xls"'
        return response

    def post(self, request):
        queryset = JornadaFilter(request.POST, queryset=Jornada.objects.all()).qs
        dataset = JornadasResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada.xls"'
        return response

class ExportToExcelViewJornadaporTrato(View):
    def get(self, request):
        queryset = JornadaPorTratoFilter(request.GET, queryset=JornadaPorTrato.objects.all()).qs
        dataset = JornadasResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada.xls"'
        return response

    def post(self, request):
        queryset = JornadaPorTratoFilter(request.POST, queryset=JornadaPorTrato.objects.all()).qs
        dataset = JornadasResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada.xls"'
        return response


#exportar trabajador
class ExportToExcelViewTrabajador(View):
    def get(self, request):
        queryset = TrabajadorFilter(request.GET, queryset=Trabajador.objects.all()).qs
        dataset = TrabajadorResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="trabajador.xls"'
        return response

    def post(self, request):
        queryset = TrabajadorFilter(request.POST, queryset=Jornada.objects.all()).qs
        dataset = TrabajadorResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada.xls"'
        return response

    
class ProcesoListAPIView(ListAPIView):
    queryset = Procesos.objects.all()
    serializer_class = ProcesoSerializer


def ayuda(request):

    contacto = {
        'form' : ContactoForm()
    }

    return render(request, 'agrosmart/ayuda.html',contacto)

#Agregar tarea
@login_required
def agregartarea(request):
    if request.method == 'POST':
        formulario = ProcesoForm(data=request.POST, files=request.FILES, user=request.user)
        if formulario.is_valid():
            tarea = formulario.save(commit=False) 
            tarea.created_by = request.user  # Asignar el usuario logueado como creador
            tarea.user = request.user  # Asignar el usuario logueado al campo 'user'
            tarea.save()  # Guardar la tarea con el usuario asignado
            messages.success(request, "Tarea Registrada")
            return redirect('gestiondetareas')  # Redirige a la vista de gestión de tareas
        else:
            data = {'form': formulario}
    else:
        data = {'form': ProcesoForm(user=request.user)}
     
    return render(request, 'agrosmart/agregartarea.html', data)

#Modificar Tarea (proceso)
@login_required
def modificartarea(request, id):
    proceso = get_object_or_404(Procesos, id=id)
    data = {
        'form': ProcesoModificarForm(instance=proceso, user=request.user)
    }

    if request.method == 'POST':
        formulario = ProcesoModificarForm(data=request.POST, instance=proceso, files=request.FILES, user=request.user)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente")
            return redirect('gestiondetareas')  # Puedes redirigir a una vista después de modificar
        data["form"] = formulario

    return render(request, 'agrosmart/modificartarea.html', data)
#Modificar Trabajador
def modificartrabajadores(request,id):
    trabajadores = get_object_or_404(Trabajador,id=id)
    data ={
        'form' : TrabajadorModificarForm(instance=trabajadores)
    }

    if request.method == 'POST':
        formulario = TrabajadorModificarForm(data=request.POST,instance=trabajadores,files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,"Modificado Correctamente")
            
        data["form"] = formulario

    return render(request, 'agrosmart/trabajadores/modificartrabajadores.html',data)
#Eliminar tarea (proceso)
def eliminartarea(request, id):
    proceso = get_object_or_404(Procesos, id=id)
    proceso.delete()
    messages.success(request, "Eliminado Correctamente")
    return redirect('gestiondetareas')



#AGREGAR ZONA ESPECIFICA

#AGREGAR filtros
#AGREGAR TRABAJADOR 

@login_required(login_url="my_login")
def agregartrabajador(request):
    if request.method == "POST":
        form = TrabajadorForm(request.POST, request.FILES) 
        if form.is_valid():
            trabajador = form.save(commit=False)
            trabajador.created_by = request.user  # Asignar el usuario logueado al campo 'created_by'
            trabajador.user = request.user  # Asignar el usuario logueado al campo 'user'
            trabajador.save()
            return redirect('gestiondetrabajadores')  # Redirigir a la vista de gestión de trabajadores
    else:
        form = TrabajadorForm()

    return render(request, 'agrosmart/trabajadores/agregartrabajador.html', {'form': form})





class TrabajadorListView(ListView):
    queryset = Trabajador.objects.all()



    template_name = 'agrosmart/trabajadores/gestiondetrabajadores.html'
    context_object_name = 'trabajador'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset=TrabajadorFilter(self.request.GET,queryset=queryset)
        return self.filterset.qs
    def get_context_data(self, **kwargs):

        context= super().get_context_data(**kwargs)
        context['form']=self.filterset.form
        return context
    
@login_required(login_url="my_login")
def modificarjornada(request, id):
    jornada = get_object_or_404(Jornada, id=id)
    user = request.user

    if request.method == 'POST':
        formulario = JornadaModificarForm(data=request.POST, instance=jornada, files=request.FILES, user=user)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Jornada Modificada Correctamente")
            return redirect('gestion_jornadas')
    else:
        formulario = JornadaModificarForm(instance=jornada, user=user)

    data = {
        'form': formulario
    }

    return render(request, 'agrosmart/jornada/modificarjornada.html', data)

def cargar_lotes(request):
    huerto_id = request.GET.get('huerto_id')
    lotes = Lote.objects.filter(huerto_id=huerto_id).values('id', 'nombre')
    return JsonResponse(list(lotes), safe=False)

def eliminarjornada(request, id):
    jornada = get_object_or_404(Jornada, id=id)
    jornada.delete()
    messages.success(request, "Jornada Eliminada Correctamente")
    return redirect('gestion_jornadas')

def eliminarjornadaPorTrato(request, id):
    jornada = get_object_or_404(JornadaPorTrato, id=id)
    jornada.delete()
    messages.success(request, "Jornada Eliminada Correctamente")
    return redirect('gestion_jornadas_por_trato')

#exportar excel
def eliminartrabajador(request, id):
    proceso = get_object_or_404(Trabajador, id=id)
    proceso.delete()
    messages.success(request, "Trabajador Eliminado Correctamente")
    return redirect('gestiondetrabajadores')

##sensor
from django.views.decorators.csrf import csrf_exempt

#jornada
from django.shortcuts import render, redirect
from .forms import JornadaForm,JornadaPorTratoForm

@login_required(login_url="my_login")
def agregar_jornada(request):
    if request.method == 'POST':
        form = JornadaForm(request.POST, user=request.user)
        if form.is_valid():
            jornada = form.save(commit=False)
            jornada.user = request.user  # Asignar el usuario logueado al campo 'user'
            jornada.created_by = request.user  # Asignar el usuario logueado al campo 'created_by'
            jornada.save()  # Ahora sí guardar la jornada con el usuario asignado
            return redirect('gestion_jornadas')
    else:
        form = JornadaForm(user=request.user)
    
    return render(request, 'agrosmart/jornada/crear_jornada.html', {'form': form})

@login_required(login_url="my_login")
def agregar_jornada_por_trato(request):
    if request.method == 'POST':
        form = JornadaPorTratoForm(request.POST, user=request.user)
        if form.is_valid():
            jornada_por_trato = form.save(commit=False)
            jornada_por_trato.user = request.user  # Asignar el usuario logueado al campo 'user'
            jornada_por_trato.created_by = request.user  # Asignar el usuario logueado al campo 'created_by'
            jornada_por_trato.save()  # Guardar la jornada por trato con el usuario asignado
            return redirect('gestion_jornadas_por_trato')
    else:
        form = JornadaPorTratoForm(user=request.user)
    
    return render(request, 'agrosmart/jornada/crear_jornada_por_trato.html', {'form': form})


@login_required(login_url="my_login")
def JornadaList(request):
    user = request.user
    
    if user.is_superuser:
        queryset = Jornada.objects.all()
    elif user.user_type == 'admin':
        queryset = Jornada.objects.filter(user=user)
    elif user.user_type == 'colaborador':
        admin_user = user.created_by
        queryset = Jornada.objects.filter(user__in=[user, admin_user])
    elif user.user_type == 'agricultor':
        colaborador_user = user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        queryset = Jornada.objects.filter(user__in=[user, colaborador_user, admin_user])
    else:
        queryset = Jornada.objects.none()

    filtered_jornadas = JornadaFilter(request.GET, queryset=queryset, user=user)

    context = {'filtered_jornadas': filtered_jornadas}
    paginated_filtered_jornadas = Paginator(filtered_jornadas.qs, 3)
    page_number = request.GET.get('page')
    jornada_page_obj = paginated_filtered_jornadas.get_page(page_number)
    context['jornada_page_obj'] = jornada_page_obj

    return render(request, 'agrosmart/jornada/gestion_jornadas.html', context=context)

@login_required(login_url="my_login")
def jornada_por_trato_list(request):
    user = request.user

    # Filtramos las jornadas según el tipo de usuario
    if user.is_superuser:
        queryset = JornadaPorTrato.objects.all()
    elif user.user_type == 'admin':
        queryset = JornadaPorTrato.objects.filter(user=user)
    elif user.user_type == 'colaborador':
        admin_user = user.created_by
        queryset = JornadaPorTrato.objects.filter(user__in=[user, admin_user])
    elif user.user_type == 'agricultor':
        colaborador_user = user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        queryset = JornadaPorTrato.objects.filter(user__in=[user, colaborador_user, admin_user])
    else:
        queryset = JornadaPorTrato.objects.none()

    # Aquí puedes aplicar cualquier filtrado adicional relacionado con 'trato'
    filtered_jornadas = JornadaFilter(request.GET, queryset=queryset, user=user)

    # Configuramos la paginación
    paginated_filtered_jornadas = Paginator(filtered_jornadas.qs, 3)
    page_number = request.GET.get('page')
    jornada_page_obj = paginated_filtered_jornadas.get_page(page_number)

    # Pasamos el contexto a la plantilla
    context = {
        'filtered_jornadas': filtered_jornadas,
        'jornada_page_obj': jornada_page_obj,
    }

    return render(request, 'agrosmart/jornada/gestion_jornadas.html', context=context)



@login_required(login_url="my_login")
def TrabajadorList(request):
    if request.user.is_superuser:
        queryset = Trabajador.objects.all()
    elif request.user.user_type == 'admin':
        queryset = Trabajador.objects.filter(created_by=request.user)
    elif request.user.user_type == 'colaborador':
        # Colaborador puede ver sus propios trabajadores y los de su admin
        admin_user = request.user.created_by
        queryset = Trabajador.objects.filter(created_by__in=[request.user, admin_user])
    elif request.user.user_type == 'agricultor':
        # Agricultor puede ver los trabajadores creados por su colaborador y su administrador
        colaborador_user = request.user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        queryset = Trabajador.objects.filter(created_by__in=[colaborador_user, admin_user])
    else:
        queryset = Trabajador.objects.none()

    filtered_trabajador = TrabajadorFilter(request.GET, queryset=queryset)

    context = {
        'filtered_trabajador': filtered_trabajador,
    }

    paginated_filtered_trabajador = Paginator(filtered_trabajador.qs, 8)
    page_number = request.GET.get('page')
    trabajador_page_obj = paginated_filtered_trabajador.get_page(page_number)

    context['trabajador_page_obj'] = trabajador_page_obj

    return render(request, 'agrosmart/trabajadores/gestiondetrabajadores.html', context=context)
 
def ProcesoList(request):
    context = { }
    filtered_proceso = ProcesoFilter(
        request.GET,
        queryset=Procesos.objects.all()

    ) 
    context['filtered_proceso'] = filtered_proceso
    paginated_filtered_proceso = Paginator(filtered_proceso.qs,8)
    page_number = request.GET.get('page')
    proceso_page_obj = paginated_filtered_proceso.get_page(page_number)

    context['proceso_page_obj'] = proceso_page_obj
    
    return render(request, 'agrosmart/gestiondetareas.html', context=context)

from django.core.serializers import serialize
@login_required(login_url="my_login")
def gestion_zona(request):
    if request.user.is_superuser:
        sectores = Sector.objects.all()
    elif request.user.user_type == 'admin':
        sectores = Sector.objects.filter(user=request.user)
    elif request.user.user_type == 'colaborador':
        # Colaborador puede ver sus propias zonas y las del admin que lo creó
        admin_user = request.user.created_by
        sectores = Sector.objects.filter(user__in=[request.user, admin_user])
    elif request.user.user_type == 'agricultor':
        # Agricultor puede ver sus propias zonas y las del colaborador y admin que lo creó
        colaborador_user = request.user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        sectores = Sector.objects.filter(user__in=[request.user, colaborador_user, admin_user])
    else:
        sectores = Sector.objects.none()

    # Serializa los sectores a JSON para usarlos en el frontend
    sectores_json = serialize('json', sectores)

    # Asegúrate de pasar tanto 'sectores_json' como 'sectores' al contexto
    context = {
        'sectores_json': sectores_json,  # Envía el JSON serializado a la plantilla
        'sectores': sectores              # Envía la queryset de sectores a la plantilla
    }

    return render(request, "agrosmart/zona/gestion_zona.html", context)




from django.shortcuts import render, redirect
from .forms import SectorForm, HuertoForm, LoteForm

@login_required(login_url="my_login")
def agregar_sector(request):
    if request.method == "POST":
        form = SectorForm(request.POST)
        if form.is_valid():
            sector = form.save(commit=False)
            sector.user = request.user  # Asigna el usuario logueado (admin)
            sector.created_by = request.user
            sector.save()

            # Manejo de las acciones del formulario
            if request.POST.get('action') == 'add_and_redirect':
                return redirect('agregar_huerto', sector_id=sector.id)
            elif request.POST.get('action') == 'add_another':
                # Redirigir al mismo formulario para agregar otro sector
                return render(request, 'agrosmart/zona/crear_sectorPoligon.html', {'form': SectorForm(), 'mensaje': 'Sector agregado exitosamente, puedes agregar otro sector.'})
    else:
        form = SectorForm()
    
    return render(request, 'agrosmart/zona/crear_sectorPoligon.html', {'form': form})






@login_required(login_url="my_login")
def agregar_huerto_sin_sector(request):
    if request.method == 'POST':
        form = HuertoForm(request.POST, user=request.user)
        if form.is_valid():
            huerto = form.save(commit=False)
            huerto.user = request.user
            huerto.created_by = request.user
            huerto.save()
            return redirect('agregar_lote_sh')  # Redirige al agregar lote sin huerto
    else:
        form = HuertoForm(user=request.user)
    return render(request, 'agrosmart/zona/agregarhuerto.html', {'form': form})

@login_required(login_url="my_login")
def agregar_huerto(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id, user=request.user)
    
    if request.method == "POST":
        form = HuertoForm(request.POST, user=request.user)
        if form.is_valid():
            huerto = form.save(commit=False)
            huerto.sector = sector  # Asigna el sector al huerto
            huerto.user = request.user
            huerto.created_by = request.user
            huerto.save()
            return redirect('agregar_lote')  # Redirige al agregar lote con huerto
    else:
        form = HuertoForm(initial={'sector': sector}, user=request.user)
    
    return render(request, 'agrosmart/zona/agregarhuerto.html', {'form': form})


@login_required(login_url="my_login")
def agregar_lote(request, huerto_id=None):
    if huerto_id:
        huerto = get_object_or_404(Huerto, id=huerto_id, user=request.user)
    else:
        huerto = None

    if request.method == "POST":
        form = LoteForm(request.POST, user=request.user)
        if form.is_valid():
            lote = form.save(commit=False)
            if huerto:
                lote.huerto = huerto
            lote.user = request.user
            lote.created_by = request.user
            lote.save()
            return redirect('gestion_zona')
    else:
        form = LoteForm(user=request.user, initial={'huerto': huerto})

    return render(request, 'agrosmart/zona/agregarlote.html', {'form': form})

@login_required(login_url="my_login")
def agregar_lote_sin_huerto(request):
    if request.method == 'POST':
        form = LoteForm(request.POST, user=request.user)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.user = request.user
            lote.created_by = request.user
            lote.save()
            return redirect('gestion_zona')
    else:
        form = LoteForm(user=request.user)
    return render(request, 'agrosmart/zona/agregarlote.html', {'form': form})



@login_required(login_url="my_login")
def cargar_lotes(request):
    huerto_id = request.GET.get('huerto_id')
    lotes = Lote.objects.filter(huerto_id=huerto_id, user=request.user)
    lotes_data = [{'id': lote.id, 'nombre': lote.nombre} for lote in lotes]
    return JsonResponse({'lotes': lotes_data})

@login_required(login_url="my_login")
def cargar_huertos(request):
    sector_id = request.GET.get('sector_id')
    huertos = Huerto.objects.filter(sector_id=sector_id, user=request.user)
    huertos_data = [{'id': huerto.id, 'nombre': huerto.nombre} for huerto in huertos]
    return JsonResponse({'huertos': huertos_data})

@login_required(login_url="my_login")
def modificarsector(request, id):
    sector = get_object_or_404(Sector, id=id, user=request.user)
    form = SectorModificarForm(instance=sector)
    
    if request.method == 'POST':
        form = SectorModificarForm(data=request.POST, instance=sector, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Modificado Correctamente")
            return redirect("gestion_zona")

    return render(request, 'agrosmart/zona/modificarsector.html', {'form': form})

@login_required(login_url="my_login")
def modificarhuerto(request, id):
    huerto = get_object_or_404(Huerto, id=id, user=request.user)
    form = HuertoModificarForm(instance=huerto, user=request.user)
    
    if request.method == 'POST':
        form = HuertoModificarForm(data=request.POST, instance=huerto, files=request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Huerto Modificado Correctamente")
            return redirect("gestion_zona")

    return render(request, 'agrosmart/zona/modificarhuerto.html', {'form': form})

@login_required(login_url="my_login")
def modificarlote(request, id):
    lote = get_object_or_404(Lote, id=id, user=request.user)
    form = LoteModificarForm(instance=lote, user=request.user)
    
    if request.method == 'POST':
        form = LoteModificarForm(data=request.POST, instance=lote, files=request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lote Modificado Correctamente")
            return redirect("gestion_zona")

    return render(request, 'agrosmart/zona/modificarlote.html', {'form': form})









def eliminarsector(request, id):
    sector = get_object_or_404(Sector, id=id)
    sector.delete()
    messages.success(request, "Sector Eliminado Correctamente")
    return redirect('gestion_zona')

def eliminarhuerto(request, id):
    huerto = get_object_or_404(Huerto, id=id)
    huerto.delete()
    messages.success(request, "Sector Eliminado Correctamente")
    return redirect ('gestion_zona')
    


# def eliminartarea(request, id):
#     proceso = get_object_or_404(Procesos, id=id)
#     proceso.delete()
#     messages.success(request, "Eliminado Correctamente")
#     return redirect('gestiondetareas')
# en views.py







def obtener_cobro_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        trabajador_id = request.GET.get('trabajador_id')
        try:
            trabajador = Trabajador.objects.get(id=trabajador_id)
            cobro = trabajador.cobro
            data = {'cobro': cobro}
            return JsonResponse(data)
        except Trabajador.DoesNotExist:
            return JsonResponse({'error': 'Trabajador no encontrado'})
    else:
        return JsonResponse({'error': 'No es una solicitud AJAX'})
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#authentication 
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm    
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login,logout
from . forms import LoginForm
from .forms import CreateUserForm, RegisterColaboradorForm
from .models import CustomUser

@login_required(login_url="my_login")
@user_passes_test(lambda u: u.is_superuser)
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'admin'  # Asignar tipo 'admin'
            user.save()
            return redirect('list_all_users')
    context = {'registerform': form}
    return render(request, 'agrosmart/registration/register.html', context=context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterColaboradorForm, TrabajadorForm

@login_required(login_url="my_login")
@user_passes_test(lambda u: u.user_type in ['superuser', 'admin'])
def register_colaborador(request):
    if request.method == 'POST':
        form_colaborador = RegisterColaboradorForm(request.POST, user=request.user)
        # Solo inicializamos el formulario de trabajador si el checkbox fue marcado
        form_trabajador = TrabajadorForm(request.POST) if 'agregar_trabajador' in request.POST else None

        if form_colaborador.is_valid() and (not form_trabajador or form_trabajador.is_valid()):
            colaborador = form_colaborador.save(commit=False)
            colaborador.created_by = request.user
            colaborador.save()
            return redirect('list_colaboradores')

            # Si el usuario ha seleccionado agregar como trabajador
            if form_trabajador:
                trabajador = form_trabajador.save(commit=False)
                trabajador.user = request.user
                trabajador.save()

            

    else:
        form_colaborador = RegisterColaboradorForm(user=request.user)
        form_trabajador = TrabajadorForm()

    context = {
        'registerform': form_colaborador,
        'trabajadorform': form_trabajador,
    }
    return render(request, 'agrosmart/registration/register_colaborador.html', context)







from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import EditColaboradorForm
from .models import CustomUser
@login_required(login_url="my_login")
@user_passes_test(lambda u: u.user_type == 'admin')
def edit_colaborador_view(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = EditColaboradorForm(request.POST, instance=user_to_edit, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Colaborador editado correctamente.")
            return redirect('list_colaboradores')
            
    else:
        form = EditColaboradorForm(instance=user_to_edit, user=request.user)

    return render(request, 'agrosmart/usuarios/modificar_colaborador.html', {'form': form})



@login_required(login_url="my_login")
@user_passes_test(lambda u: u.user_type == 'superuser')
def list_all_users(request):
    users = CustomUser.objects.all()
    context = {'users': users}
    return render(request, 'agrosmart/usuarios/user_list.html', context=context)

@login_required(login_url="my_login")
@user_passes_test(lambda u: u.user_type == 'admin')
def list_colaboradores(request):
    users = CustomUser.objects.filter(created_by=request.user)
    context = {'users': users}
    return render(request, 'agrosmart/usuarios/user_list.html', context=context)

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm  # Usa el formulario estándar
from django.contrib.auth.decorators import login_required

def my_login(request):
    form = AuthenticationForm()  # Inicializa el formulario aquí
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("home")  # Asegúrate de tener una vista con nombre 'home'
    context = {"form": form}
    return render(request, 'agrosmart/registration/my-login.html', context=context)



def user_logout(request):
    auth.logout(request)
    return redirect ("home")

@user_passes_test(lambda u: u.user_type in ['superuser', 'admin'])
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    if request.user == user_to_delete:
        messages.error(request, "No puedes eliminar tu propio perfil.")
    else:
        user_to_delete.delete()
        messages.success(request, "Colaborador eliminado correctamente.")

        # Redirección basada en el tipo de usuario
        if request.user.user_type == 'admin':
            return redirect('list_colaboradores')
        elif request.user.is_superuser:
            return redirect('list_all_users')

    return redirect('list_colaboradores')  # En c



 
#crear empresa
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .forms import EmpresaOFundoForm,EditColaboradorForm
from .models import EmpresaOFundo

# Decorador para verificar si el usuario es un administrador
def is_admin(user):
    return user.user_type == 'admin'

@user_passes_test(is_admin)
def agregar_empresa(request):
     
    if EmpresaOFundo.objects.filter(created_by=request.user).exists():
        messages.error(request, "Ya tienes una empresa registrada.")
        return redirect('lista_empresas')  # Redirige a la list


    if request.method == 'POST':
        form = EmpresaOFundoForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.user = request.user
            empresa.created_by = request.user  # El administrador que crea la empresa
            empresa.save()
            messages.success(request, "Empresa registrada con éxito.")
            return redirect('lista_empresas')  # Redirigir a una página que muestre las empresas
    else:
        form = EmpresaOFundoForm()
    
    return render(request, 'agrosmart/empresa/agregar_empresa.html', {'form': form})

from django.shortcuts import render
from .models import EmpresaOFundo

@login_required
def lista_empresas(request):
    empresas = EmpresaOFundo.objects.none()  # Iniciar como vacía

    if request.user.user_type == 'admin':
        # Asegurarte de que el usuario 'admin' tiene empresas
        empresas = EmpresaOFundo.objects.filter(created_by=request.user)

    return render(request, 'agrosmart/empresa/lista_empresas.html', {'empresas': empresas})



#DATOS DE SENSOR 

from .models import TemperatureHumidityLocation
from .models import HumiditySoil
@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        # Procesar los datos aquí
        data = request.POST
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        latitude=data.get('latitude')
        longitude=data.get('longitude')
        

        # Guardar los datos en la base de datos
        # Suponiendo que tienes un modelo TemperatureHumidity para almacenar estos datos
        from .models import TemperatureHumidityLocation
        TemperatureHumidityLocation.objects.create(
            temperature=temperature,
            humidity=humidity,
            latitude=latitude,
            longitude=longitude

            
        )

        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)
    
#DATOS SENSOR SUELO

@csrf_exempt
def receive_data_soil(request):
    if request.method == 'POST':
        # Procesar los datos aquí
        data = request.POST
        humiditysoil = data.get('humiditysoil')

        if humiditysoil:
            HumiditySoil.objects.create(
                humiditysoil=humiditysoil,
            )
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"message": "Missing data"}, status=400)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)




from .serializers import TemperatureHumidityLocationSerializer
class TemperatureHumidityAPIView(APIView):
    def post(self, request, format=None):
        serializer = TemperatureHumidityLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
def combined_data_view(request):
    # Obtener la última entrada
    latest_data = TemperatureHumidityLocation.objects.last()
    return render(request, 'agrosmart/tiemporeal.html', {'latest_data': latest_data})

def combined_data_view_soil(request):
    latest_data = HumiditySoil.objects.last()
    return render(request, 'agrosmart/tiemporealsoil.html', {'latest_data': latest_data})


#INFORMES DE DATOS 1
from django.db.models import Avg, DateTimeField
from django.db.models.functions import TruncHour
from django.shortcuts import render
from django.db.models import Count, FloatField, Value
from django.db.models.functions import TruncHour, Cast
import json

def informes(request):
    # Promedio por hora para TemperatureHumidityLocation
    temp_humidity_data = (
        TemperatureHumidityLocation.objects
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(
            avg_temp=Avg('temperature'),
            avg_humidity=Avg('humidity')
        )
        .order_by('hour')
    )
    
    # Promedio por hora para HumiditySoil
    soil_data = (
        HumiditySoil.objects
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(avg_humidity_soil=Avg('humiditysoil'))
        .order_by('hour')
    )

    # Redondear los valores
    temp_humidity_data = [
        {
            'hour': entry['hour'].strftime('%Y-%m-%d %H:%M:%S'),
            'avg_temp': round(entry['avg_temp'], 2),
            'avg_humidity': round(entry['avg_humidity'], 2),
        } for entry in temp_humidity_data
    ]
    
    soil_data = [
        {
            'hour': entry['hour'].strftime('%Y-%m-%d %H:%M:%S'),
            'avg_humidity_soil': round(entry['avg_humidity_soil'], 2),
        } for entry in soil_data
    ]

    context = {
        'temp_humidity_data': json.dumps(temp_humidity_data),
        'soil_data': json.dumps(soil_data),
    }
    
    return render(request, 'agrosmart/informes.html', context)



from django.shortcuts import render, redirect
from .forms import SectorPoligonForm
@login_required(login_url="my_login")
def crear_sectorPoligon(request):
    if request.method == 'POST':
        form = SectorPoligonForm(request.POST)
        if form.is_valid():
            sector = form.save(commit=False)
            sector.user = request.user
            sector.created_by = request.user  # Asignamos el usuario actual como creador
            sector.save()
            return redirect('gestion_zonaPoligon')  # Redirigir a la lista de sectores o cualquier otra vista
    else:
        form = SectorPoligonForm()
    return render(request, "agrosmart/zona/crear_sectorPoligon.html", {'form': form})




from .models import SectorPoligon
from django.core.serializers import serialize
@login_required(login_url="my_login")
def gestion_zonaPoligon(request):
    if request.user.is_superuser:
        sectores = SectorPoligon.objects.all()
    elif request.user.user_type == 'admin':
        sectores = SectorPoligon.objects.filter(user=request.user)
    elif request.user.user_type == 'colaborador':
        # Colaborador puede ver sus propias zonas y las del admin que lo creó
        admin_user = request.user.created_by
        sectores = SectorPoligon.objects.filter(user__in=[request.user, admin_user])
    elif request.user.user_type == 'agricultor':
        # Agricultor puede ver sus propias zonas y las del colaborador y admin que lo creó
        colaborador_user = request.user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        sectores = SectorPoligon.objects.filter(user__in=[request.user, colaborador_user, admin_user])
    else:
        sectores = SectorPoligon.objects.none()
    sectores_json = serialize('json', sectores)
    context = {
        'sectores_json': sectores_json,  # Envía el JSON serializado a la plantilla
    }

    return render(request, "agrosmart/zona/gestion_zonaPoligon.html", context)
    


from .models import FinanzasPorTrabajador

def gestion_finanzas(request):
    finanzas = FinanzasPorTrabajador.objects.all()
    return render(request, 'agrosmart/finanzas/gestion_finanzas.html', {'finanzas': finanzas})