from django.contrib.auth.models import AbstractUser
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    language = models.CharField(max_length=10, choices=[("es", "Castellano"), ("va", "Valencià")])

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('padre', 'Padre'),
        ('alumno', 'Alumno'),
        ('profesor', 'Profesor'),
        ('director', 'Director'),
        ('admin', 'Administrador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    
class Classroom(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

class Group(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    tutor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={"role": "teacher"})
