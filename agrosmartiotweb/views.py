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
            return redirect('gestiondetareas')  # Redirigir a la vista deseada
        data["form"] = formulario  # Volver a mostrar el formulario con errores

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
from django.core.paginator import Paginator
from .models import Procesos

@login_required(login_url="my_login")
def ProcesoList(request):
    user = request.user
    
    # Filtrado según el tipo de usuario
    if user.is_superuser:
        queryset = Procesos.objects.all()
    elif user.user_type == 'admin':
        queryset = Procesos.objects.filter(user=user)
    elif user.user_type == 'colaborador':
        admin_user = user.created_by
        queryset = Procesos.objects.filter(user__in=[user, admin_user])
    elif user.user_type == 'agricultor':
        colaborador_user = user.created_by
        admin_user = colaborador_user.created_by if colaborador_user else None
        queryset = Procesos.objects.filter(user__in=[user, colaborador_user, admin_user])
    else:
        queryset = Procesos.objects.none()

    # Aplicando el filtro de búsqueda
    filtered_proceso = ProcesoFilter(request.GET, queryset=queryset, user=user)

    # Paginación
    context = {'filtered_proceso': filtered_proceso}
    paginated_filtered_proceso = Paginator(filtered_proceso.qs, 8)  # Número de elementos por página
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
    sectores_json = []  # Inicializa la lista de sectores

    if request.method == "POST":
        form = SectorForm(request.POST)
        if form.is_valid():
            sector = form.save(commit=False)
            sector.user = request.user  # Asigna el usuario logueado (admin)
            sector.created_by = request.user
            sector.save()

            # Almacena las coordenadas del sector creado
            sectores_json.append({'fields': {'nombre': sector.nombre, 'coordenadas': sector.coordenadas}})

            return render(request, 'agrosmart/zona/crear_sectorPoligon.html', {
                'form': SectorForm(),
                'mensaje': 'Sector agregado exitosamente.',
                'sectores_json': sectores_json,  # Pasa las coordenadas del nuevo sector
                'coordenadas': sector.coordenadas,  # Pasa las coordenadas del nuevo sector para centrar el mapa
            })
    else:
        form = SectorForm()

    # Carga los sectores existentes si no se está agregando uno nuevo
    sectores = Sector.objects.filter(user=request.user)  # Filtrar por usuario
    if sectores.exists():
        sectores_json = [{'fields': {'nombre': sector.nombre, 'coordenadas': sector.coordenadas}} for sector in sectores]
        # Tomar la primera coordenada para centrar el mapa en el primer sector
        coordenadas = sectores[0].coordenadas
    else:
        coordenadas = None  # No hay sectores, el mapa debe centrar en la ubicación actual

    return render(request, 'agrosmart/zona/crear_sectorPoligon.html', {
        'form': form,
        'sectores_json': sectores_json,  # Pasa los sectores existentes
        'coordenadas': coordenadas,  # Pasa coordenadas para centrar
    })











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
from .models import HumidityTemperaturaSoil,SensorAire,SensorSuelo
@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        # Obtener la API Key desde la cabecera 'Authorization'
        api_key = request.headers.get('Authorization')
        
        if not api_key:
            return JsonResponse({'status': 'error', 'message': 'API Key no proporcionada'}, status=400)

        # Verificar que la API Key sea válida
        sensor = SensorAire.objects.filter(api_key=api_key).first()
        if not sensor:
            return JsonResponse({'status': 'error', 'message': 'API Key inválida'}, status=403)

        # Obtener los datos enviados en la solicitud
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Verificar que los datos obligatorios estén presentes
        if not all([temperature, humidity, latitude, longitude]):
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)

        # Crear una nueva entrada de datos asociada al sensor
        TemperatureHumidityLocation.objects.create(
            temperature=temperature,
            humidity=humidity,
            latitude=latitude,
            longitude=longitude,
            sensor=sensor  # Asociar los datos al sensor encontrado por la API Key
        )

        return JsonResponse({'status': 'success', 'message': 'Datos recibidos correctamente'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    
#DATOS SENSOR SUELO

@csrf_exempt

def receive_data_soil(request):
    if request.method == 'POST':
        # Obtener la API Key desde la cabecera 'Authorization'
        api_key = request.headers.get('Authorization')
        
        if not api_key:
            return JsonResponse({'status': 'error', 'message': 'API Key no proporcionada'}, status=400)

        # Verificar que la API Key sea válida
        sensor = SensorSuelo.objects.filter(api_key=api_key).first()
        if not sensor:
            return JsonResponse({'status': 'error', 'message': 'API Key inválida'}, status=403)

        # Obtener los datos enviados en la solicitud
        humiditysoil = request.POST.get('humiditysoil')
        temperature = request.POST.get('temperature')

        # Verificar que los datos obligatorios estén presentes
        if not all([humiditysoil, temperature]):
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)

        # Crear una nueva entrada de datos asociada al sensor
        HumidityTemperaturaSoil.objects.create(
            humiditysoil=humiditysoil,
            temperature=temperature,
            sensor=sensor  # Asociar los datos al sensor encontrado por la API Key
        )

        return JsonResponse({'status': 'success', 'message': 'Datos de humedad del suelo recibidos correctamente'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)




from .serializers import TemperatureHumidityLocationSerializer
class TemperatureHumidityAPIView(APIView):
    def post(self, request, format=None):
        serializer = TemperatureHumidityLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
from django.shortcuts import render
from .models import TemperatureHumidityLocation, SensorAire

@login_required
def combined_data_view(request):
    # Obtener el usuario actual
    user = request.user

    # Obtener todos los sensores asociados al usuario
    sensors = SensorAire.objects.filter(user=user)

    # Comprobar si el usuario tiene sensores
    if not sensors.exists():
        return render(request, 'agrosmart/tiemporeal.html', {
            'sensor_data': [],
            'no_sensors_message': "No tienes sensores registrados.",
        })

    # Crear una lista para almacenar los datos de cada sensor y sus recomendaciones
    sensor_data = []

    for sensor in sensors:
        # Obtener la última entrada de datos para el sensor
        latest_data = TemperatureHumidityLocation.objects.filter(sensor=sensor).order_by('-timestamp').first()

        if latest_data:
            temperature = float(latest_data.temperature)
            humidity = float(latest_data.humidity)

            # Generar recomendaciones
            temperature_recommendation = ""
            humidity_recommendation = ""

            if temperature < 0:
                temperature_recommendation = "La temperatura es muy baja. Protege tus plantas del frío extremo."
            elif 0 <= temperature <= 10:
                temperature_recommendation = "La temperatura es fresca. Considera proteger las plantas del frío."
            elif 10 < temperature <= 25:
                temperature_recommendation = "La temperatura es óptima para las plantas de uva."
            elif temperature > 25:
                temperature_recommendation = "La temperatura es alta. Asegúrate de que las plantas tengan suficiente agua."

            if humidity < 40:
                humidity_recommendation = "El aire está seco. Es recomendable aumentar la humedad para las plantas."
            elif 40 <= humidity <= 70:
                humidity_recommendation = "La humedad es adecuada para el crecimiento de las plantas de uva."
            elif humidity > 70:
                humidity_recommendation = "La humedad es alta. Podría haber riesgo de enfermedades fúngicas."

            # Agregar datos a la lista
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': latest_data,
                'temperature_recommendation': temperature_recommendation,
                'humidity_recommendation': humidity_recommendation
            })
        else:
            # Si no hay datos, agregar el sensor con un mensaje de falta de datos
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': None,
                'temperature_recommendation': "No hay datos disponibles.",
                'humidity_recommendation': "No hay datos disponibles."
            })

    return render(request, 'agrosmart/tiemporeal.html', {
        'sensor_data': sensor_data,
    })


@login_required
def combined_data_view_soil(request):
    # Obtener el usuario actual
    user = request.user

    # Obtener todos los sensores de suelo asociados al usuario
    sensors = SensorSuelo.objects.filter(user=user)

    # Comprobar si el usuario tiene sensores
    if not sensors.exists():
        return render(request, 'agrosmart/tiemporealsoil.html', {
            'sensor_data': [],
            'no_sensors_message': "No tienes sensores de suelo registrados.",
        })

    # Crear una lista para almacenar los datos de cada sensor y sus recomendaciones
    sensor_data = []

    for sensor in sensors:
        # Obtener la última entrada de datos para el sensor
        latest_data = HumidityTemperaturaSoil.objects.filter(sensor=sensor).order_by('-timestamp').first()

        if latest_data:
            soil_temperature = float(latest_data.temperature)
            soil_humidity = float(latest_data.humiditysoil)

            # Generar recomendaciones
            soil_temperature_recommendation = ""
            soil_humidity_recommendation = ""

            # Recomendaciones basadas en la temperatura del suelo
            if soil_temperature < 10:
                soil_temperature_recommendation = "La temperatura del suelo es baja. Considera el uso de coberturas para retener el calor."
            elif 10 <= soil_temperature <= 20:
                soil_temperature_recommendation = "La temperatura del suelo es óptima para la mayoría de cultivos."
            elif soil_temperature > 20:
                soil_temperature_recommendation = "La temperatura del suelo es alta. Asegúrate de que haya suficiente humedad para evitar estrés en las plantas."

            # Recomendaciones basadas en la humedad del suelo
            if soil_humidity < 30:
                soil_humidity_recommendation = "El suelo está muy seco. Es necesario regar para mantener la salud de las plantas."
            elif 30 <= soil_humidity <= 60:
                soil_humidity_recommendation = "La humedad del suelo es adecuada para el crecimiento saludable de las plantas."
            elif soil_humidity > 60:
                soil_humidity_recommendation = "La humedad del suelo es alta. Asegúrate de tener buen drenaje para evitar encharcamientos."

            # Agregar datos a la lista
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': latest_data,
                'soil_temperature_recommendation': soil_temperature_recommendation,
                'soil_humidity_recommendation': soil_humidity_recommendation
            })
        else:
            # Si no hay datos, agregar el sensor con un mensaje de falta de datos
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': None,
                'soil_temperature_recommendation': "No hay datos disponibles.",
                'soil_humidity_recommendation': "No hay datos disponibles."
            })

    return render(request, 'agrosmart/tiemporealsoil.html', {
        'sensor_data': sensor_data,
    })


#INFORMES DE DATOS 1
from django.db.models import Avg, DateTimeField
from django.db.models.functions import TruncHour
from django.shortcuts import render
from django.db.models import Count, FloatField, Value
from django.db.models.functions import TruncHour, Cast
from django.db.models.functions import TruncMinute
from django.utils import timezone
from datetime import timedelta

import json

def informes(request):
    # Obtener sensores asociados al usuario autenticado
    user_sensors_air = SensorAire.objects.filter(user=request.user)
    user_sensors_soil = SensorSuelo.objects.filter(user=request.user)

    # Promedio por hora para TemperatureHumidityLocation (sensores de aire)
    temp_humidity_data = (
        TemperatureHumidityLocation.objects
        .filter(sensor__in=user_sensors_air)  # Filtrar solo los datos de los sensores del usuario
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(
            avg_temp=Avg('temperature'),
            avg_humidity=Avg('humidity')
        )
        .order_by('hour')
    )

    last_hour_data_air=(
        TemperatureHumidityLocation.objects
        .filter(sensor__in=user_sensors_air, timestamp__gte=timezone.now()-timedelta(hours=1))
        .annotate(minute=TruncMinute('timestamp'))
        .values('minute')
        .annotate(
            avg_temp_hour=Avg('temperature'),
            avg_humidity_hour=Avg('humidity')
        )
        .order_by('minute')

    )

    # Promedio por hora para HumidityTemperaturaSoil (sensores de suelo)
    soil_data = (
        HumidityTemperaturaSoil.objects
        .filter(sensor__in=user_sensors_soil)
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(
            avg_humidity_soil=Avg('humiditysoil'),
            avg_temp=Avg('temperature')
        )
        .order_by('hour')
    )

    # Redondear los valores de los datos
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
            'avg_temp': round(entry['avg_temp'], 2),
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
    


from .models import FinanzasPorTrabajador, FinanzasPorInsumosyMaquinaria,FinanzasPorMes
from django.db.models import Sum
@login_required
def gestion_finanzas(request):
    user = request.user
    
    # Filtrar las finanzas relacionadas con el usuario autenticado
    finanzas = FinanzasPorTrabajador.objects.filter(
        trabajador__user=user  # Si hay una relación entre Trabajador y Usuario
    )
    
    finanzas_por_mes = FinanzasPorMes.objects.filter(
        user=user
    )
    
    # Filtrar FinanzasPorInsumosyMaquinaria por el usuario autenticado
    finanzas_insumos = FinanzasPorInsumosyMaquinaria.objects.filter(
        user=user
    ).values('trabajo__trabajo__opciones_trabajo').annotate(
        total_gasto=Sum('gasto_total')
    )

    return render(request, 'agrosmart/finanzas/gestion_finanzas.html', {
        'finanzas': finanzas,
        'finanzas_insumos': finanzas_insumos,
        'finanzas_por_mes': finanzas_por_mes
    })





from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Jornada, JornadaPorTrato, Procesos, Cosecha  # Asegúrate de importar Cosecha

@login_required(login_url="my_login")
def cuadernodecampo(request):
    user = request.user
    # Obtener las jornadas, jornadas por trato, procesos y cosechas para el usuario autenticado
    jornadas = Jornada.objects.filter(user=user)
    jornadas_por_trato = JornadaPorTrato.objects.filter(user=user)
    procesos = Procesos.objects.filter(user=user)
    cosechas = Cosecha.objects.filter(created_by=user)

    eventos = []

    # Agregar jornadas al calendario
    for jornada in jornadas:
        tarea_2 = f" - {jornada.nombre_tarea_2}" if jornada.nombre_tarea_2 else ""
        tarea_3 = f" - {jornada.nombre_tarea_3}" if jornada.nombre_tarea_3 else ""

        eventos.append({
            'title': f"Jornada: {jornada.nombre_tarea_1}{tarea_2}{tarea_3} ",
            'start': jornada.fecha.isoformat(),
            'end': jornada.fecha.isoformat(),
            'sector': jornada.sector.nombre if jornada.sector else 'Sin sector',
            'trabajador': jornada.asignado.nombre,
        })

    # Agregar jornadas por trato al calendario
    for jornada_trato in jornadas_por_trato:
        tarea_2_trato = f" - {jornada_trato.nombre_tarea_2}" if jornada_trato.nombre_tarea_2 else ""
        tarea_3_trato = f" - {jornada_trato.nombre_tarea_3}" if jornada_trato.nombre_tarea_3 else ""

        eventos.append({
            'title': f"Jornada por Trato: {jornada_trato.nombre_tarea_1}{tarea_2_trato}{tarea_3_trato} ",
            'start': jornada_trato.fecha.isoformat(),
            'end': jornada_trato.fecha.isoformat(),
            'sector': jornada_trato.sector.nombre if jornada_trato.sector else 'Sin sector',
            'trabajador': jornada_trato.asignado.nombre,
        })

    # Agregar procesos al calendario
    for proceso in procesos:
        eventos.append({
            'title': f"Tarea: {proceso.trabajo} ",
            'start': proceso.fecha.isoformat(),
            'end': proceso.fecha.isoformat(),
            
            'trabajador': proceso.asignado.nombre,
        })

    # Agregar cosechas al calendario
    for cosecha in cosechas:
        eventos.append({
            'title': f"Cosecha: {cosecha.tipo_producto} - {cosecha.cantidad} kg",
            'start': cosecha.fecha_cosecha.isoformat(),
            'end': cosecha.fecha_cosecha.isoformat(),
            'sector': cosecha.sector.nombre if cosecha.sector else 'Sin sector',
        })

    # Verificar si la solicitud es para obtener los eventos en formato JSON (por ejemplo, desde FullCalendar)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(eventos, safe=False)
    
    # Renderizar el template HTML si no es una solicitud AJAX
    return render(request, 'agrosmart/cuadernodecampo/cuadernodecampo.html')






from .forms import CosechaForm
from .models import Cosecha

@login_required
def crear_cosecha(request):
    if request.method == 'POST':
        form = CosechaForm(request.POST, user=request.user)
        if form.is_valid():
            cosecha = form.save(commit=False)
            cosecha.created_by = request.user  # Asignar el usuario actual como el creador
            cosecha.user = request.user  # Asignar el usuario actual como el usuario responsable
            cosecha.save()
            return redirect('cosechas_list')  # Redirige a una página de lista de cosechas (modifica según tu URL)
    else:
        form = CosechaForm(user=request.user)
    
    return render(request, 'agrosmart/cosecha/crear_cosecha.html', {'form': form})

@login_required
def cosechas_list(request):
    cosechas = Cosecha.objects.filter(user=request.user)  # Filtra por usuario actual
    return render(request, 'agrosmart/cosecha/gestion_cosecha.html', {'cosechas': cosechas})

