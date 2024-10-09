#!/bin/bash

set -e

# Function to display an error message and exit
function error_exit {
    echo "Error: $1" >&2
    exit 1
}

# Variables
APP_DIR="/opt/cli-evm-accs"
VENV_DIR="$APP_DIR/venv"
REPO_URL="https://github.com/0ndrec/cli-evm-accs.git"
REPO_DIR="$APP_DIR/cli-evm-accs"
EXECUTABLE="/usr/local/bin/evmaccs"

# Function to install the application
function install_app {
    # Install Python3 if not installed
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python3 not found. Installing..."
        apt-get update || error_exit "Failed to update package list."
        apt-get install -y python3 python3-venv python3-pip || error_exit "Failed to install Python3."
    else
        echo "Python3 is already installed."
    fi

    # Install git if not installed
    if ! command -v git >/dev/null 2>&1; then
        echo "Git not found. Installing..."
        apt-get install -y git || error_exit "Failed to install Git."
    else
        echo "Git is already installed."
    fi

    # Create application directory
    if [[ ! -d "$APP_DIR" ]]; then
        mkdir -p "$APP_DIR" || error_exit "Failed to create application directory at $APP_DIR."
    fi

    # Create virtual environment
    if [[ ! -d "$VENV_DIR" ]]; then
        echo "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR" || error_exit "Failed to create virtual environment."
    else
        echo "Virtual environment already exists at $VENV_DIR."
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment."

    # Clone the repository
    if [[ ! -d "$REPO_DIR" ]]; then
        echo "Cloning repository..."
        git clone "$REPO_URL" "$REPO_DIR" || error_exit "Failed to clone repository."
    else
        echo "Repository already cloned at $REPO_DIR."
    fi

    # Install dependencies
    if [[ -f "$REPO_DIR/requirements.txt" ]]; then
        echo "Installing Python dependencies..."
        pip install -r "$REPO_DIR/requirements.txt" || error_exit "Failed to install dependencies."
    else
        echo "No requirements.txt found. Skipping dependency installation."
    fi

    # Create executable script
    echo "Creating executable at $EXECUTABLE..."
    cat << EOF > "$EXECUTABLE"
#!/bin/bash
source "$VENV_DIR/bin/activate"
python "$REPO_DIR/main.py" "\$@"
EOF

    chmod +x "$EXECUTABLE" || error_exit "Failed to make $EXECUTABLE executable."

    echo "Installation complete. You can now run the application using the 'evmaccs' command."
}

# Function to update the application
function update_app {
    if [[ ! -d "$REPO_DIR" ]]; then
        error_exit "Application is not installed. Please run the script without arguments to install."
    fi

    echo "Updating application..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment."

    # Navigate to repository directory
    cd "$REPO_DIR" || error_exit "Failed to navigate to repository directory."

    # Pull latest changes
    git pull || error_exit "Failed to update repository."

    # Re-install dependencies if requirements.txt has changed
    if [[ -f "requirements.txt" ]]; then
        echo "Updating Python dependencies..."
        pip install -r "requirements.txt" || error_exit "Failed to install dependencies."
    else
        echo "No requirements.txt found. Skipping dependency installation."
    fi

    echo "Application update complete."
}

# Check if script is run as root, else use sudo
if [[ $EUID -ne 0 ]]; then
    echo "This script requires root privileges. Attempting to use sudo..."
    if ! command -v sudo >/dev/null 2>&1; then
        error_exit "sudo is required but not installed. Please install sudo or run as root."
    fi
    exec sudo bash "$0" "$@"
fi

# Main script logic
if [[ "$1" == "update" ]]; then
    update_app
else
    install_app
fi
