#!/usr/bin/env python3
"""
Setup script for The Last Neuron project.
This script helps set up the development environment.
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and check:
        print(result.stderr)
    return result


def generate_secret_key():
    """Generate a Django secret key."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))


def generate_encryption_key():
    """Generate a 32-byte encryption key."""
    return secrets.token_urlsafe(32)[:32]


def create_env_file():
    """Create .env file with default values."""
    env_file = Path('.env')
    if env_file.exists():
        print(".env file already exists. Skipping creation.")
        return

    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    env_content = f"""# Environment Configuration for The Last Neuron

# Django Settings
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
POSTGRES_DB=the_last_neuron
POSTGRES_USER=postgres
POSTGRES_PASSWORD=devpassword123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# Encryption Settings
ENCRYPTION_KEY={encryption_key}

# Machine Learning Settings
PERSONALITY_MODEL_RETRAIN_HOURS=72
RL_LEARNING_RATE=0.001
RL_BATCH_SIZE=64

# Email Configuration (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Development Settings
DJANGO_SETTINGS_MODULE=config.settings.development
"""

    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default configuration")


def setup_python_environment():
    """Set up Python virtual environment and install dependencies."""
    print("Setting up Python environment...")
    
    # Check if virtual environment exists
    if not Path('venv').exists():
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine the correct pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    run_command(f"{pip_path} install --upgrade pip")
    
    # Install dependencies
    run_command(f"{pip_path} install -r requirements.txt")
    
    # Install spaCy model
    run_command(f"{python_path} -m spacy download en_core_web_sm", check=False)
    
    print("✅ Python environment setup complete")


def setup_database():
    """Run database migrations."""
    print("Setting up database...")
    
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    # Run migrations
    run_command(f"{python_path} manage.py makemigrations")
    run_command(f"{python_path} manage.py migrate")
    
    print("✅ Database setup complete")


def create_superuser():
    """Create a Django superuser."""
    print("Creating superuser...")
    
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    print("Please create a superuser account:")
    run_command(f"{python_path} manage.py createsuperuser")
    
    print("✅ Superuser created")


def collect_static():
    """Collect static files."""
    print("Collecting static files...")
    
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    run_command(f"{python_path} manage.py collectstatic --noinput")
    print("✅ Static files collected")


def setup_directories():
    """Create necessary directories."""
    directories = ['logs', 'media', 'staticfiles', 'models']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")


def check_system_requirements():
    """Check if system requirements are met."""
    print("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    # Check if pip is available
    try:
        run_command("pip --version")
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        sys.exit(1)
    
    print("✅ System requirements check passed")


def main():
    """Main setup function."""
    print("🧠 The Last Neuron - Setup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    try:
        # Run setup steps
        check_system_requirements()
        setup_directories()
        create_env_file()
        setup_python_environment()
        setup_database()
        collect_static()
        
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Create a superuser account:")
        
        if sys.platform == "win32":
            print("   venv\\Scripts\\python manage.py createsuperuser")
        else:
            print("   venv/bin/python manage.py createsuperuser")
        
        print("\n2. Start the development server:")
        
        if sys.platform == "win32":
            print("   venv\\Scripts\\python manage.py runserver")
        else:
            print("   venv/bin/python manage.py runserver")
        
        print("\n3. In separate terminals, start Celery:")
        
        if sys.platform == "win32":
            print("   venv\\Scripts\\celery -A config worker -l info")
            print("   venv\\Scripts\\celery -A config beat -l info")
        else:
            print("   venv/bin/celery -A config worker -l info")
            print("   venv/bin/celery -A config beat -l info")
        
        print("\n4. Visit http://localhost:8000 to see The Last Neuron!")
        print("\n5. Admin panel: http://localhost:8000/admin")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
