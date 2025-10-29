@echo off
echo ============================
echo =	Building Python to EXE  =
echo ============================
echo.
echo 1. Checking Python installation...
python --version
if errorlevel 1 (
	echo python isn't installed
	set /p "choice=Install Python? (Y/n): "
	if /i "%choice%" == "y" (
		start "https://python.org/downloads/"
		echo python.org opened
		)
		else (
			echo exiting... 
			timeout /t 3
			exit
		)
)
echo. 
echo 2. Cheking PyInstaller installation...
pyinstaller --version
if errorlevel 1 (
	echo PyInstaller isn't installed
	set /p "choice=Install PyInstaller? (Y/n): "
	if /i "%choice%" == "y" (
		pip install PyInstaller
		)
		else (
			echo exiting... 
			timeout /t 3
			exit
		)
)
echo.
echo 3. Building EXE file...
set /p "choice1=Input Python file name (without .py): "
set /p "choice2=Input output EXE file name: "
echo Building...

pyinstaller --onefile --windowed --name "%choice2%" --clean --distpath . --workpath temp --specpath temp "%choice1%.py"

rmdir /s /q "temp"

echo.
echo.
powershell -Command "Write-Host 'Build complete!' -ForegroundColor Green"
echo.
pause