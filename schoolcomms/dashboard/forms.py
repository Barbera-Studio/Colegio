from django import forms
from django.contrib.auth import get_user_model

from .models import Aviso, Tarea, Incidencia, PrivateMessage

User = get_user_model()


# ---------------------- FORMULARIO DE AVISOS ----------------------
class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = ['titulo', 'contenido', 'destinatarios']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del aviso'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Contenido del aviso'
            }),
            'destinatarios': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
        }


# ---------------------- FORMULARIO DE TAREAS ----------------------
class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "descripcion", "fecha_entrega", "hora", "completada"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe el título..."}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe la tarea..."}),
            "fecha_entrega": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "hora": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "completada": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ---------------------- FORMULARIO DE INCIDENCIAS ----------------------
class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Problema con Aula Virtual'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe la incidencia...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class EstadoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['estado']


# ---------------------- FORMULARIO DE MENSAJE PRIVADO ----------------------
class PrivateMessageForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Destinatario",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = PrivateMessage
        fields = ["receiver", "subject", "content"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asunto"}),
            "content": forms.Textarea(attrs={"class": "form-control", "placeholder": "Escribe tu mensaje..."}),
        }
