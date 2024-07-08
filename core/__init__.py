from .version import __version__
import os
import importlib.util
from .processing import ProcessThread
from .log import Log
from .database import DB

# Get the directory of this script
current = os.path.dirname(os.path.abspath(__file__))

# Import address object from manage.py dynamically
manage_path = os.path.join(current, '..', 'manage.py')
spec = importlib.util.spec_from_file_location("manage", manage_path)
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)
