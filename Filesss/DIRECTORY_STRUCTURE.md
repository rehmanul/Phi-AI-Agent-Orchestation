# Directory Structure - Folder Monitor System

## Created Directories

The folder monitor system creates and uses the following directory structure:

```
investment-sales-bd/
├── output/
│   ├── processed_documents/     # All processing outputs
│   │   ├── parsed/              # Parsed text, layout, tables
│   │   ├── classified/          # Classification results
│   │   └── results/             # Complete processing results
│   ├── archive/                 # Archived original files (prevents reprocessing)
│   └── logs/
│       └── processed_files.json # Processing log (tracks what's been done)
│
├── agents/
│   └── monitoring/
│       ├── __init__.py
│       └── folder_monitor.py   # Folder monitoring agent
│
└── process_folder_monitor.py    # Main processing script
```

## Input Folder

**Monitored Folder:** `C:\Users\phi3t\12.20 dash\1.5.2026\PDF HTML TRAINING PHI ADD IN`

This folder is monitored for:
- `*.pdf` files
- `*.html` files

## How It Works

### 1. Folder Monitoring
- Agent checks the input folder for new files
- Compares against processed log to avoid duplicates

### 2. Duplicate Prevention
- **File Hash (SHA256):** Primary check - unique file content identifier
- **Filename + Size:** Secondary check
- **Archive Log:** JSON file tracks all processed files with metadata

### 3. Processing Flow
1. Check if file already processed → Skip if yes
2. Parse document (PDF or HTML)
3. Classify document type and relevance
4. Save all outputs to organized directories
5. Archive original file
6. Mark as processed in log

### 4. Output Organization
- **parsed/**: Raw parsing outputs (text, layout, tables)
- **classified/**: Classification results (type, relevance)
- **results/**: Complete processing results with metadata
- **archive/**: Original files (backup, prevents reprocessing)

## Running the Monitor

```bash
cd investment-sales-bd
python process_folder_monitor.py
```

The agent will:
1. Check input folder for new files
2. Process only new files (skip already processed)
3. Archive and tag completed work
4. Generate summary report

## Benefits

✅ **No Duplicate Work:** Files are tracked by hash, won't process twice  
✅ **Organized Output:** All results in structured directories  
✅ **Archive Safety:** Original files preserved  
✅ **Resumable:** Can stop/restart without losing progress  
✅ **Audit Trail:** Complete log of all processed files
