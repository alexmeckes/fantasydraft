# Virtual Environment Setup Guide

## Quick Start (macOS/Linux)

Use the provided script:
```bash
./start_venv.sh
source venv/bin/activate
python app.py
```

## Manual Setup

### 1. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
```

**Windows:**
```cmd
python -m venv venv
```

### 2. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Once activated, you'll see `(venv)` in your terminal prompt:
```bash
pip install -r requirements.txt
```

### 4. Set API Key

**macOS/Linux:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

### 5. Run the Application

**Web Interface:**
```bash
python app.py
```

**Command Line:**
```bash
python demo.py --interactive
```

## Managing the Virtual Environment

### Check if venv is active:
Look for `(venv)` at the beginning of your terminal prompt.

### Deactivate when done:
```bash
deactivate
```

### Delete venv (if needed):
```bash
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

## Why Use a Virtual Environment?

1. **Isolation**: Keeps project dependencies separate from system Python
2. **Version Control**: Ensures everyone uses the same package versions
3. **Clean Uninstall**: Easy to remove all project dependencies
4. **No Conflicts**: Prevents package version conflicts between projects

## Troubleshooting

### "python3: command not found"
Try `python` instead of `python3`

### "Permission denied" on macOS/Linux
Make sure the script is executable:
```bash
chmod +x start_venv.sh
```

### PowerShell execution policy error on Windows
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Package installation fails
Update pip first:
```bash
pip install --upgrade pip
``` 