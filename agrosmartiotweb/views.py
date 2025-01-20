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
from .admin import ProcesosResource,JornadasResource,TrabajadorResource,JornadasPorTratoResource


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
    def get_queryset(self, request):
        user = request.user
        if user.is_superuser:
            queryset = Procesos.objects.all()
        elif user.user_type == 'admin':
        # El admin puede ver los procesos de sus subordinados
            subordinates = CustomUser.objects.filter(created_by=user)
            queryset = Procesos.objects.filter(user__in=[user] + list(subordinates))
        elif user.user_type == 'colaborador':
            # Obtener el admin del colaborador
            admin_user = user.created_by
            # Obtener todos los usuarios que fueron creados por el admin
            subordinates = CustomUser.objects.filter(created_by=admin_user)
            # El colaborador puede ver sus procesos, los procesos de su admin y los procesos de los usuarios subordinados
            queryset = Procesos.objects.filter(user__in=[user, admin_user] + list(subordinates))
        elif user.user_type == 'agricultor' or user.user_type == 'ayudante':
            # Agricultor y Ayudante solo pueden ver lo que han creado
            queryset = Procesos.objects.filter(user=user)
        else:
            queryset = Procesos.objects.none()

        # Aplicar filtros adicionales usando ProcesoFilter
        return ProcesoFilter(request.GET, queryset=queryset, user=user).qs


    def get(self, request):
        queryset = self.get_queryset(request)
        dataset = ProcesosResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="procesos.xls"'
        return response

    def post(self, request):
        queryset = self.get_queryset(request)
        dataset = ProcesosResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="procesos.xls"'
        return response

    
#exportar excel jornada


class ExportToExcelViewJornada(View):
    def get_queryset(self, request):
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

        # Aplicar filtros adicionales
        return JornadaFilter(request.GET, queryset=queryset, user=user).qs

    def get(self, request):
        queryset = self.get_queryset(request)
        dataset = JornadasResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornadas.xls"'
        return response
    
class ExportToExcelViewJornadaPorTrato(View):
    def get_queryset(self, request):
        user = request.user
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

        # Aplicar filtros adicionales
        return JornadaPorTratoFilter(request.GET, queryset=queryset, user=user).qs

    def get(self, request):
        queryset = self.get_queryset(request)
        dataset = JornadasPorTratoResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Jornada_Por_Trato.xls"'
        return response



#exportar trabajador
class ExportToExcelViewTrabajador(View):
    def get_queryset(self, request):
        user = request.user
        if user.is_superuser:
            queryset = Trabajador.objects.all()
        elif user.user_type == 'admin':
            queryset = Trabajador.objects.filter(created_by=user)
        elif user.user_type == 'colaborador':
            admin_user = user.created_by
            queryset = Trabajador.objects.filter(created_by__in=[user, admin_user])
        elif user.user_type == 'agricultor':
            colaborador_user = user.created_by
            admin_user = colaborador_user.created_by if colaborador_user else None
            queryset = Trabajador.objects.filter(created_by__in=[user, colaborador_user, admin_user])
        else:
            queryset = Trabajador.objects.none()

        # Aplicar filtros adicionales usando TrabajadorFilter
        return TrabajadorFilter(request.GET, queryset=queryset, user=user).qs

    def get(self, request):
        queryset = self.get_queryset(request)
        dataset = TrabajadorResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="trabajadores.xls"'
        return response

    def post(self, request):
        queryset = self.get_queryset(request)
        dataset = TrabajadorResource().export(queryset=queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="trabajadores.xls"'
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
    print(filtered_jornadas.qs)

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
    filtered_jornadas = JornadaPorTratoFilter(request.GET, queryset=queryset, user=user)

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



from django.http import HttpResponseForbidden

@login_required(login_url="my_login")
def TrabajadorList(request):
    # Limitar acceso solo a superuser, admin y colaborador
    if not (request.user.is_superuser or request.user.user_type in ['admin', 'colaborador']):
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    
    if request.user.is_superuser:
        queryset = Trabajador.objects.all()
    elif request.user.user_type == 'admin':
        queryset = Trabajador.objects.filter(created_by=request.user)
    elif request.user.user_type == 'colaborador':
        # Colaborador puede ver sus propios trabajadores y los de su admin
        admin_user = request.user.created_by
        queryset = Trabajador.objects.filter(created_by__in=[request.user, admin_user])
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
    
    if user.is_superuser:
        queryset = Procesos.objects.all()
    elif user.user_type == 'admin':
        # El admin puede ver los procesos de sus subordinados
        subordinates = CustomUser.objects.filter(created_by=user)
        queryset = Procesos.objects.filter(user__in=[user] + list(subordinates))
    elif user.user_type == 'colaborador':
        # Obtener el admin del colaborador
        admin_user = user.created_by
        # Obtener todos los usuarios que fueron creados por el admin
        subordinates = CustomUser.objects.filter(created_by=admin_user)
        # El colaborador puede ver sus procesos, los procesos de su admin y los procesos de los usuarios subordinados
        queryset = Procesos.objects.filter(user__in=[user, admin_user] + list(subordinates))
    elif user.user_type in ['agricultor', 'ayudante']:
        queryset = Procesos.objects.filter(user=user)
    else:
        queryset = Procesos.objects.none()

    # Aplicando el filtro de búsqueda
    filtered_proceso = ProcesoFilter(request.GET, queryset=queryset, user=user)
    
    # Ordenando por fecha de creación en orden descendente
    queryset = filtered_proceso.qs.order_by('-fecha_creacion', '-hora_creacion')


    # Paginación
    context = {'filtered_proceso': filtered_proceso}
    paginated_filtered_proceso = Paginator(queryset, 4)  # Número de elementos por página
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

from datetime import datetime, timedelta
from .models import TemperatureHumidityLocation
from .models import HumidityTemperaturaSoil, SensorAire, SensorSuelo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
        fecha_registro = request.POST.get('fecha_registro')

        # Verificar que los datos obligatorios estén presentes
        if not all([temperature, humidity, latitude, longitude, fecha_registro]):
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)

        # Convertir `fecha_registro` a un objeto datetime
        try:
            fecha_registro_dt = datetime.strptime(fecha_registro, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS'}, status=400)

        # Obtener la hora actual
        ahora = datetime.now()

        # Verificar que `fecha_registro` no sea más de 5 minutos en el futuro
        if fecha_registro_dt > ahora + timedelta(minutes=5):
            return JsonResponse({'status': 'error', 'message': 'Fecha de registro inválida, no puede ser más de 5 minutos en el futuro'}, status=400)

        # Crear una nueva entrada de datos asociada al sensor
        TemperatureHumidityLocation.objects.create(
            temperature=temperature,
            humidity=humidity,
            latitude=latitude,
            longitude=longitude,
            sensor=sensor,
            fecha_registro=fecha_registro  # Asociar los datos al sensor encontrado por la API Key
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
        fecha_registro = request.POST.get('fecha_registro')


        # Verificar que los datos obligatorios estén presentes
        if not all([humiditysoil, temperature,fecha_registro]):
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)

        # Crear una nueva entrada de datos asociada al sensor
        HumidityTemperaturaSoil.objects.create(
            humiditysoil=humiditysoil,
            temperature=temperature,
            sensor=sensor,
            fecha_registro=fecha_registro  # Asociar los datos al sensor encontrado por la API Key
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

from django.db.models import Avg
from datetime import timedelta
from django.utils import timezone


def combined_data_view(request):
    user = request.user
    sensors = SensorAire.objects.filter(user=user)

    if not sensors.exists():
        return render(request, 'agrosmart/tiemporeal.html', {
            'sensor_data': [],
            'no_sensors_message': "No tienes sensores registrados.",
        })

    sensor_data = []
    for sensor in sensors:
        # Obtener el dato más reciente basado en fecha_registro
        latest_data = TemperatureHumidityLocation.objects.filter(sensor=sensor).order_by('-fecha_registro').first()
        if latest_data:
            temperature = float(latest_data.temperature)
            humidity = float(latest_data.humidity)

        

            # Calcular el promedio de las últimas 24 horas por hora usando fecha_registro
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            hourly_data = TemperatureHumidityLocation.objects.filter(
                sensor=sensor, fecha_registro__gte=twenty_four_hours_ago
            ).values('fecha_registro__hour').annotate(
                avg_temperature=Avg('temperature'),
                avg_humidity=Avg('humidity')
            ).order_by('fecha_registro__hour')

            # Preparar datos para el gráfico
            hourly_temperature = [data['avg_temperature'] for data in hourly_data]
            hourly_humidity = [data['avg_humidity'] for data in hourly_data]
            hours = [data['fecha_registro__hour'] for data in hourly_data]

            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': latest_data,
                'sensor_name':sensor.name,
                'hourly_temperature': hourly_temperature,
                'hourly_humidity': hourly_humidity,
                'hours': hours
            })
        else:
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': None,

                'hourly_temperature': [],
                'hourly_humidity': [],
                'hours': [],
            })

    return render(request, 'agrosmart/tiemporeal.html', {'sensor_data': sensor_data})





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

       
            # Recomendaciones basadas en la temperatura del suelo
          
            # Agregar datos a la lista
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': latest_data,
                'sensor_name':sensor.name,

            })
        else:
            # Si no hay datos, agregar el sensor con un mensaje de falta de datos
            sensor_data.append({
                'sensor_id': sensor.id,
                'latest_data': None,

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

    # Datos de la última hora para temperatura y humedad del aire
    last_hour_data_air = (
        TemperatureHumidityLocation.objects
        .filter(sensor__in=user_sensors_air, timestamp__gte=timezone.now() - timedelta(hours=1))
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

    last_hour_data_air = [
        {
            'minute': entry['minute'].strftime('%Y-%m-%d %H:%M:%S'),
            'avg_temp_hour': round(entry['avg_temp_hour'], 2),
            'avg_humidity_hour': round(entry['avg_humidity_hour'], 2),
        } for entry in last_hour_data_air
    ]

    context = {
        'temp_humidity_data': json.dumps(temp_humidity_data),
        'soil_data': json.dumps(soil_data),
        'last_hour_data_air': json.dumps(last_hour_data_air),
      
        
    }
    
    return render(request, 'agrosmart/informes.html', context)


import plotly.graph_objects as go
from django.shortcuts import render
from django.db.models import Avg
from django.db.models.functions import TruncHour
from .models import SensorAire, SensorSuelo, TemperatureHumidityLocation, HumidityTemperaturaSoil
import json
from datetime import timedelta
from django.utils import timezone

def informesporsensor(request):
    # Obtener sensores asociados al usuario autenticado
    user_sensors_air = SensorAire.objects.filter(user=request.user)
    user_sensors_soil = SensorSuelo.objects.filter(user=request.user)

    # Crear una lista para almacenar los gráficos
    charts = []

    # Datos para los sensores de aire
    for sensor in user_sensors_air:
        temp_humidity_data = (
            TemperatureHumidityLocation.objects
            .filter(sensor=sensor)  # Filtrar solo los datos de este sensor
            .annotate(hour=TruncHour('timestamp'))
            .values('hour')
            .annotate(
                avg_temp=Avg('temperature'),
                avg_humidity=Avg('humidity')
            )
            .order_by('hour')
        )
        
        # Preparar los datos para el gráfico
        hours = [entry['hour'].strftime('%Y-%m-%d %H:%M:%S') for entry in temp_humidity_data]
        avg_temps = [entry['avg_temp'] for entry in temp_humidity_data]
        avg_humidities = [entry['avg_humidity'] for entry in temp_humidity_data]

        # Crear gráfico interactivo con Plotly
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hours,
            y=avg_temps,
            mode='lines+markers',
            name='Temperatura Promedio',
            line=dict(color='red', width=2),
            marker=dict(size=8, color='red')
        ))

        fig.add_trace(go.Scatter(
            x=hours,
            y=avg_humidities,
            mode='lines+markers',
            name='Humedad Promedio',
            line=dict(color='blue', width=2),
            marker=dict(size=8, color='blue')
        ))

        # Personalización del gráfico
        fig.update_layout(
            title=f'Sensor de Aire: {sensor.name}',
            xaxis_title='Hora',
            yaxis_title='Valor',
            template='plotly',  # Fondo blanco
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=150),  # Ajustar márgenes para evitar que los títulos de los ejes se sobrepongan
            showlegend=True,
            hovermode='closest',  # Mejor visualización de los puntos en el gráfico
            plot_bgcolor='white',  # Fondo blanco para el gráfico
            paper_bgcolor='white',  # Fondo blanco para el área fuera del gráfico
            font=dict(color='black'),  # Color de fuente negro para los textos
            xaxis=dict(
                tickangle=45,  # Rotar las etiquetas del eje X para que no se sobrepongan
                ticks='outside',  # Ticks fuera para que no se sobrepongan con los textos
            ),
            yaxis=dict(
                ticks='outside',  # Ticks fuera para el eje Y
            ),
            legend=dict(
                orientation='h',  # Colocar la leyenda horizontal
                yanchor='top',  # Fijar la leyenda arriba
                y=-0.2,  # Mover la leyenda fuera del gráfico, debajo
                xanchor='center',
                x=0.5  # Centrar la leyenda debajo del gráfico
            ),
        )



        # Convertir la figura a HTML y agregarla a la lista de gráficos
        graph_html = fig.to_html(full_html=False)
        charts.append(graph_html)

    # Datos para los sensores de suelo
    for sensor in user_sensors_soil:
        soil_data = (
            HumidityTemperaturaSoil.objects
            .filter(sensor=sensor)
            .annotate(hour=TruncHour('timestamp'))
            .values('hour')
            .annotate(
                avg_humidity_soil=Avg('humiditysoil'),
                avg_temp=Avg('temperature')
            )
            .order_by('hour')
        )
        
        # Preparar los datos para el gráfico
        hours = [entry['hour'].strftime('%Y-%m-%d %H:%M:%S') for entry in soil_data]
        avg_humidity_soil = [entry['avg_humidity_soil'] for entry in soil_data]
        avg_temp_soil = [entry['avg_temp'] for entry in soil_data]

        # Crear gráfico interactivo con Plotly
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hours,
            y=avg_temp_soil,
            mode='lines+markers',
            name='Temperatura Promedio Suelo',
            line=dict(color='green', width=2),
            marker=dict(size=8, color='green')
        ))

        fig.add_trace(go.Scatter(
            x=hours,
            y=avg_humidity_soil,
            mode='lines+markers',
            name='Humedad Promedio Suelo',
            line=dict(color='orange', width=2),
            marker=dict(size=8, color='orange')
        ))

        # Personalización del gráfico
        fig.update_layout(
            title=f'Sensor de Suelo: {sensor.name}',
            xaxis_title='Hora',
            yaxis_title='Valor',
            template='plotly',  # Fondo blanco
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=150),  # Ajustar márgenes para evitar que los títulos de los ejes se sobrepongan
            showlegend=True,
            hovermode='closest',  # Mejor visualización de los puntos en el gráfico
            plot_bgcolor='white',  # Fondo blanco para el gráfico
            paper_bgcolor='white',  # Fondo blanco para el área fuera del gráfico
            font=dict(color='black'),  # Color de fuente negro para los textos
            xaxis=dict(
                tickangle=45,  # Rotar las etiquetas del eje X para que no se sobrepongan
                ticks='outside',  # Ticks fuera para que no se sobrepongan con los textos
            ),
            yaxis=dict(
                ticks='outside',  # Ticks fuera para el eje Y
            ),
            legend=dict(
                orientation='h',  # Colocar la leyenda horizontal
                yanchor='top',  # Fijar la leyenda arriba
                y=-0.2,  # Mover la leyenda fuera del gráfico, debajo
                xanchor='center',
                x=0.5  # Centrar la leyenda debajo del gráfico
            ),
        )

        # Convertir la figura a HTML y agregarla a la lista de gráficos
        graph_html = fig.to_html(full_html=False)
        charts.append(graph_html)

    context = {
        'charts': charts
    }

    return render(request, 'agrosmart/informesporsensor.html', context)

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
from django.db.models import Q
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
    if user.user_type == 'admin':
    # Admin: ve sus propias finanzas y las de sus colaboradores y trabajadores
        finanzas_insumos = FinanzasPorInsumosyMaquinaria.objects.filter(
            Q(user=user) | Q(user__created_by=user)  # El admin ve sus propias finanzas y las de sus colaboradores
        ).values('trabajo__trabajo').annotate(
            total_gasto=Sum('gasto_total')
        )
    elif user.user_type == 'colaborador':
        # Colaborador: ve sus propias finanzas, las de los trabajadores asignados por él, y las del administrador
        finanzas_insumos = FinanzasPorInsumosyMaquinaria.objects.filter(
            Q(user=user) | Q(user__created_by=user) | Q(user__created_by__created_by=user)  # El colaborador ve sus finanzas, las del admin y de los ayudantes/agricultores
        ).values('trabajo__trabajo').annotate(
            total_gasto=Sum('gasto_total')
        )

    elif user.user_type in ['ayudante', 'agricultor']:
        # Ayudante o Agricultor: solo ve sus propias finanzas
        finanzas_insumos = FinanzasPorInsumosyMaquinaria.objects.filter(
            user=user
        ).values('trabajo__trabajo').annotate(
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
            'start': proceso.fecha_compra,
            'end': proceso.fecha_compra,
            
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

