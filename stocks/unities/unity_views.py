from django.views.generic import ListView

from ..models import Unity


class UnityListView(ListView):
    model = Unity
    template_name = ''
    context_object_name = 'unities'