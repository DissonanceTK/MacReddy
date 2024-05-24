import os
import shutil
import subprocess
import sys
import platform
import importlib.util


def is_windows():
    return sys.platform == 'win32'

def is_macos():
    return sys.platform == 'darwin'

def install_linux_dependencies():
    package_managers = {
        'apt-get': ['sudo', 'apt-get', 'install', '-y', 'xclip', 'ffmpeg', 'portaudio19-dev'],
        'pacman': ['sudo', 'pacman', '-Sy', 'xclip', 'ffmpeg', 'portaudio']
    }

    for manager, command in package_managers.items():
        try:
            subprocess.check_call(command)
            print(f"Successfully installed dependencies using {manager}")
            return
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies using {manager}: {e}")
            continue

    print("Unable to install dependencies. Please install them manually.")
    sys.exit(1)

def install_macos_dependencies():
    package_managers = {
        'brew': ['brew', 'install', 'xclip', 'ffmpeg', 'portaudio']
    }

    for manager, command in package_managers.items():
        try:
            subprocess.check_call(command)
            print(f"Successfully installed dependencies using {manager}")
            return
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies using {manager}: {e}")
            continue

    print("Unable to install dependencies. Please install them manually.")
    sys.exit(1)


def copy_file(src, dest):
    """
    Copies a file from the source path to the destination path.
    If the destination file already exists, it prompts the user for confirmation to overwrite.
    """
    if os.path.exists(dest):
        if dest == "config.py":
            should_overwrite = input(f"{dest} already exists. Do you want to overwrite it? This may be required after an update as new contents are added to the config file often.(y/n): ")
        else:
            should_overwrite = input(f"{dest} already exists. Do you want to overwrite it? (y/n): ")
        if should_overwrite.lower() != 'y':
            print(f"Skipping {dest}")
            return
    shutil.copy(src, dest)
    print(f"Copied {src} to {dest}")

def create_run_files():
    if is_windows():
        with open('run_AlwaysReddy.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('if not defined VIRTUAL_ENV (\n')
            f.write(' call venv\\Scripts\\activate.bat\n')
            f.write(')\n')
            f.write('python main.py\n')
            f.write('pause\n')
        print("Created run file")

def add_to_startup(run_file):
    if is_windows():
        confirm = input("Are you sure you want to add AlwaysReddy to startup? (y/n): ")
        if confirm.lower() != 'y':
            print("Skipping adding AlwaysReddy to startup.")
            return False

        startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        os.makedirs(startup_dir, exist_ok=True)
        startup_file = os.path.join(startup_dir, "AlwaysReddy.bat")
        with open(startup_file, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd /d \"{os.path.dirname(os.path.abspath(__file__))}\"\n")
            f.write(f"start cmd /k \"{run_file}\"\n")
        print(f"Added {run_file} to startup")

        return True
    else:
        print("Startup setup is only available for Windows.")
        return False

def remove_from_startup():
    if is_windows():
        startup_file = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "AlwaysReddy.bat")
        if os.path.exists(startup_file):
            os.remove(startup_file)
            print("Removed AlwaysReddy from startup")
        else:
            print("AlwaysReddy not found in startup")
    else:
        print("Startup setup is only available for Windows.")

def main():
    # Check if the system is Linux and install dependencies if necessary
    if is_macos():
        install_macos_dependencies()
    elif not is_windows():
        install_linux_dependencies()

    # Copy config_default.py to config.py
    copy_file('config_default.py', 'config.py')

    # Copy .env.example to .env
    copy_file('.env.example', '.env')
    print("Please open .env and enter your API keys")

    # Prompt the user to install Piper TTS
    install_piper = input("Would you like to install Piper TTS? (y/n): ").strip().lower()
    if install_piper == 'y':
        # Import the setup function from installpipertts.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        installpipertts_path = os.path.join(script_dir, 'scripts', 'installpipertts.py')
        
        spec = importlib.util.spec_from_file_location("installpipertts", installpipertts_path)
        installpipertts = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installpipertts)
        
        # Call the setup function
        installpipertts.setup_piper_tts()
    else:
        print("Piper TTS installation skipped.")

    create_run_files()

    if is_windows():
        # Ask if the user wants to add the project to startup
        add_to_startup_prompt = input("Do you want to add AlwaysReddy to startup? (y/n): ")
        if add_to_startup_prompt.lower() == 'y':
            run_file = 'run_AlwaysReddy.bat'
        else:
            print("Skipping adding AlwaysReddy to startup.")



if __name__ == "__main__":
    main()