from django.http import HttpResponse
import json
import csv


# Create your views here.
def index(request):

    with open('geonode/static/geonode/files/NSO_Muni.csv', 'r') as locationsCsv:    
        fieldnames = ("city","province","region","mun_code")
        locationsList = []
        reader = csv.DictReader( locationsCsv, fieldnames)
        locationsList = list(reader)

        return HttpResponse(json.dumps(locationsList),mimetype='application/json',status=200)