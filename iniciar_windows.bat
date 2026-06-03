@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Transcritor de Auditoria Operacional
echo ========================================
echo.

REM --- Cria o ambiente virtual na primeira execucao ---
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Criando ambiente virtual ^(.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERRO: Python nao encontrado.
        echo Instale o Python 3.10+ em https://www.python.org/downloads/
        echo e marque a opcao "Add Python to PATH" durante a instalacao.
        echo.
        pause
        exit /b 1
    )
)

REM --- Ativa o ambiente e instala dependencias ---
call ".venv\Scripts\activate.bat"

echo [2/3] Instalando dependencias ^(pode demorar na primeira vez^)...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERRO ao instalar dependencias. Verifique sua conexao com a internet.
    echo.
    pause
    exit /b 1
)

REM --- Sobe o servidor web ---
echo [3/3] Iniciando servidor web...
echo.
echo  Abra no navegador:  http://127.0.0.1:5000
echo  Para parar o servidor: feche esta janela ou pressione CTRL+C.
echo.
python -m auditoria_relatorio.web --host 127.0.0.1 --port 5000

pause
