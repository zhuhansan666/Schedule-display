from os import system

from src.Version import VERSION

cmd = r"python -m nuitka --follow-imports --output-dir=build .\src\main.py"

print(cmd)
system(cmd)
