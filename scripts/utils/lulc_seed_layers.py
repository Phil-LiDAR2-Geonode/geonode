#!/usr/bin/python
# Geonode

__version__ = "0.2.2"

from geonode.settings import GEONODE_APPS
import geonode.settings as settings
import subprocess
import os

from datetime import datetime, timedelta
from django.contrib.auth.models import Group
from django.db.models import Q
from geonode.base.models import TopicCategory
from geonode.layers.models import Layer, Style
from geoserver.catalog import Catalog
from guardian.shortcuts import assign_perm, get_anonymous_user
from pprint import pprint
from threading import Thread

def seed_layers(layer):
	try:
			out = subprocess.check_output(['/home/geonode/geonode/' + '/gwc.sh', 'seed',
																		 '{0}:{1}'.format(
																				 layer.workspace, layer.name), 'EPSG:900913', '-v', '-a',
																		 settings.OGC_SERVER['default']['USER'] + ':' +
																		 settings.OGC_SERVER['default'][
																				 'PASSWORD'], '-u',
																		 settings.OGC_SERVER['default']['LOCATION'] + 'gwc/rest'],
																		stderr=subprocess.STDOUT)
			print out
	except subprocess.CalledProcessError as e:
			print 'Error seeding layer:', layer
			print 'e.returncode:', e.returncode
			print 'e.cmd:', e.cmd
			print 'e.output:', e.output

if __name__ == "__main__":

	# Get lulc layers uploaded within the past 2 days
	lastday = datetime.now() - timedelta(days=2)
	layers = Layer.objects.filter(Q(name__iregex=r'parmap') & \
	Q(upload_session__date__gte=lastday))

	total = len(layers)
	print 'Updating', total, 'layers!'

	# Update metadata
	counter = 0
	start_time = datetime.now()
	print layers
	for layer in layers:
		print '#' * 40

		seed_layers(layer)

		counter += 1
		duration = datetime.now() - start_time
		total_time = duration.total_seconds() * total / float(counter)
		print counter, '/', total, 'ETA:', start_time + timedelta(seconds=total_time)
