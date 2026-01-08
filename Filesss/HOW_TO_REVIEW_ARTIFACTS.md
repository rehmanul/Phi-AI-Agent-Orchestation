# How to Review Artifacts - Simple Guide

## The Batch File You Need

**Location:** `agent-orchestrator\START_VIEWER_SERVER.bat`

**What it does:** Starts the FastAPI server so you can use the web viewer.

---

## Step-by-Step: How to Review Artifacts

### Step 1: Start the Server

Double-click this file:
```
agent-orchestrator\START_VIEWER_SERVER.bat
```

Or if you're already in that folder, just type:
```
START_VIEWER_SERVER.bat
```

**What happens:**
- A black window (command prompt) opens
- The server starts on port 8000
- Your browser automatically opens to `http://localhost:8000/`
- **Keep that window open** - closing it stops the server

---

### Step 2: The Viewer Opens

You'll see:
- A blue header saying "Agent Orchestrator - Artifact Review Console"
- Statistics showing your artifact counts (104 total artifacts, etc.)
- A green dot saying "• Server: Online" (if everything worked)

---

### Step 3: Browse Artifacts

**By Category:**
- Click tabs at the top: "Intelligence", "Drafting", "Execution", etc.
- Each shows artifacts of that type

**By Status:**
- Click filter buttons: "All", "Unreviewed", "Approved", "Needs Revision"
- Shows artifacts filtered by their review status

**Search:**
- Type in the search box at the top
- Filters artifacts by name, path, or type

---

### Step 4: Review an Artifact

1. **Click on an artifact card** (they're in a grid layout)

2. **Expand it** (if preview is hidden):
   - Click "▼ Expand Preview" to see artifact content
   - Or click "📄 Open File" to see the full JSON

3. **Review the content:**
   - Read through the artifact
   - Check if it's correct, complete, and appropriate

4. **Make a decision:**
   - **✓ Approve** - Artifact is good to use
   - **↻ Revise** - Needs changes before approval
   - **✗ Reject** - Not suitable, don't use

5. **Fill out the review form:**
   - **Reason:** Type why you're approving/rejecting (required)
   - **Include in LLM packet:** Check if this should go to an LLM
   - **Intended Recipient:** Select who this is for (if LLM)
   - **Why sending:** Explain why you're sending it (if LLM)

6. **Submit:**
   - Click "Submit Review" button
   - The status updates immediately (you'll see a green flash)

---

### Step 5: Generate a Brief (Optional)

If you've approved artifacts and marked them for LLM:

1. **Click "Generate One-Look Brief"** (blue button at top)

2. **The brief opens in a new window:**
   - Shows all approved artifacts ready for LLM
   - Answers: What, Why, Who, How, What Exactly

3. **Save it if needed:**
   - Right-click in the brief window
   - "Save As" to download the markdown file

---

## Quick Tips

### If the server won't start:
- Make sure Python is installed
- Make sure port 8000 isn't already in use
- Check the error message in the command window

### If the viewer shows "Server: Offline":
- The server window might have closed
- Restart `START_VIEWER_SERVER.bat`
- Refresh your browser (Ctrl+F5)

### If artifact counts show 0:
- Refresh the browser (Ctrl+F5)
- Check the server is actually running
- Look for errors in browser console (F12)

### If review buttons don't work:
- Make sure server status shows "• Server: Online" (green)
- Check you filled in the "Reason" field
- Look for error messages in browser console (F12)

---

## Where Everything Lives

```
agent-orchestrator/
├── START_VIEWER_SERVER.bat    ← **START HERE** (double-click this)
├── artifacts/
│   ├── ARTIFACT_INDEX.html    ← The viewer (opened automatically)
│   └── [your artifacts here]  ← All your 104+ artifacts
├── review/
│   └── HR_*_queue.json        ← Review queues (created automatically)
└── app/
    └── main.py                ← The FastAPI server code
```

---

## That's It!

**Summary:**
1. Double-click `START_VIEWER_SERVER.bat`
2. Browser opens automatically
3. Browse, search, and review artifacts
4. Approve/reject with reasons
5. Generate briefs when ready

The batch file is right there in the main `agent-orchestrator` folder - just double-click it!
