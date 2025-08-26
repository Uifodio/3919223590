#!/bin/bash

# Super File Manager - Build Script for Linux/macOS
# This script provides detailed logging and full automation

# Set script to exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Create log file with timestamp
LOG_FILE="build_log_$(date +%Y%m%d_%H%M%S).txt"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check error and exit
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: $1 failed${NC}"
        log "ERROR: $1 failed"
        exit 1
    fi
}

# Clear screen and show header
clear
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Super File Manager - Build Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${CYAN}Build started at: $(date)${NC}"
echo -e "${CYAN}Log file: $LOG_FILE${NC}"
echo

# Initialize log file
log "Build script started"
log "Operating system: $(uname -s)"
log "Architecture: $(uname -m)"

# Step 1: Check Node.js installation
echo -e "${YELLOW}[1/8] Checking Node.js installation...${NC}"
log "[1/8] Checking Node.js installation..."

if ! command_exists node; then
    echo -e "${RED}ERROR: Node.js is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Node.js from https://nodejs.org/${NC}"
    log "ERROR: Node.js not found"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js version: $NODE_VERSION${NC}"
log "✓ Node.js version: $NODE_VERSION"

# Step 1: Check npm installation
echo -e "${YELLOW}[1/8] Checking npm installation...${NC}"
log "[1/8] Checking npm installation..."

if ! command_exists npm; then
    echo -e "${RED}ERROR: npm is not available${NC}"
    log "ERROR: npm not found"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm version: $NPM_VERSION${NC}"
log "✓ npm version: $NPM_VERSION"

# Step 1: Check Git installation (optional)
echo -e "${YELLOW}[1/8] Checking Git installation...${NC}"
log "[1/8] Checking Git installation..."

if command_exists git; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✓ Git version: $GIT_VERSION${NC}"
    log "✓ Git version: $GIT_VERSION"
else
    echo -e "${YELLOW}⚠ Git not found (optional)${NC}"
    log "⚠ Git not found (optional)"
fi

# Step 2: Check project structure
echo -e "${YELLOW}[2/8] Checking project structure...${NC}"
log "[2/8] Checking project structure..."

if [ ! -f "package.json" ]; then
    echo -e "${RED}ERROR: package.json not found. Please run this script from the project root directory.${NC}"
    log "ERROR: package.json not found"
    exit 1
fi

if [ ! -d "src" ]; then
    echo -e "${RED}ERROR: src directory not found. Please run this script from the project root directory.${NC}"
    log "ERROR: src directory not found"
    exit 1
fi

echo -e "${GREEN}✓ Project structure verified${NC}"
log "✓ Project structure verified"

# Step 3: Clean previous builds
echo -e "${YELLOW}[3/8] Cleaning previous builds...${NC}"
log "[3/8] Cleaning previous builds..."

if [ -d "dist" ]; then
    echo -e "${CYAN}Removing dist directory...${NC}"
    rm -rf "dist"
    log "Removed dist directory"
fi

if [ -d "node_modules" ]; then
    echo -e "${CYAN}Removing node_modules directory...${NC}"
    rm -rf "node_modules"
    log "Removed node_modules directory"
fi

if [ -f "package-lock.json" ]; then
    echo -e "${CYAN}Removing package-lock.json...${NC}"
    rm -f "package-lock.json"
    log "Removed package-lock.json"
fi

echo -e "${GREEN}✓ Cleanup completed${NC}"
log "✓ Cleanup completed"

# Step 4: Install dependencies
echo -e "${YELLOW}[4/8] Installing dependencies...${NC}"
log "[4/8] Installing dependencies..."
echo -e "${CYAN}Running: npm install${NC}"
log "Running: npm install"
npm install --verbose >> "$LOG_FILE" 2>&1
check_error "npm install"

echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
log "✓ Dependencies installed successfully"

# Step 5: Verify critical dependencies
echo -e "${YELLOW}[5/8] Verifying critical dependencies...${NC}"
log "[5/8] Verifying critical dependencies..."

if [ ! -d "node_modules/electron" ]; then
    echo -e "${RED}ERROR: Electron not found in node_modules${NC}"
    log "ERROR: Electron not found"
    exit 1
fi

if [ ! -d "node_modules/react" ]; then
    echo -e "${RED}ERROR: React not found in node_modules${NC}"
    log "ERROR: React not found"
    exit 1
fi

if [ ! -d "node_modules/@monaco-editor/react" ]; then
    echo -e "${RED}ERROR: Monaco Editor not found in node_modules${NC}"
    log "ERROR: Monaco Editor not found"
    exit 1
fi

echo -e "${GREEN}✓ Critical dependencies verified${NC}"
log "✓ Critical dependencies verified"

# Step 6: Build React application
echo -e "${YELLOW}[6/8] Building React application...${NC}"
log "[6/8] Building React application..."
echo -e "${CYAN}Running: npm run build${NC}"
log "Running: npm run build"
npm run build >> "$LOG_FILE" 2>&1
check_error "npm run build"

if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}ERROR: Build output not found. Check the log file for details.${NC}"
    log "ERROR: Build output not found"
    exit 1
fi

echo -e "${GREEN}✓ React application built successfully${NC}"
log "✓ React application built successfully"

# Step 7: Build Electron application
echo -e "${YELLOW}[7/8] Building Electron application...${NC}"
log "[7/8] Building Electron application..."
echo -e "${CYAN}Running: npm run build:electron${NC}"
log "Running: npm run build:electron"
npm run build:electron >> "$LOG_FILE" 2>&1
check_error "npm run build:electron"

# Step 8: Check for build output
echo -e "${YELLOW}[8/8] Verifying build output...${NC}"
log "[8/8] Verifying build output..."

BUILD_FOUND=0

# Check for different build outputs based on platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    if ls dist/*.exe 1> /dev/null 2>&1; then
        echo -e "${GREEN}✓ Windows installer found${NC}"
        log "✓ Windows installer found"
        BUILD_FOUND=1
    fi
    if [ -d "dist/win-unpacked" ]; then
        echo -e "${GREEN}✓ Windows unpacked build found${NC}"
        log "✓ Windows unpacked build found"
        BUILD_FOUND=1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ls dist/*.dmg 1> /dev/null 2>&1; then
        echo -e "${GREEN}✓ macOS DMG found${NC}"
        log "✓ macOS DMG found"
        BUILD_FOUND=1
    fi
    if [ -d "dist/mac" ]; then
        echo -e "${GREEN}✓ macOS unpacked build found${NC}"
        log "✓ macOS unpacked build found"
        BUILD_FOUND=1
    fi
else
    # Linux
    if ls dist/*.AppImage 1> /dev/null 2>&1; then
        echo -e "${GREEN}✓ Linux AppImage found${NC}"
        log "✓ Linux AppImage found"
        BUILD_FOUND=1
    fi
    if [ -d "dist/linux-unpacked" ]; then
        echo -e "${GREEN}✓ Linux unpacked build found${NC}"
        log "✓ Linux unpacked build found"
        BUILD_FOUND=1
    fi
fi

if [ $BUILD_FOUND -eq 0 ]; then
    echo -e "${RED}ERROR: No build output found. Check the log file for details.${NC}"
    log "ERROR: No build output found"
    exit 1
fi

# Display build summary
echo
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BUILD COMPLETED SUCCESSFULLY!${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo -e "${GREEN}✓ Node.js: $NODE_VERSION${NC}"
echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"
echo -e "${GREEN}✓ Dependencies: Installed${NC}"
echo -e "${GREEN}✓ React Build: Completed${NC}"
echo -e "${GREEN}✓ Electron Build: Completed${NC}"
echo -e "${GREEN}✓ Build Output: Found${NC}"
echo
echo -e "${CYAN}Build artifacts are in the 'dist' directory${NC}"
echo -e "${CYAN}Log file: $LOG_FILE${NC}"
echo

# List build outputs
echo -e "${YELLOW}Build outputs found:${NC}"
if [ -d "dist" ]; then
    ls -la dist/ | while read line; do
        echo -e "${WHITE}  $line${NC}"
    done
else
    echo -e "${WHITE}  (No files found)${NC}"
fi

echo
echo -e "${MAGENTA}Press Enter to open the dist folder...${NC}"
read

# Open dist folder
if [ -d "dist" ]; then
    echo -e "${CYAN}Opening dist folder...${NC}"
    if command_exists xdg-open; then
        xdg-open dist
    elif command_exists open; then
        open dist
    else
        echo -e "${YELLOW}Could not automatically open dist folder${NC}"
    fi
fi

echo -e "${GREEN}Build script completed successfully!${NC}"
log "Build script completed successfully!"
echo -e "${CYAN}Log file saved as: $LOG_FILE${NC}"
echo