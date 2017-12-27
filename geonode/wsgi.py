#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os

activate_this = '/home/geonode/.virtualenvs/geonode-python2.7.13/bin/activate_this.py'
if os.path.isfile(activate_this):
    execfile(activate_this, dict(__file__=activate_this))
else:
    raise FileNotFoundError("Cannot find virtualenv activate file [{0}]".format(activate_this))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

application = get_wsgi_application()
