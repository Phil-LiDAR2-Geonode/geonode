import autocomplete_light
from models import Document
from geonode.layers.autocomplete_light_registry import ParmapAutocomplete

autocomplete_light.register(
    ParmapAutocomplete,
    autocomplete_js_attributes={
        'placeholder': 'Specify keyword here..',
    },
)
