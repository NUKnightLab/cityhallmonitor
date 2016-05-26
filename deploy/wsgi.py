import os
import site
import sys

#site.addsitedir('/home/apps/env/cityhallmonitor/lib/python2.7/site-packages')
#sys.path.append('/home/apps/sites/cityhallmonitor')
sys.stdout = sys.stderr

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
