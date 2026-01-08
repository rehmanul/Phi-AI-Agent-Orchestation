# How to Launch Investment Sales BD System

## Quick Start (Recommended)

### Step 1: Navigate to the System Directory
```
C:\Users\phi3t\12.20 dash\1.5.2026\investment-sales-bd
```

### Step 2: Double-Click the Batch File
**Double-click:** `START_SYSTEM.bat`

This will:
- ✅ Start the backend API on port 8001
- ✅ Start the frontend on port 3001
- ✅ Open your browser to http://localhost:3001

### Step 3: Wait for Servers to Start
- Backend window will show "Uvicorn running on..."
- Frontend window will show "Ready on http://localhost:3001"
- Browser will automatically open

## File Path

```
📁 C:\Users\phi3t\12.20 dash\1.5.2026\investment-sales-bd\
   └── 📄 START_SYSTEM.bat  ← Double-click this file
```

## What Happens When You Run It

1. **Two command windows open:**
   - "BD Backend" - Python FastAPI server
   - "BD Frontend" - Next.js development server

2. **Browser automatically opens:**
   - URL: http://localhost:3001
   - Shows the Investment Sales BD System homepage

3. **System is ready to use:**
   - All pages are accessible
   - API endpoints are available
   - Full functionality enabled

## Access URLs

After launching:

- **Frontend (Main Application)**: http://localhost:3001
- **Backend API Documentation**: http://localhost:8001/docs
- **Backend Health Check**: http://localhost:8001/health

## Manual Launch (Alternative)

If you prefer to start servers manually:

### Terminal 1 - Backend:
```batch
cd "C:\Users\phi3t\12.20 dash\1.5.2026\investment-sales-bd"
python -m api.main
```

### Terminal 2 - Frontend:
```batch
cd "C:\Users\phi3t\12.20 dash\1.5.2026\investment-sales-bd\frontend"
npm run dev
```

Then open: http://localhost:3001

## Troubleshooting

### Port Already in Use? ✅ FIXED
**The batch file now automatically handles this!**

- The `START_SYSTEM.bat` file will automatically detect and kill processes on ports 8001 and 3001 before starting
- If a process can't be killed automatically, Next.js will auto-select the next available port
- Check the Frontend window to see which port it actually started on if different from 3001

**Manual Fix (if automatic doesn't work):**
- Find what's using a port: `netstat -ano | findstr ":3001"`
- Kill a process: `taskkill /F /PID <process_id>`

### Servers Won't Start?
1. Make sure Python is installed: `python --version`
2. Make sure Node.js is installed: `node --version`
3. Install backend dependencies: `pip install -r requirements.txt`
4. Install frontend dependencies: `cd frontend && npm install`

### Browser Doesn't Open?
- Manually navigate to: http://localhost:3001

## Stopping the System

1. Close both command windows (BD Backend and BD Frontend)
2. Or press `Ctrl+C` in each window to stop the servers

## System Status

After launching, you can verify everything is working:

1. **Check Backend**: Visit http://localhost:8001/health
   - Should show: `{"status":"healthy","service":"investment-sales-bd-api"}`

2. **Check Frontend**: Visit http://localhost:3001
   - Should show the homepage with three navigation cards

3. **Check API Docs**: Visit http://localhost:8001/docs
   - Should show Swagger UI with all available endpoints

## Summary

**To launch the system:**

1. Navigate to: `C:\Users\phi3t\12.20 dash\1.5.2026\investment-sales-bd`
2. Double-click: **START_SYSTEM.bat**
3. Wait for browser to open
4. Start using the system!

That's it! 🚀
