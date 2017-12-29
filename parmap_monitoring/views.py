from django.shortcuts import render
from parmap_monitoring.models import DataDownload
from geonode.people.models import Profile
from django.template import loader
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
import csv
import os

def export_to_csv(request):
	if Profile.objects.get(username=request.user.username).is_staff:
		date = timezone.now()
		outfile = "_".join(["parmap_downloads", date.strftime('%Y%m%d'), date.strftime('%H%M%S') + ".csv"])
		outfile_path = os.path.join(os.path.join(settings.MEDIA_ROOT, "data_downloads/", outfile))
		qs = DataDownload.objects.all()
		model = qs.model
		csv_obj = open(outfile_path, 'w')
		writer = csv.writer(csv_obj)

		headers = []
		for field in model._meta.fields:
			headers.append(field.name)
		writer.writerow(headers)

		for obj in qs:
			row = []
			for field in headers:
				val = getattr(obj, field)
				if callable(val):
					val = val()
				if type(val) == unicode:
					val = val.encode("utf-8")
				row.append(val)
			writer.writerow(row)

		csv_obj.close()

		fp = open(outfile_path, 'rb')
		response = HttpResponse(fp, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=%s ' % outfile
		return response
