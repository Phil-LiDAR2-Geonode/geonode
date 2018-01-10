from django.http import HttpResponse
import json
import csv
from django.contrib.staticfiles.storage import staticfiles_storage


# Create your views here.
def index(request):
    muncode_file = staticfiles_storage.path('geonode/files/NSO_Muni.csv')
    
    with open(muncode_file, 'r') as locationsCsv:
        fieldnames = ("city","province","region","mun_code")
        locationsList = []
        reader = csv.DictReader( locationsCsv, fieldnames)
        locationsList = list(reader)

        return HttpResponse(json.dumps(locationsList),mimetype='application/json',status=200)