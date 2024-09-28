import django_filters
from django_filters import DateFromToRangeFilter
from .models import Procesos,Trabajador,Jornada


class ProcesoFilter(django_filters.FilterSet):
    presupuesto = django_filters.RangeFilter()
    fecha = DateFromToRangeFilter(field_name='fecha', label='Fecha')
    trabajo = django_filters.CharFilter(lookup_expr='icontains')
    asignado = django_filters.CharFilter(lookup_expr='icontains')
    observacion = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model=Procesos
        fields = {'trabajo': ['exact'],
                  'estado':['exact'],
                
                  'asignado':['exact'],
                  'observacion':['exact'],
                  
                  'hora_asignada': ['exact']}


class TrabajadorFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    cobro = django_filters.RangeFilter()
    trabajo_a_realizar = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model=Trabajador
        fields = {'nombre': ['exact'],
                  
                  'trabajo_a_realizar':['exact']
                }


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


