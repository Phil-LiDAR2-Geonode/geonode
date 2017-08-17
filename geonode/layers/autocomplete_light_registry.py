import autocomplete_light
from geonode.layers.models import Layer
from geonode.documents.models import Document

class ParmapAutocomplete(autocomplete_light.AutocompleteListBase):
    # JS is responsible for converting the sluggified version of the keyword
    autocomplete_list = []
    for layer in Layer.objects.all():
        for keyword in layer.keywords.names():
            autocomplete_list.append(unicode(keyword).encode('utf8'))

    for document in Document.objects.all():
        for keyword in document.keywords.names():
            autocomplete_list.append(unicode(keyword).encode('utf8'))

    choices = set(autocomplete_list)

autocomplete_light.register(
    ParmapAutocomplete,
    autocomplete_js_attributes={
        'placeholder': 'Specify keyword here..',
    },
)
