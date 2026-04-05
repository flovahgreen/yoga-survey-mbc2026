import sys
import os

# 프로젝트 경로 추가 (PythonAnywhere에서 사용)
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from server import app as application
