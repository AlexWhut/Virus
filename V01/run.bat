@echo off
setlocal enabledelayedexpansion
title Instalador y ejecutor del proyecto (modo prueba)

echo ==============================
echo Iniciando instalacion y ejecucion...
echo ==============================

REM --- Obtener carpeta del script ---
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
echo [INFO] Directorio del script: "%SCRIPT_DIR%"
echo.

REM === Validar si Python 3.11.5 ya está instalado ===
set "PYTHON_VERSION=3.11.5"
set "PYTHON_FOUND="

for /f "delims=" %%p in ('where python 2^>nul') do (
    for /f "delims=" %%v in ('"%%p" --version 2^>nul') do (
        echo %%v | findstr /C:"Python %PYTHON_VERSION%" >nul
        if !errorlevel! == 0 (
            set "PYTHON_FOUND=%%p"
        )
    )
)

REM --- Si no está instalado, ejecutar instalador local (modo visible para prueba) ---
if not defined PYTHON_FOUND (
    echo [INFO] Python %PYTHON_VERSION% no está instalado. Ejecutando instalador en modo visible para prueba...
    if exist "%SCRIPT_DIR%\python-3.11.5-amd64.exe" (
        "%SCRIPT_DIR%\python-3.11.5-amd64.exe"
        echo [INFO] Por favor, instala Python manualmente y asegúrate de marcar "Add Python to PATH".
        pause
    ) else (
        echo [ERROR] No se encontró el instalador python-3.11.5-amd64.exe en la carpeta.
        pause
        exit /b
    )
)

REM --- Reintentar detección Python en PATH ---
set "PYTHON_FOUND="
for /f "delims=" %%p in ('where python 2^>nul') do (
    for /f "delims=" %%v in ('"%%p" --version 2^>nul') do (
        echo %%v | findstr /C:"Python %PYTHON_VERSION%" >nul
        if !errorlevel! == 0 (
            set "PYTHON_FOUND=%%p"
        )
    )
)

REM --- Buscar en Program Files ---
if not defined PYTHON_FOUND if exist "%ProgramFiles%\Python311\python.exe" (
    set "PYTHON_FOUND=%ProgramFiles%\Python311\python.exe"
)

REM --- Buscar en LocalAppData ---
if not defined PYTHON_FOUND if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PYTHON_FOUND=%LocalAppData%\Programs\Python\Python311\python.exe"
)

if not defined PYTHON_FOUND (
    echo [ERROR] No se pudo detectar Python %PYTHON_VERSION% tras la instalación.
    pause
    exit /b
)
echo [OK] Python %PYTHON_VERSION% encontrado en: %PYTHON_FOUND%
echo.

REM === Verificar que pip esté disponible ===
echo [INFO] Verificando pip...
"%PYTHON_FOUND%" -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] pip no encontrado. Instalando pip...
    "%PYTHON_FOUND%" -m ensurepip --upgrade >nul 2>&1
)

REM === Instalar dependencias ===
echo [INFO] Instalando dependencias...
"%PYTHON_FOUND%" -m pip install --upgrade pip >nul 2>&1
"%PYTHON_FOUND%" -m pip install PyQt5 >nul 2>&1
echo [OK] Dependencias instaladas o ya presentes.
echo.

REM === Verificar Git ===
for /f "delims=" %%g in ('where git 2^>nul') do set "GIT_FOUND=%%g"

if not defined GIT_FOUND (
    echo [INFO] Git no está instalado. Buscando instalador local...
    if exist "%SCRIPT_DIR%\Git-*.exe" (
        for %%f in ("%SCRIPT_DIR%\Git-*.exe") do (
            echo [INFO] Instalando Git desde: %%~nxf
            start /wait "" "%%~f" /VERYSILENT /NORESTART
        )
    ) else (
        echo [ERROR] No se encontró instalador de Git en la carpeta.
        pause
        exit /b
    )
)

REM --- Verificar Git nuevamente ---
for /f "delims=" %%g in ('where git 2^>nul') do set "GIT_FOUND=%%g"

if not defined GIT_FOUND (
    echo [ERROR] Git no se pudo instalar o no está en PATH.
    pause
    exit /b
)
echo [OK] Git encontrado en: %GIT_FOUND%
echo.

REM === Clonar repositorio ===
set "REPO_URL=https://github.com/AlexWhut/Virus.git"
set "REPO_FOLDER=Virus"
set "REPO_PATH=%USERPROFILE%\Desktop\%REPO_FOLDER%"

if exist "%REPO_PATH%" (
    echo [INFO] El repositorio ya existe. Borrando para clonar limpio...
    rmdir /s /q "%REPO_PATH%"
)

echo [INFO] Clonando repositorio en el escritorio...
"%GIT_FOUND%" clone "%REPO_URL%" "%REPO_PATH%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Error al clonar el repositorio.
    pause
    exit /b
)
echo [OK] Repositorio clonado exitosamente.
echo.

REM === Ejecutar main.py ===
if exist "%REPO_PATH%\main.py" (
    echo [INFO] Ejecutando main.py...
    pushd "%REPO_PATH%" >nul
    "%PYTHON_FOUND%" main.py
    popd >nul
) else (
    echo [ERROR] No se encontró main.py en "%REPO_PATH%"
)

echo.
pause
