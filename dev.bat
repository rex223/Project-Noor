@echo off
REM Development helper script for The Last Neuron (Windows)

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="run" goto run
if "%1"=="migrate" goto migrate
if "%1"=="shell" goto shell
if "%1"=="test" goto test
if "%1"=="celery" goto celery
if "%1"=="beat" goto beat
if "%1"=="collect" goto collect
if "%1"=="super" goto super
goto help

:help
echo.
echo 🧠 The Last Neuron - Development Helper
echo =====================================
echo.
echo Available commands:
echo   setup    - Run initial project setup
echo   run      - Start development server
echo   migrate  - Run database migrations
echo   shell    - Open Django shell
echo   test     - Run tests
echo   celery   - Start Celery worker
echo   beat     - Start Celery beat scheduler
echo   collect  - Collect static files
echo   super    - Create superuser
echo   help     - Show this help message
echo.
goto end

:setup
echo Setting up The Last Neuron...
python setup.py
goto end

:run
echo Starting development server...
venv\Scripts\python manage.py runserver
goto end

:migrate
echo Running migrations...
venv\Scripts\python manage.py makemigrations
venv\Scripts\python manage.py migrate
goto end

:shell
echo Opening Django shell...
venv\Scripts\python manage.py shell
goto end

:test
echo Running tests...
venv\Scripts\python manage.py test
goto end

:celery
echo Starting Celery worker...
venv\Scripts\celery -A config worker -l info
goto end

:beat
echo Starting Celery beat scheduler...
venv\Scripts\celery -A config beat -l info
goto end

:collect
echo Collecting static files...
venv\Scripts\python manage.py collectstatic --noinput
goto end

:super
echo Creating superuser...
venv\Scripts\python manage.py createsuperuser
goto end

:end
