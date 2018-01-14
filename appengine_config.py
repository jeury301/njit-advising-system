from ferris import fix_imports
from ferris.core import settings
from google.appengine.ext import vendor

(fix_imports)
settings.load_settings()

# Add any libraries installed in the "lib" folder.
vendor.add('lib')


