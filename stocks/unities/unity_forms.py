from django import forms

from stocks.models import Unity


class UnityForm(forms.ModelForm):
    class Meta:
        model = Unity
        fields = '__all__'
