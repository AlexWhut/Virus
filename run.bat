@echo off
REM ==============================
REM Run Virus project (auto-update)
REM ==============================

REM Verificar si Python esta instalado
where python >nul 2>nul
if %errorlevel%==0 (
    echo Python esta instalado.
) else (
    echo Python no esta instalado. Instala Python desde https://www.python.org/downloads/
    pause
    exit
)

REM Instalar dependencias
python -m pip install --upgrade pip
python -m pip install PyQt5

REM Verificar si Git esta instalado
where git >nul 2>nul
if %errorlevel%==0 (
    echo Git esta instalado.
) else (
    echo Git no esta instalado. Instala Git desde https://git-scm.com/downloads
    pause
    exit
)

REM -----------------------------
REM Repositorio
REM -----------------------------
set REPO_URL=https://github.com/AlexWhut/Virus.git
set REPO_FOLDER=Virus

if exist "%REPO_FOLDER%" (
    echo El repositorio ya existe. Actualizando...
    cd %REPO_FOLDER%
    git pull
    cd ..
) else (
    echo Clonando repositorio...
    git clone %REPO_URL%
    if %errorlevel%==0 (
        echo Repositorio clonado exitosamente.
    ) else (
        echo Error al clonar el repositorio. Verifica la URL o tu conexion.
        pause
        exit
    )
)

REM -----------------------------
REM Ejecutar el script principal
REM -----------------------------
cd %REPO_FOLDER%
set SCRIPT_NAME=main.py
if exist "%SCRIPT_NAME%" (
    python %SCRIPT_NAME%
) else (
    echo No se encontro %SCRIPT_NAME% en %REPO_FOLDER%.
)
