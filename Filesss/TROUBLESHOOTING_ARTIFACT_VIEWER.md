# Troubleshooting: Artifact Viewer Shows 0 Artifacts

## Quick Fix

**If you're seeing "0 Total Artifacts" and "Server: Checking...":**

1. **Open Browser Console (F12)**
   - Look for error messages
   - Check if `artifactsData` is loading

2. **Check Server is Running:**
   - Make sure the review server is running on port 8080
   - Terminal should show: `Uvicorn running on http://0.0.0.0:8080`

3. **Hard Refresh Browser:**
   - Press **Ctrl+F5** (or Cmd+Shift+R on Mac)
   - This clears cache and reloads everything

4. **Check Console Logs:**
   - You should see: `=== Initializing Artifact Viewer ===`
   - Then: `ArtifactsData structure: { categories: [...], ... }`
   - Then: `Stats updated: { total: 104, ... }`

---

## Common Issues

### Issue 1: "Server: Checking..." Never Changes

**Problem:** Server isn't responding or wrong port

**Fix:**
1. Check server is running: Look at terminal window
2. Verify port 8080 is correct in terminal output
3. Try manually: Open `http://localhost:8080/api/health` in browser
4. Should see: `{"status":"healthy",...}`

### Issue 2: Stats Show 0 But Embedded Data Exists

**Problem:** Stats calculation not running or DOM not ready

**Fix:**
1. Open browser console (F12)
2. Type: `artifactsData`
3. You should see an object with arrays
4. Type: `Object.keys(artifactsData)`
5. Should show: `['intelligence', 'drafting', 'execution', ...]`
6. Type: `artifactsData.intelligence.length`
7. Should show a number > 0

### Issue 3: API Endpoint Returns 404

**Problem:** `/api/v1/artifacts/index` not found

**Fix:**
1. Restart the review server (Ctrl+C, then run `START_REVIEW_SERVER.bat` again)
2. The endpoint was just added, needs server restart

### Issue 4: Embedded Data Structure Wrong

**Problem:** `artifactsData` exists but has wrong structure

**Fix:**
1. Check in console: `typeof artifactsData` → should be `"object"`
2. Check: `Array.isArray(artifactsData.intelligence)` → should be `true`
3. If not, regenerate the index:
   ```powershell
   cd agent-orchestrator
   python scripts/temporal__generate_artifact_index.py
   ```

---

## Step-by-Step Debugging

### Step 1: Check Server Status

In browser console (F12), run:
```javascript
fetch('http://localhost:8080/api/health')
  .then(r => r.json())
  .then(d => console.log('Server health:', d))
  .catch(e => console.error('Server not responding:', e));
```

**Expected:** `{status: "healthy", ...}`  
**If error:** Server isn't running

### Step 2: Check Artifacts Endpoint

```javascript
fetch('http://localhost:8080/api/v1/artifacts/index')
  .then(r => r.json())
  .then(d => {
    console.log('Total artifacts:', d._meta?.total_artifacts);
    console.log('Categories:', Object.keys(d.artifacts || {}));
  })
  .catch(e => console.error('Endpoint error:', e));
```

**Expected:** `{_meta: {total_artifacts: 104, ...}, artifacts: {...}}`  
**If 404:** Restart server (endpoint was just added)

### Step 3: Check Embedded Data

```javascript
console.log('Embedded data:', {
  type: typeof artifactsData,
  categories: Object.keys(artifactsData || {}),
  intelligence: artifactsData?.intelligence?.length || 0,
  drafting: artifactsData?.drafting?.length || 0
});
```

**Expected:** Object with arrays containing artifacts  
**If wrong:** Regenerate index file

### Step 4: Force Stats Update

```javascript
updateStats();
```

This should immediately update the counts if data exists.

---

## Manual Fix: Regenerate Index

If embedded data is corrupted or missing:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python scripts/temporal__generate_artifact_index.py
```

This regenerates:
- `artifacts/ARTIFACT_INDEX.html` (with embedded data)
- `artifacts/ARTIFACT_INDEX.json` (if script creates it)

Then refresh browser (Ctrl+F5).

---

## Still Not Working?

**Check these:**

1. ✅ Server is running on port 8080
2. ✅ Browser console shows no JavaScript errors
3. ✅ `/api/health` endpoint responds
4. ✅ `/api/v1/artifacts/index` endpoint exists (check after restarting server)
5. ✅ `artifactsData` object exists in console
6. ✅ Embedded data has arrays with length > 0

**If all check out but still shows 0:**
- Try a different browser
- Clear browser cache completely
- Check if browser extensions are blocking JavaScript
