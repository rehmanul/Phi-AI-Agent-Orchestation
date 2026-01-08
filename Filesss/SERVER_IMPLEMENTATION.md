# Server Implementation - Port Finding Logic

## Overview

The server implementation automatically finds an available port by trying multiple ports sequentially until it finds one that's not in use.

## How It Works

### Port Finding Algorithm

1. **Start Port**: Begins checking from port 8000
2. **Port Check**: For each port, checks if it's available using socket binding
3. **Continue**: If port is in use, automatically tries the next port (8001, 8002, 8003, etc.)
4. **Max Attempts**: Tries up to 100 ports (8000-8099) before giving up
5. **Success**: Returns the first available port found

### Code Flow

```python
def find_available_port(start_port=8000, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):  # Checks if port can be bound
            return port              # Returns first available port
    return None                      # No port found after max attempts
```

### Port Availability Check

```python
def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))  # Try to bind to port
            return True                   # Port is available
        except OSError:
            return False                  # Port is in use
```

## Usage

### Method 1: Run Workflow and Server Together
```bash
START_WORKFLOW.bat
```
- Runs workflow
- Generates HTML viewer
- Starts server on first available port
- Opens browser automatically

### Method 2: Just Launch Viewer
```bash
LAUNCH_VIEWER.bat
```
- Checks for HTML viewer (generates if missing)
- Starts server on first available port
- Opens browser automatically

### Method 3: Python Direct
```bash
python start_server.py
```
- Finds available port automatically
- Starts server
- Opens browser

## Example Output

```
[INFO] Looking for available port...
[INFO] Checking ports starting from 8000...
[SKIP] Port 8000 is in use, trying next...
[SKIP] Port 8001 is in use, trying next...
[OK] Port 8002 is available
[INFO] Found available port: 8002
[SUCCESS] Server started on http://localhost:8002
[INFO] Serving directory: C:\...\agentic-coding-workflow\output
[INFO] Opening browser...
[INFO] Press Ctrl+C to stop the server
```

## Features

- ✅ **Automatic Port Finding**: No manual port configuration needed
- ✅ **Sequential Checking**: Tries ports in order (8000, 8001, 8002...)
- ✅ **Up to 100 Attempts**: Won't give up easily
- ✅ **Clear Feedback**: Shows which ports are being tried
- ✅ **Browser Auto-Open**: Automatically opens browser when server starts
- ✅ **CORS Enabled**: Allows cross-origin requests for local development

## Port Range

- **Start**: 8000
- **End**: 8099 (8000 + 100 attempts)
- **Default**: Usually finds one in first few attempts

## Error Handling

If no port is found after 100 attempts:
- Prints error message
- Exits with error code 1
- User can manually specify a different start port

## Server Features

- Serves static files from output directory
- CORS headers enabled for local development
- Handles KeyboardInterrupt gracefully
- Shows clear status messages
