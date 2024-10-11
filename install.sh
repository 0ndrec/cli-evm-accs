#!/bin/bash

set -e

# Function to display an error message and exit
function error_exit {
    echo "Error: $1" >&2
    exit 1
}

# Variables
APP_DIR="/opt/evmaccs"
VENV_POINT=".venv"
VENV_DIR="$APP_DIR/$VENV_POINT"
REPO_URL="https://github.com/0ndrec/cli-evm-accs.git"
REPO_DIR="$APP_DIR/app"
EXECUTABLE="/usr/local/bin/evmaccs"

# Check if script is run as root, else use sudo
if [[ $EUID -ne 0 ]]; then
    echo "This script requires root privileges. Attempting to use sudo..."
    if ! command -v sudo >/dev/null 2>&1; then
        error_exit "sudo is required but not installed. Please install sudo or run as root."
    fi
    exec sudo bash "$0" "$@"
fi

# Delete old application directory
if [[ -d "$APP_DIR" ]]; then
    echo "Clearing old application directory..."
    rm -rf "$APP_DIR" || error_exit "Failed to clear old application directory."
fi

# Clone the repository
if [[ ! -d "$REPO_DIR" ]]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR" || error_exit "Failed to clone repository."
fi

# Upgrade packages
apt-get update || error_exit "Failed to update package list."
sudo apt upgrade -y > /dev/null || error_exit "Failed to upgrade packages."

# Install Python3 if not installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Installing..."
    apt-get install -y python3 || error_exit "Failed to install Python3."
else
    echo "Python3 is already installed."
fi

# Install virtualenv if not installed, and pip
apt-get install -y python3-pip || error_exit "Failed to install pip."
apt-get install -y python3-venv || error_exit "Failed to install virtualenv."


# Create application directory
if [[ ! -d "$APP_DIR" ]]; then
    mkdir -p "$APP_DIR" || error_exit "Failed to create application directory at $APP_DIR."
fi

# Create virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating Python virtual environment..."
    cd "$APP_DIR" && python3 -m venv "$VENV_POINT" || error_exit "Failed to create virtual environment."
else
    echo "Virtual environment already exists at $VENV_DIR."
fi


# Activate virtual environment
if source "$VENV_DIR/bin/activate"; then
    echo "Virtual environment activated."
else
    error_exit "Failed to activate virtual environment."
fi


# Install dependencies
if [[ -f "$REPO_DIR/requirements.txt" ]]; then
    echo "Installing Python dependencies..."
    pip install -r "$REPO_DIR/requirements.txt" > /dev/null || error_exit "Failed to install dependencies."
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

# Create executable script
echo "Creating executable at $EXECUTABLE..."
cat << EOF > "$EXECUTABLE"
#!/bin/bash
source "$VENV_DIR/bin/activate"
echo "Starting evmaccs..."
python "$REPO_DIR/main.py" "\$@"
deactivate
EOF

chmod +x "$EXECUTABLE" || error_exit "Failed to make $EXECUTABLE executable."

echo "Installation complete. You can now run the application using the 'evmaccs' command."

