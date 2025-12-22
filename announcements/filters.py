import django_filters
from .models import Announcement, ClassGroup
from django import forms

class AnnouncementFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(field_name="title", lookup_expr="icontains", label="Buscar")
    group = django_filters.ModelChoiceFilter(field_name="target_groups", queryset=ClassGroup.objects.all(), label="Grupo")
    ate_from = django_filters.DateFilter(
    field_name="created_at",
    lookup_expr="date__gte",
    label="Desde",
    widget=forms.DateInput(attrs={"type": "date"})
)

date_to = django_filters.DateFilter(
    field_name="created_at",
    lookup_expr="date__lte",
    label="Hasta",
    widget=forms.DateInput(attrs={"type": "date"})
)

class Meta:
    model = Announcement
    fields = ["q", "group", "date_from", "date_to"]
