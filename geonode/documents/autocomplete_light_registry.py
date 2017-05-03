import autocomplete_light
from models import Document

autocomplete_light.register(
    Document,
    search_fields=['^title' 'keywords'],
    autocomplete_js_attributes={
        'placeholder': 'Document name..',
    },
)
