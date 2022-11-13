import os

from src.Version import VERSION

cmd = r"python -m nuitka --onefile --follow-imports --windows-icon-from-ico=src/static/images/icon.ico " \
      r"--output-dir=build .\src\main.py"

# dll_env = ';{}'.format(r"F:\codes\pyfiles-New\日程显示\venv\Lib\site-packages\pygame")
# os.environ['path'] += dll_env

print(cmd)
os.system(cmd)
