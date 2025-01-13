import django_filters
from django_filters import DateFromToRangeFilter
from .models import Procesos,Trabajador,Jornada,JornadaPorTrato


class ProcesoFilter(django_filters.FilterSet):
    presupuesto = django_filters.RangeFilter()
    fecha = DateFromToRangeFilter(field_name='fecha', label='Fecha')

    observacion = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model=Procesos
        fields = {'trabajo': ['exact'],
                  'estado':['exact'],
                
                  'asignado':['exact'],
                  'observacion':['exact'],
                  
                  'fecha_compra': ['exact']}
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario de kwargs, si está presente
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar los queryset de los campos en función del usuario
            if user.user_type == 'superuser':
                # Si el usuario es superusuario, puede ver todos los trabajadores
                self.filters['asignado'].queryset = Trabajador.objects.all()
            elif user.user_type == 'admin':
                # Si el usuario es admin, puede ver los trabajadores que creó directamente
                self.filters['asignado'].queryset = Trabajador.objects.filter(created_by=user)
            elif user.user_type == 'colaborador':
                # Si el usuario es colaborador, puede ver los trabajadores que fueron creados por él
                colaborador_user = user.created_by
                self.filters['asignado'].queryset = Trabajador.objects.filter(created_by=colaborador_user)
            elif user.user_type == 'agricultor' or user.user_type == 'ayudante':
                # Si el usuario es agricultor o ayudante, puede ver los trabajadores creados por su colaborador y su admin
                colaborador_user = user.created_by
                admin_user = colaborador_user.created_by if colaborador_user else None
                self.filters['asignado'].queryset = Trabajador.objects.filter(created_by__in=[colaborador_user, admin_user])
            else:
                # Si el usuario no tiene un tipo definido, no podrá ver ningún trabajador
                self.filters['asignado'].queryset = Trabajador.objects.none()
            
        



class TrabajadorFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    cobro = django_filters.RangeFilter()
    trabajo_a_realizar = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model=Trabajador
        fields = {'nombre': ['exact'],
                  
                  'trabajo_a_realizar':['exact']
                }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario de kwargs, si está presente
        super().__init__(*args, **kwargs)


from .models import Jornada, Trabajador, Sector, Huerto, Lote,JornadaPorTrato
class JornadaFilter(django_filters.FilterSet):
    total_gasto_jornada = django_filters.RangeFilter(
        label='Gasto Total Jornada Desde $ : Y HASTA $ :',
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'number'}),
    )
    fecha = django_filters.DateFromToRangeFilter(
        field_name='fecha', 
        label='Fecha', 
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )
    asignado__nombre = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Buscar Asignado'
    )

    class Meta:
        model = Jornada
        fields = {
            'estado': ['exact'],
            'asignado': ['exact'],
            'sector': ['exact'],
            'huerto': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario de kwargs, si está presente
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar los queryset de los campos en función del usuario
            self.filters['sector'].queryset = Sector.objects.filter(user=user)
            self.filters['huerto'].queryset = Huerto.objects.filter(user=user)
            self.filters['asignado'].queryset = Trabajador.objects.filter(user=user)

class JornadaPorTratoFilter(django_filters.FilterSet):
    total_gasto_jornada = django_filters.RangeFilter(
        label='Gasto Total Jornada Desde $ : Y HASTA $ :',
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'number'}),
    )
    fecha = django_filters.DateFromToRangeFilter(
        field_name='fecha', 
        label='Fecha', 
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )
    asignado__nombre = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Buscar Asignado'
    )

    class Meta:
        model = JornadaPorTrato
        fields = {
            'estado': ['exact'],
            'asignado': ['exact'],
            'sector': ['exact'],
            'huerto': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario de kwargs, si está presente
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar los queryset de los campos en función del usuario
            self.filters['sector'].queryset = Sector.objects.filter(user=user)
            self.filters['huerto'].queryset = Huerto.objects.filter(user=user)
            self.filters['asignado'].queryset = Trabajador.objects.filter(user=user)


