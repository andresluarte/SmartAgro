from django import forms 
from .models import Procesos,Contacto,Trabajador,Sector,Huerto,Lote

class DateInput(forms.DateInput):
    input_type='date'

class TimePickerInput(forms.TimeInput):
    input_type = 'time'

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ["trabajo", "fecha", "hora_asignada", "sector", "huerto", "lote", "asignado", "presupuesto", "observacion"]
        widgets = {
            "fecha": DateInput,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Extrae el usuario de los kwargs
        super().__init__(*args, **kwargs)
        
        # Filtrar los queryset según el usuario logueado
        self.fields['asignado'].queryset = Trabajador.objects.filter(user=user)
        self.fields['sector'].queryset = Sector.objects.filter(user=user)
        self.fields['huerto'].queryset = Huerto.objects.filter(user=user)
        self.fields['lote'].queryset = Lote.objects.filter(user=user)

class ContactoForm(forms.ModelForm):

    class Meta:
        model = Contacto
        fields = '__all__'

class ProcesoModificarForm(forms.ModelForm):
    
    class Meta:
        model = Procesos
        fields = ["trabajo", "fecha", "hora_asignada", "sector", "huerto", "lote", "estado", "asignado", "presupuesto", "observacion"]
        widgets = {
            "fecha": forms.SelectDateWidget,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Extrae el usuario de los kwargs
        super().__init__(*args, **kwargs)
        
        # Filtrar los queryset según el usuario logueado
        self.fields['asignado'].queryset = Trabajador.objects.filter(user=user)
        self.fields['sector'].queryset = Sector.objects.filter(user=user)
        self.fields['huerto'].queryset = Huerto.objects.filter(sector__user=user)
        self.fields['lote'].queryset = Lote.objects.filter(huerto__sector__user=user)
class TrabajadorModificarForm(forms.ModelForm):
    
    class Meta:
        model = Trabajador
        fields =  ["nombre","cobro","trabajo_a_realizar"]
        
            
        



        
class FiltroEstado(forms.Form):
    estado = forms.CharField()

class TrabajadorForm(forms.ModelForm): 

    class Meta:
        model = Trabajador
        fields = ['nombre','rut','tipo_contraro','fecha_ingreso', 'fecha_termino_contrato','cobro','trabajo_a_realizar']
        widgets={
            "fecha_ingreso":DateInput(),
            "fecha_termino_contrato": DateInput(),
   
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establece un valor predeterminado para el campo fecha_termino_contrato
        self.fields['fecha_termino_contrato'].initial = 'Sin Fecha Termino'  
####formato

FORMAT_CHOICES = (
    ('xls','xls'),
    ('csv','csv')
)

class FormatoForm(forms.Form):
    format = forms.ChoiceField(choices=FORMAT_CHOICES,widget=forms.Select(attrs={'class':'form-select'}))

from .models import Jornada
#jornada


HORAS_PERMITIDAS = [
    '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00',
    '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
    '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00',
    '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00',
]

class CustomTimePickerInput(DateInput):
    def __init__(self, attrs=None, format=None):
        super().__init__(attrs={'type': 'time', 'step': '1800', 'list': 'horas-permitidas'})
    
    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer)
        rendered += '<datalist id="horas-permitidas">'
        for hora in HORAS_PERMITIDAS:
            rendered += f'<option value="{hora}">'
        rendered += '</datalist>'
        return rendered


from django import forms
from .models import Jornada, Trabajador, Sector, Huerto, Lote

class JornadaForm(forms.ModelForm):
    
    class Meta:
        model = Jornada
        exclude = ['creador']
        fields = ['asignado',  'sector', 'huerto', 'lote', 'fecha', 'nombre_tarea_1', 
                  'hora_inicio_tarea_1', 'hora_fin_tarea_1', 'cobro_tarea_1', 'nombre_tarea_2', 'hora_inicio_tarea_2', 
                  'hora_fin_tarea_2', 'cobro_tarea_2', 'nombre_tarea_3', 'hora_inicio_tarea_3', 'hora_fin_tarea_3', 'cobro_tarea_3',
                  'nombre_extra_1', 'gasto_extra_1', 'nombre_extra_2', 'gasto_extra_2', 'nombre_extra_3', 'gasto_extra_3', 
                  'observacion']
        widgets = {
            "fecha": DateInput(),
            "hora_inicio_tarea_1": CustomTimePickerInput(),
            "hora_fin_tarea_1": CustomTimePickerInput(),
            "hora_inicio_tarea_2": CustomTimePickerInput(),
            "hora_fin_tarea_2": CustomTimePickerInput(),
            "hora_inicio_tarea_3": CustomTimePickerInput(),
            "hora_fin_tarea_3": CustomTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario de kwargs, si está presente
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['asignado'].queryset = Trabajador.objects.filter(user=user)
            self.fields['sector'].queryset = Sector.objects.filter(user=user)
            self.fields['huerto'].queryset = Huerto.objects.filter(user=user)
            self.fields['lote'].queryset = Lote.objects.filter(user=user)

        # Hacer que los campos de cobro no sean de solo lectura
        for field_name in ['cobro_tarea_1', 'cobro_tarea_2', 'cobro_tarea_3']:
            self.fields[field_name].widget.attrs['readonly'] = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        cobro_por_hora = instance.asignado.cobro if instance.asignado else None

        def calcular_cobro_tarea(hora_inicio, hora_fin):
            if hora_inicio and hora_fin and cobro_por_hora:
                hora_inicio = hora_inicio.hour + hora_inicio.minute / 60
                hora_fin = hora_fin.hour + hora_fin.minute / 60
                horas_trabajadas = hora_fin - hora_inicio
                return round(horas_trabajadas * cobro_por_hora, 2)
            return None

        # Calcular los cobros de las tareas
        instance.cobro_tarea_1 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_1'), self.cleaned_data.get('hora_fin_tarea_1'))
        instance.cobro_tarea_2 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_2'), self.cleaned_data.get('hora_fin_tarea_2'))
        instance.cobro_tarea_3 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_3'), self.cleaned_data.get('hora_fin_tarea_3'))

        # Sumar los cobros de las tareas para calcular detalle_gasto_total_tareas
        cobros_tareas = [instance.cobro_tarea_1, instance.cobro_tarea_2, instance.cobro_tarea_3]
        instance.detalle_gasto_total_tareas = sum(filter(None, cobros_tareas))

        # Calcular detalle_gastos_total_extras
        gastos_extras = [instance.gasto_extra_1, instance.gasto_extra_2, instance.gasto_extra_3]
        instance.detalle_gastos_total_extras = sum(filter(None, gastos_extras))

        # Calcular total_gasto_jornada
        instance.total_gasto_jornada = instance.detalle_gasto_total_tareas + instance.detalle_gastos_total_extras

        if commit:
            instance.save()
        return instance

from django import forms
from .models import JornadaPorTrato

class JornadaPorTratoForm(forms.ModelForm):
    
    class Meta:
        model = JornadaPorTrato
        fields = ['asignado', 'sector', 'huerto', 'lote', 'fecha', 'nombre_tarea_1', 'cobro_tarea_1', 
                  'nombre_tarea_2', 'cobro_tarea_2', 'nombre_tarea_3', 'cobro_tarea_3', 
                  'nombre_extra_1', 'gasto_extra_1', 'nombre_extra_2', 'gasto_extra_2', 'nombre_extra_3', 'gasto_extra_3', 
                  'observacion']
        widgets = {
            "fecha": forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['asignado'].queryset = Trabajador.objects.filter(user=user)
            self.fields['sector'].queryset = Sector.objects.filter(user=user)
            self.fields['huerto'].queryset = Huerto.objects.filter(user=user)
            self.fields['lote'].queryset = Lote.objects.filter(user=user)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Calcular total_gasto_jornada, detalle_gasto_total_tareas y detalle_gastos_total_extras
        cobros_tareas = [instance.cobro_tarea_1, instance.cobro_tarea_2, instance.cobro_tarea_3]
        instance.detalle_gasto_total_tareas = sum(filter(None, cobros_tareas))
        
        gastos_extras = [instance.gasto_extra_1, instance.gasto_extra_2, instance.gasto_extra_3]
        instance.detalle_gastos_total_extras = sum(filter(None, gastos_extras))

        instance.total_gasto_jornada = instance.detalle_gasto_total_tareas + instance.detalle_gastos_total_extras

        if commit:
            instance.save()
        return instance


from django import forms
from .models import Jornada, Lote

class JornadaModificarForm(forms.ModelForm):
    class Meta:
        model = Jornada
        fields = ['asignado', 'sector', 'huerto', 'lote', 'fecha', 'estado', 'nombre_tarea_1',
                  'hora_inicio_tarea_1', 'hora_fin_tarea_1', 'cobro_tarea_1', 'nombre_tarea_2',
                  'hora_inicio_tarea_2', 'hora_fin_tarea_2', 'cobro_tarea_2', 'nombre_tarea_3',
                  'hora_inicio_tarea_3', 'hora_fin_tarea_3', 'cobro_tarea_3', 'nombre_extra_1',
                  'gasto_extra_1', 'nombre_extra_2', 'gasto_extra_2', 'nombre_extra_3', 'gasto_extra_3',
                  'observacion']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filtrar sectores
            self.fields['sector'].queryset = Sector.objects.filter(user=user)
            # Filtrar huertos
            self.fields['huerto'].queryset = Huerto.objects.filter(user=user)
            # Filtrar trabajadores
            self.fields['asignado'].queryset = Trabajador.objects.filter(user=user)

            if self.instance and self.instance.huerto:
                self.fields['lote'].queryset = Lote.objects.filter(huerto=self.instance.huerto, user=user)
            else:
                self.fields['lote'].queryset = Lote.objects.none()

        for field_name in ['cobro_tarea_1', 'cobro_tarea_2', 'cobro_tarea_3']:
            self.fields[field_name].widget.attrs['readonly'] = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        cobro_por_hora = instance.asignado.cobro if instance.asignado else None

        def calcular_cobro_tarea(hora_inicio, hora_fin):
            if hora_inicio and hora_fin and cobro_por_hora:
                hora_inicio = hora_inicio.hour + hora_inicio.minute / 60
                hora_fin = hora_fin.hour + hora_fin.minute / 60
                horas_trabajadas = hora_fin - hora_inicio
                return round(horas_trabajadas * cobro_por_hora, 2)
            return None

        instance.cobro_tarea_1 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_1'), self.cleaned_data.get('hora_fin_tarea_1'))
        instance.cobro_tarea_2 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_2'), self.cleaned_data.get('hora_fin_tarea_2'))
        instance.cobro_tarea_3 = calcular_cobro_tarea(self.cleaned_data.get('hora_inicio_tarea_3'), self.cleaned_data.get('hora_fin_tarea_3'))

        cobros_tareas = [instance.cobro_tarea_1, instance.cobro_tarea_2, instance.cobro_tarea_3]
        instance.detalle_gasto_total_tareas = sum(filter(None, cobros_tareas))

        gastos_extras = [instance.gasto_extra_1, instance.gasto_extra_2, instance.gasto_extra_3]
        instance.detalle_gastos_total_extras = sum(filter(None, gastos_extras))

        instance.total_gasto_jornada = instance.detalle_gasto_total_tareas + instance.detalle_gastos_total_extras

        if commit:
            instance.save()
        return instance

from django import forms
from .models import Sector, Huerto, Lote

class SectorForm(forms.ModelForm):
    google_maps_link = forms.URLField(
        max_length=200, 
        required=False,
        label="Enlace de Google Maps (opcional)"
    )

    class Meta:
        model = Sector
        fields = ['nombre', 'latitud', 'longitud', 'google_maps_link']

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get("latitud")
        lng = cleaned_data.get("longitud")
        link = cleaned_data.get("google_maps_link")

        if not link and (not lat or not lng):
            raise forms.ValidationError("Debes proporcionar coordenadas o un enlace de Google Maps.")




class HuertoForm(forms.ModelForm):
    class Meta:
        model = Huerto
        fields = ['nombre', 'sector']  # Incluye el campo sector

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Recibir el usuario desde la vista
        super(HuertoForm, self).__init__(*args, **kwargs)
        # Filtrar los sectores para que solo aparezcan los del usuario logueado
        if user is not None:
            self.fields['sector'].queryset = Sector.objects.filter(user=user)


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nombre', 'huerto']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['huerto'].queryset = Huerto.objects.filter(user=user)


class SectorModificarForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['nombre', 'latitud', 'longitud', 'google_maps_link']

class HuertoModificarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(HuertoModificarForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['sector'].queryset = Sector.objects.filter(user=user)

    class Meta:
        model = Huerto
        fields = ['nombre', 'sector']

class LoteModificarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LoteModificarForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['huerto'].queryset = Huerto.objects.filter(user=user)

    class Meta:
        model = Lote
        fields = ['nombre', 'huerto']

from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser
from django import forms

from django.forms.widgets import PasswordInput,TextInput


class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        widgets = {
            'user_type': forms.HiddenInput()  # Campo oculto
        }

    def save(self, commit=True):
        # Guardamos el formulario pero asignamos el tipo de usuario
        user = super(CreateUserForm, self).save(commit=False)
        if not user.user_type:  # Si el tipo de usuario no ha sido asignado, lo asignamos
            user.user_type = 'admin'
        if commit:
            user.save()
        return user
    
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, EmpresaOFundo

from django import forms
from .models import CustomUser, EmpresaOFundo

class RegisterColaboradorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'user_type', 'empresa']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario autenticado
        super(RegisterColaboradorForm, self).__init__(*args, **kwargs)

        # Filtrar las empresas para que solo muestre las del usuario autenticado
        if user:
            self.fields['empresa'].queryset = EmpresaOFundo.objects.filter(created_by=user)

        # Mantener visible el campo user_type pero restringir las opciones
        self.fields['user_type'].choices = [
            choice for choice in CustomUser.USER_TYPE_CHOICES if choice[0] not in ['superuser', 'admin']
        ]

    def save(self, commit=True):
        # Guardamos el formulario pero antes encriptamos la contraseña
        user = super(RegisterColaboradorForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user




class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


from .models import EmpresaOFundo

from django import forms
from django.core.exceptions import ValidationError
from .models import EmpresaOFundo
from PIL import Image

class EmpresaOFundoForm(forms.ModelForm):
    class Meta:
        model = EmpresaOFundo
        fields = ['nombre', 'numero_hectareas', 'foto1', 'foto2', 'foto3', 'logo', 'ubicacion', 'tipo_cultivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_hectareas': forms.NumberInput(attrs={'class': 'form-control'}),
            'foto1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'foto2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'foto3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_cultivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        foto1 = cleaned_data.get('foto1')
        foto2 = cleaned_data.get('foto2')
        foto3 = cleaned_data.get('foto3')

        # Definir la relación de aspecto estándar (1250:837)
        aspect_ratio_target = 1250 / 837  # Calcula la relación de aspecto

        # Verifica la foto1
        if foto1:
            img1 = Image.open(foto1)
            width1, height1 = img1.size
            aspect_ratio1 = width1 / height1

            # Verifica que la relación de aspecto de foto1 sea correcta
            if not self.is_aspect_ratio_valid(aspect_ratio1, aspect_ratio_target):
                raise ValidationError("La relación de aspecto de foto1 debe ser 1250:837.")

        # Verifica las otras fotos
        for i, foto in enumerate([foto2, foto3], start=2):
            if foto:
                img = Image.open(foto)
                width, height = img.size
                aspect_ratio = width / height
                
                # Verifica que la relación de aspecto de las otras fotos sea correcta
                if not self.is_aspect_ratio_valid(aspect_ratio, aspect_ratio_target):
                    raise ValidationError(f"La relación de aspecto de foto{i} debe ser 1250:837.")

        return cleaned_data

    def is_aspect_ratio_valid(self, aspect_ratio, target_ratio, tolerance=0.01):
        """
        Verifica si la relación de aspecto está dentro de un margen de tolerancia del objetivo.
        """
        return abs(aspect_ratio - target_ratio) < tolerance





#edit colaborador
class EditColaboradorForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['user_type', 'empresa']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario autenticado
        super(EditColaboradorForm, self).__init__(*args, **kwargs)

        # Filtrar las empresas solo para las del usuario autenticado
        if user:
            self.fields['empresa'].queryset = EmpresaOFundo.objects.filter(created_by=user)

        # Evitar que los 'colaboradores' y 'ayudantes' vean los tipos de usuario 'superuser' y 'admin'
        self.fields['user_type'].choices = [
            choice for choice in CustomUser.USER_TYPE_CHOICES if choice[0] not in ['superuser', 'admin']
        ]

from django import forms
from .models import SectorPoligon

class SectorPoligonForm(forms.ModelForm):
    class Meta:
        model = SectorPoligon
        fields = ['nombre', 'coordenadas']
        widgets = {
            'coordenadas': forms.HiddenInput(),  # Ocultamos este campo, se llenará desde JavaScript
        }
