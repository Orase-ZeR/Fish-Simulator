@echo off
::===============================================================
::               Script d'installation Python                 
::===============================================================
:: Auteur : Gaetan F.                                          
:: Version: 1.1                                                
::                                                              
:: - Vérifie Python >= 3.11                                    
:: - Tente d'installer pip si absent                            
:: - Installe les librairies depuis requirements.txt           
::                                                              
:: /!\ En cas d'erreur, vérifier la version de Python et pip.  
::===============================================================

setlocal enabledelayedexpansion

:: ---- Variables ----
set "TIMEOUT_SECONDS=30"

:: ---- Couleurs ----
color 0A

:: ---- Affichage du header ----
echo ===============================================================
echo        SCRIPT D'INSTALLATION PYTHON & REQUIREMENTS
echo ===============================================================
echo.
echo Appuyez sur une touche pour lancer l'installation...
pause >nul

:: ---- Détecter Python ----
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
    echo [ERREUR] Python non trouve dans le PATH.
    echo Installer Python 3.11+ : https://www.python.org/downloads/
    goto :wait_and_exit_error
)

:: ---- Vérifier version Python ----
for /f "tokens=2 delims= " %%i in ('%PYEXEC% --version 2^>^&1') do set "PYVER=%%i"
if not defined PYVER (
    echo [ERREUR] Impossible de determiner la version de Python.
    goto :wait_and_exit_error
)

for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set "PYMAJOR=%%a"
    set "PYMINOR=%%b"
)
if not defined PYMINOR set "PYMINOR=0"

echo Python detecte : %PYEXEC% (version %PYVER%)

if %PYMAJOR% LSS 3 goto :err_ver
if %PYMAJOR% GTR 3 goto :ok_ver
if %PYMINOR% LSS 11 goto :err_ver
goto :ok_ver

:err_ver
echo [ERREUR] Python 3.11 ou superieur requis (version trouvee: %PYVER%).
goto :wait_and_exit_error

:ok_ver
:: ---- Vérifier pip ----
%PYEXEC% -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] pip introuvable, tentative d'installation via ensurepip...
    %PYEXEC% -m ensurepip --upgrade >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] Impossible d'installer pip automatiquement. Installer pip manuellement.
        goto :wait_and_exit_error
    )
    echo [INFO] Mise a jour pip, setuptools et wheel...
    %PYEXEC% -m pip install --upgrade pip setuptools wheel
)

:: ---- Installer requirements.txt ----
if exist "%CD%\requirements.txt" (
    echo [INFO] Installation depuis "%CD%\requirements.txt"...
    %PYEXEC% -m pip install -r "%CD%\requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] L'installation a echoue. Verifier le contenu de requirements.txt.
        goto :wait_and_exit_error
    )
    echo [OK] Installation terminee avec succes.
    pause
    exit /b 0
) else (
    echo [ERREUR] requirements.txt introuvable dans "%CD%".
    goto :wait_and_exit_error
)

:wait_and_exit_error
echo.
echo [ERREUR] Installation interrompue. Voir messages ci-dessus.
echo Vous pouvez appuyer sur une touche pour fermer ou attendre %TIMEOUT_SECONDS% secondes...
where choice >nul 2>&1
if %ERRORLEVEL%==0 (
    choice /n /c Y /t %TIMEOUT_SECONDS% /d Y >nul 2>&1
) else (
    timeout /t %TIMEOUT_SECONDS% /nobreak >nul 2>&1
)
exit /b 1
