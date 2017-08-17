from django import forms
from django.forms import widgets

from parmap_data_request.models import DataRequest, RequestReason

class DataRequestForm(forms.ModelForm): 
    reason = forms.ModelMultipleChoiceField(
        required = False,
        widget = widgets.CheckboxSelectMultiple(),
        help_text = '',
        queryset = RequestReason.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super(DataRequestForm, self).__init__(*args, **kwargs)
        #self.fields['reason'].queryset = RequestReason.objects.all()
        self.fields['profile'].widget.can_add_related = False

    class Meta: 
        model = DataRequest
        fields = ('resource', 'profile', 'reason')

