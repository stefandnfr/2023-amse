import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from data.utils import saveCSVLocally,removeOldDBIfExists
from data.pull_fluege_db import convertCSVToSQL
from main import pipeline
