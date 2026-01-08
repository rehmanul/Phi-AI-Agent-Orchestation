# 🚀 Quick Launch Guide

## Double-Click to Start!

**Just double-click:** `LAUNCH.bat`

That's it! The system will:
- ✅ Check prerequisites
- ✅ Start backend server
- ✅ Start frontend server  
- ✅ Open your browser automatically

---

## Available Batch Files

### `LAUNCH.bat` ⭐ (Recommended)
**One-click launch** - Starts everything with progress indicators

**What it does:**
1. Checks Python & Node.js
2. Installs dependencies if needed
3. Starts backend (port 8002)
4. Starts frontend (port 3000)
5. Opens browser to http://localhost:3000

**Output:**
- Shows progress steps: `[1/5]`, `[2/5]`, etc.
- Opens two windows (backend green, frontend red)
- Opens browser automatically

---

### `START_SYSTEM.bat`
Same as LAUNCH.bat but with more verbose output

---

### `START_BACKEND_ONLY.bat`
Starts only the backend API server
- Useful for API development
- Backend runs on port 8002
- API docs at http://localhost:8002/docs

---

### `START_FRONTEND_ONLY.bat`
Starts only the frontend
- Use when backend is already running
- Frontend runs on port 3000

---

### `STOP_SYSTEM.bat`
Stops all running servers
- Kills processes on ports 8002 and 3000
- Closes Node.js processes
- Use this if ports are in use

---

## First Time Setup

**Prerequisites:**
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))

**Steps:**
1. Double-click `LAUNCH.bat`
2. Wait for dependencies to install (first time only)
3. Browser opens automatically (~15 seconds)
4. Start using the system!

---

## What You'll See

### When you run LAUNCH.bat:

```
╔═══════════════════════════════════════════════════════════╗
║     RISK MANAGEMENT SYSTEM - QUICK LAUNCH                 ║
╚═══════════════════════════════════════════════════════════╝

[1/5] Checking prerequisites...
   ✓ Python found
   ✓ Node.js found

[2/5] Checking backend dependencies...
   ✓ Backend ready

[3/5] Starting backend server...
   ✓ Backend starting...

[4/5] Starting frontend server...
   ✓ Frontend starting...

[5/5] Opening browser...
   ✓ Browser opening...

╔═══════════════════════════════════════════════════════════╗
║                    ✅ SYSTEM STARTED!                      ║
╚═══════════════════════════════════════════════════════════╝
```

### Two Windows Will Open:

**Window 1: Backend Server (Green)**
```
╔════════════════════════════════════════════╗
║   RISK MANAGEMENT - BACKEND SERVER          ║
╚════════════════════════════════════════════╝

Running on: http://localhost:8002
API Docs:  http://localhost:8002/docs
```

**Window 2: Frontend Server (Red)**
```
╔════════════════════════════════════════════╗
║   RISK MANAGEMENT - FRONTEND SERVER         ║
╚════════════════════════════════════════════╝

Running on: http://localhost:3000
```

---

## Troubleshooting

### "Python not found"
**Solution:** Install Python from python.org and make sure to check "Add Python to PATH"

### "Node.js not found"  
**Solution:** Install Node.js from nodejs.org

### "Port 8002 already in use"
**Solution:** Run `STOP_SYSTEM.bat` first, then try again

### "Port 3000 already in use"
**Solution:** Close any other apps using port 3000, or run `STOP_SYSTEM.bat`

### Frontend won't start
**Solution:** 
1. Run `STOP_SYSTEM.bat`
2. Delete `frontend/node_modules` folder
3. Run `LAUNCH.bat` again (it will reinstall)

---

## Manual Start (Alternative)

If you prefer to start manually:

**Terminal 1:**
```bash
cd risk-management-system
python -m api.main
```

**Terminal 2:**
```bash
cd risk-management-system/frontend
npm run dev
```

Then open: http://localhost:3000

---

## System URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8002
- **API Documentation:** http://localhost:8002/docs
- **Health Check:** http://localhost:8002/health

---

## Need Help?

- See `QUICK_START.md` for detailed documentation
- See `IMPLEMENTATION_COMPLETE.md` for technical details
- Run `python verify_implementation.py` to check system status

---

**Ready to start?** Just double-click `LAUNCH.bat`! 🚀
