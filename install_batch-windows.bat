::===============================================================
::||               Script d'installation (batch)               ||
::===============================================================
::|| Fonction basiques : Détecte la présence de python et une  ||
::|| bonne version (>=3.11) ou jette une erreur.               ||
::||                                                           ||
::||         /!\ Tentera d'installer PIP si Absent             ||
::||                                                           ||
::||                                                           ||
::|| je garantis pas que ce script fonctionne et encore moins  ||
::|| le script bash qui vas avec mon batch est un peu rouillé  ||
::|| et les 3 cafés aident pas mais normalement le batch est ok||
::||                                                           ||
::|| Si ça fonctionne pas s'assurer de la version (>=3.11) et  ||
::|| installer le ./requirements.txt                           ||
::===============================================================
::||                        Gaetan F.                          ||
::===============================================================

@echo off
setlocal

REM Timeout en sec
set "TIMEOUT_SECONDS=30"

REM Détecter Python
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PYEXEC=py -3"
) else (
  where python >nul 2>&1
  if %ERRORLEVEL%==0 (
    set "PYEXEC=python"
  )
)

if not defined PYEXEC (
  echo ERREUR: Python non trouve dans le PATH.
  echo Installer Python 3.11+ : https://www.python.org/downloads/
  goto :wait_and_exit_error
)

REM Récupérer la version (ex: 3.13.7)
for /f "tokens=2 delims= " %%i in ('%PYEXEC% --version 2^>^&1') do set "PYVER=%%i"
if not defined PYVER (
  echo ERREUR: Impossible de determiner la version de Python.
  goto :wait_and_exit_error
)

for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
  set "PYMAJOR=%%a"
  set "PYMINOR=%%b"
)
if not defined PYMINOR set "PYMINOR=0"

echo Python trouve: %PYEXEC% (version %PYVER%)

REM Vérifier si la version est >= 3.11
if %PYMAJOR% LSS 3 goto :err_ver
if %PYMAJOR% GTR 3 goto :ok_ver
if %PYMINOR% LSS 11 goto :err_ver
goto :ok_ver

:err_ver
echo ERREUR: Python 3.11 ou superieur requis (version trouve: %PYVER%).
goto :wait_and_exit_error

:ok_ver
REM Vérifier pip
%PYEXEC% -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo pip introuvable pour %PYEXEC%. Tentative d'installation via ensurepip...
  %PYEXEC% -m ensurepip --upgrade >nul 2>&1
  if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Impossible d'installer pip automatiquement. Installer pip manuellement.
    goto :wait_and_exit_error
  )
  echo Mise a jour de pip/setuptools/wheel...
  %PYEXEC% -m pip install --upgrade pip setuptools wheel
)

REM Installer requirements.txt dans le cd
if exist "%CD%\requirements.txt" (
  echo Installation depuis "%CD%\requirements.txt"...
  %PYEXEC% -m pip install -r "%CD%\requirements.txt"
  if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: L'installation a echoue.
    goto :wait_and_exit_error
  )
  echo Installation terminee avec succes.
  exit /b 0
) else (
  echo ERREUR: requirements.txt introuvable dans "%CD%".
  goto :wait_and_exit_error
)

:wait_and_exit_error
echo.
echo ERREUR: voir le message ci-dessus.
echo Vous pouvez appuyer sur une touche pour fermer ou attendre %TIMEOUT_SECONDS% secondes...
where choice >nul 2>&1
if %ERRORLEVEL%==0 (
  choice /n /c Y /t %TIMEOUT_SECONDS% /d Y >nul 2>&1
) else (
  timeout /t %TIMEOUT_SECONDS% /nobreak >nul 2>&1
)
exit /b 1