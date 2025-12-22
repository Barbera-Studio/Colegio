# core/forms.py
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UsernameField

User = get_user_model()


class RegistroForm(forms.ModelForm):
    """
    Formulario de registro para core.CustomUser.
    Incluye:
    - username
    - email obligatorio y único
    - contraseñas con validación fuerte
    - aceptación de términos
    """
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        help_text="Introduce un correo válido. Lo necesitarás para recuperar tu contraseña."
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Mínimo 8 caracteres, con mayúsculas, minúsculas, números y símbolos."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    terms = forms.BooleanField(
        label="Acepto los términos y condiciones y la política de privacidad.",
        required=True
    )

    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}
        widgets = {
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.", code="email_exists")
        return email

    def clean_password1(self):
        pwd = self.cleaned_data.get("password1") or ""
        # Validadores de Django
        password_validation.validate_password(pwd, user=None)

        # Validación fuerte adicional
        has_lower = any(c.islower() for c in pwd)
        has_upper = any(c.isupper() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_symbol = any(not c.isalnum() for c in pwd)

        if not (has_lower and has_upper and has_digit and has_symbol):
            raise ValidationError(
                "La contraseña debe incluir minúsculas, mayúsculas, números y símbolos.",
                code="weak_password"
            )
        return pwd

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")

        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", ValidationError("Las contraseñas no coinciden.", code="password_mismatch"))

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    """
    Formulario de edición de perfil para core.CustomUser.
    Permite actualizar nombre, apellidos, email y avatar.
    Valida que el email sea único (excepto el del propio usuario).
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Este correo ya está en uso por otro usuario.", code="email_exists")
        return email

