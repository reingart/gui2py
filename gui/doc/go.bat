@echo off
echo -----------------------------------------------------------------------
echo - Generating HTML documentation                                       -
echo -----------------------------------------------------------------------

rd /s /q .\api
rd /s /q .\_build

sphinx-build -w _build/html/warnings.txt -b html -D graphviz_dot=C:\Progra~2\Graphv~1.28\bin\dot.exe . _build/html

echo -----------------------------------------------------------------------
pause 10