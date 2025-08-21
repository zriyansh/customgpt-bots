#!/usr/bin/env python3
"""
Quick setup script for CustomGPT Teams Bot
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60 + "\n")


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def create_env_file():
    """Create .env file from example"""
    if not Path(".env").exists() and Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from .env.example")
        return True
    elif Path(".env").exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False


def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Get activation command based on OS
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    return activate_cmd


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    
    # Determine pip command
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def prompt_configuration():
    """Prompt for configuration values"""
    print_header("Bot Configuration")
    print("Please provide the following configuration values:")
    print("(Press Enter to skip and configure later in .env file)\n")
    
    config = {}
    
    # Teams configuration
    config['TEAMS_APP_ID'] = input("Microsoft App ID: ").strip()
    config['TEAMS_APP_PASSWORD'] = input("Microsoft App Password: ").strip()
    
    # CustomGPT configuration
    config['CUSTOMGPT_API_KEY'] = input("CustomGPT API Key: ").strip()
    config['CUSTOMGPT_PROJECT_ID'] = input("CustomGPT Project ID: ").strip()
    
    # Update .env file
    if any(config.values()):
        update_env_file(config)
        print("\n✅ Configuration saved to .env file")
    else:
        print("\n⚠️  No configuration provided. Please update .env file manually.")


def update_env_file(config):
    """Update .env file with provided configuration"""
    env_path = Path(".env")
    if not env_path.exists():
        return
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update values
    updated_lines = []
    for line in lines:
        updated = False
        for key, value in config.items():
            if value and line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                updated = True
                break
        if not updated:
            updated_lines.append(line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)


def create_app_package():
    """Create Teams app package"""
    print_header("Teams App Package")
    
    manifest_path = Path("deployment/manifest.json")
    if not manifest_path.exists():
        print("❌ manifest.json not found")
        return
    
    print("To create a Teams app package:")
    print("1. Update deployment/manifest.json with your App ID")
    print("2. Add app icons (color.png and outline.png)")
    print("3. Run: cd deployment && zip -r ../teams-app.zip manifest.json *.png")
    print("\nRefer to README.md for detailed instructions.")


def print_next_steps():
    """Print next steps"""
    print_header("Next Steps")
    
    print("1. Complete configuration in .env file")
    print("2. Register your bot in Azure Portal")
    print("3. Create and upload Teams app package")
    print("4. Run the bot:")
    print("   - Activate virtual environment")
    print("   - Run: python app.py")
    print("\nFor detailed instructions, see README.md")
    print("\nUseful commands:")
    print("  python app.py                    # Run the bot")
    print("  pytest                           # Run tests")
    print("  docker-compose up                # Run with Docker")
    print("  docker-compose --profile dev up  # Run with ngrok for testing")


def main():
    """Main setup function"""
    print_header("CustomGPT Teams Bot Setup")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("Please create .env file manually from .env.example")
        sys.exit(1)
    
    # Create virtual environment
    activate_cmd = create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        print(f"\nPlease activate virtual environment and install manually:")
        print(f"  {activate_cmd}")
        print(f"  pip install -r requirements.txt")
        sys.exit(1)
    
    # Prompt for configuration
    prompt_configuration()
    
    # App package instructions
    create_app_package()
    
    # Next steps
    print_next_steps()
    
    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    main()