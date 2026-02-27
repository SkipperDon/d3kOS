# Manage Manuals - RAG Delete Function Fix

**Date:** February 27, 2026
**Status:** ✅ COMPLETE - Bug fixed, tested, and verified
**Session Duration:** ~30 minutes
**Bug:** Delete button only removed PDF from filesystem, not from RAG database

---

## Summary

Fixed critical bug in the "Manage Manuals" delete function. The web UI claimed to remove documents from the "AI knowledge base" but only deleted the file from disk, leaving old content searchable by the AI.

**Result:** Delete button now properly removes documents from both filesystem AND RAG vector database, ensuring old fishing regulations (or any outdated manuals) are truly removed from the AI's memory.

---

## The Bug

### User's Use Case:

User needs to update fishing regulations annually:
1. Delete old 2026 regulations
2. Upload new 2027 regulations
3. AI should cite ONLY the new regulations

### What Was Broken:

**UI Message:** "This will also remove its content from the AI knowledge base"

**Backend Reality:**
```python
def delete_manual(self, filename):
    # ...
    os.remove(filepath)  # Only deleted file
    # ❌ Did NOT call RAG delete function
```

**Result:**
- ✅ PDF file deleted from `/opt/d3kos/data/manuals/`
- ❌ Document still in ChromaDB vector database
- ❌ AI still had old regulations in memory
- ❌ AI could cite outdated 2026 regulations even after "deleting" them

---

## Root Cause Analysis

### Investigation Process:

1. **User reported:** Need to remove old PDFs from "ollama memory" (RAG database)
2. **Found:** "Manage Manuals" page has delete button
3. **Checked backend:** `history_api.py` delete_manual() method
4. **Discovered:** Only calls `os.remove(filepath)`, no RAG integration

### Missing Integration:

The delete function was never connected to the RAG system:
- Upload flow: ✅ Adds to RAG (fixed in previous session)
- Delete flow: ❌ Does not remove from RAG (THIS BUG)

---

## The Fix

### Files Modified:

**File:** `/opt/d3kos/services/ai/history_api.py`
**Backup:** `/opt/d3kos/services/ai/history_api.py.bak.pre-rag-delete`

### Changes Made:

#### 1. Added PDF Processor Import:
```python
import sys

# Add PDF processor to path for RAG integration
sys.path.insert(0, '/opt/d3kos/services/documents')

# Import PDF processor for RAG (optional - fail gracefully if not available)
try:
    from pdf_processor import PDFProcessor
    RAG_AVAILABLE = True
    print("✓ RAG integration enabled for manual deletion", flush=True)
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠ RAG integration disabled: {e}", flush=True)
```

#### 2. Initialize RAG Processor (Module-Level):
```python
# Initialize RAG processor if available (module-level, persistent)
rag_processor = None
if RAG_AVAILABLE:
    try:
        rag_processor = PDFProcessor()
        print("✓ RAG processor initialized", flush=True)
    except Exception as e:
        print(f"⚠ RAG processor initialization failed: {e}", flush=True)
        rag_processor = None
```

#### 3. Modified delete_manual() Method:
```python
def delete_manual(self, filename):
    """Delete an uploaded manual from filesystem and RAG database"""
    try:
        # Sanitize filename
        filename = os.path.basename(filename)
        filepath = os.path.join(MANUALS_DIR, filename)

        # Validation checks...

        # ✅ NEW: Delete from RAG database first (before deleting file)
        rag_deleted = False
        rag_error = None

        if rag_processor:
            try:
                print(f"🗑️ Removing from RAG database: {filename}", flush=True)
                rag_result = rag_processor.delete_document(filename)  # <-- Pass filename, not filepath!

                if rag_result.get('success'):
                    print(f"✓ Removed from RAG: {filename}", flush=True)
                    rag_deleted = True
                else:
                    rag_error = rag_result.get('error', 'Unknown RAG error')
                    print(f"⚠ RAG deletion failed: {rag_error}", flush=True)
                    # Continue with file deletion even if RAG fails

            except Exception as e:
                rag_error = str(e)
                print(f"⚠ RAG deletion error: {e}", flush=True)
                # Continue with file deletion even if RAG fails
        else:
            print(f"⚠ RAG not available - only deleting file", flush=True)

        # Delete file from filesystem
        os.remove(filepath)
        print(f"✓ Deleted file: {filename}", flush=True)

        # Prepare response
        response = {
            'success': True,
            'message': f'Manual {filename} deleted',
            'rag_deleted': rag_deleted
        }

        if rag_error:
            response['warning'] = f'File deleted but RAG removal failed: {rag_error}'

        self.send_json_response(response)

    except Exception as e:
        self.send_json_response({
            'success': False,
            'error': str(e)
        }, 500)
```

### Key Fix - Filename vs Filepath:

**Initial bug in the fix:**
```python
rag_result = rag_processor.delete_document(filepath)  # ❌ Wrong!
# filepath = "/opt/d3kos/data/manuals/test.pdf"
```

**The pdf_processor.delete_document() method expects filename only:**
```python
def delete_document(self, filename: str) -> Dict:
    # Find document by filename
    for hash_val, meta in self.metadata.items():
        if meta['filename'] == filename:  # <-- Searches by filename only!
            doc_hash = hash_val
            break
```

**Correct fix:**
```python
rag_result = rag_processor.delete_document(filename)  # ✅ Correct!
# filename = "test.pdf"
```

---

## Testing Results

### Test Setup:

Created test PDF:
- Filename: `test_delete_manual.pdf`
- Size: 3.1 KB
- Content: "Test Manual for Delete Function"

### Test Flow:

**Step 1: Upload Test PDF**
```bash
curl -X POST -F "file=@/tmp/test_delete_manual.pdf" -F "type=test" \
  http://localhost:8081/upload/manual
```

**Response:**
```json
{
  "success": true,
  "filename": "test_delete_manual.pdf",
  "size": 3127,
  "message": "Manual uploaded and processed successfully"
}
```

**Step 2: Verify in RAG Database**
```bash
cd /opt/d3kos/services/documents
python3 pdf_processor.py list | grep test_delete_manual
```

**Result:**
```json
{
  "filename": "test_delete_manual.pdf",
  "filepath": "/opt/d3kos/data/manuals/test_delete_manual.pdf",
  "hash": "fd1e1a317a197d8dde579c807853bb4b39863139306dbe52205fce5b66a35a2f",
  "chunks": 1,
  "characters": 104,
  "added_at": "2026-02-27 11:32:51"
}
```

**Status:** ✅ Document in RAG database

**Step 3: Delete via API (Fixed Code)**
```bash
curl -X DELETE http://localhost:8082/history/manual/test_delete_manual.pdf
```

**Response:**
```json
{
  "success": true,
  "message": "Manual test_delete_manual.pdf deleted",
  "rag_deleted": true
}
```

**Status:** ✅ Delete successful, RAG deleted

**Step 4: Verify Removal**

**Filesystem Check:**
```bash
ls -la /opt/d3kos/data/manuals/test_delete_manual.pdf
```

**Result:**
```
ls: cannot access '/opt/d3kos/data/manuals/test_delete_manual.pdf': No such file or directory
```

**Status:** ✅ File removed from filesystem

**RAG Database Check:**
```bash
cd /opt/d3kos/services/documents
python3 pdf_processor.py list | grep -c test_delete_manual
```

**Result:**
```
0
```

**Status:** ✅ Document removed from RAG database

---

## Behavior Changes

### Before Fix:

**Delete Button Click:**
1. ✅ File deleted from `/opt/d3kos/data/manuals/`
2. ❌ Document STILL in ChromaDB
3. ❌ AI can still search old content
4. ❌ AI cites deleted regulations

**Example Problem:**
```
User: Delete 2026 fishing regulations (via web UI)
System: "Manual deleted" ✓
User: "What's the walleye bag limit?"
AI: "According to 2026 fishing regulations: 6 walleye" ← WRONG! (old data)
```

### After Fix:

**Delete Button Click:**
1. ✅ RAG database entry deleted
2. ✅ Metadata removed
3. ✅ File deleted from filesystem
4. ✅ AI cannot find old content

**Correct Behavior:**
```
User: Delete 2026 fishing regulations (via web UI)
System: "Manual deleted" ✓ (RAG + file)
User: Upload 2027 fishing regulations
System: "Manual uploaded and processed" ✓
User: "What's the walleye bag limit?"
AI: "According to 2027 fishing regulations: 4 walleye" ← CORRECT! (new data)
```

---

## API Response Format

### Success (Both Deleted):
```json
{
  "success": true,
  "message": "Manual fishing-regs-2026.pdf deleted",
  "rag_deleted": true
}
```

### Success (File Only):
```json
{
  "success": true,
  "message": "Manual manual.pdf deleted",
  "rag_deleted": false,
  "warning": "File deleted but RAG removal failed: Document not found"
}
```

### Error (File Not Found):
```json
{
  "success": false,
  "error": "Manual not found"
}
```

---

## User Workflow

### Annual Regulations Update:

**Old Broken Workflow:**
1. Open "Manage Manuals" page
2. Click delete on "Fishing Regulations 2026.pdf"
3. Upload "Fishing Regulations 2027.pdf"
4. ❌ AI still cites 2026 regulations (ghost data)
5. User frustrated - has to manually remove from RAG via command line

**New Working Workflow:**
1. Open "Manage Manuals" page
2. Click delete on "Fishing Regulations 2026.pdf"
3. ✅ System removes from both filesystem and RAG
4. Upload "Fishing Regulations 2027.pdf"
5. ✅ AI only knows about 2027 regulations
6. ✅ Clean update complete

---

## Error Handling

### Graceful Degradation:

**RAG Not Available:**
- System continues with filesystem delete only
- Warning logged: "RAG not available - only deleting file"

**RAG Delete Fails:**
- File still deleted from filesystem
- Response includes warning message
- User can manually verify with RAG list command

**File Not Found:**
- Returns 404 error
- No attempt to delete from RAG
- Prevents accidental RAG deletions

---

## Files Modified (on Pi)

**Modified:**
- `/opt/d3kos/services/ai/history_api.py`
  - Added pdf_processor import
  - Added RAG processor initialization
  - Modified delete_manual() to call RAG delete
  - Added rag_deleted flag to response
  - **Bug fix:** Pass filename (not filepath) to delete_document()
  - Backup: `history_api.py.bak.pre-rag-delete`

**No Changes Needed:**
- `/var/www/html/manuals.html` (UI already shows correct message)
- `/opt/d3kos/services/documents/pdf_processor.py` (delete method already exists)

---

## Service Management

**Service Name:** d3kos-history-api (not a systemd service, runs as background process)

**Restart Commands:**
```bash
# Kill old process
sudo pkill -f history_api.py

# Start new process
cd /opt/d3kos/services/ai
nohup python3 history_api.py > /tmp/history_api.log 2>&1 &

# Verify running
ps aux | grep history_api | grep -v grep
```

**Log File:** `/tmp/history_api.log`

---

## Future Enhancements

### Potential Improvements:

1. **Systemd Service:** Convert to proper systemd service for auto-restart
2. **Batch Delete:** Allow multiple manuals to be deleted at once
3. **Trash/Recycle Bin:** Soft delete with 30-day recovery period
4. **Version Control:** Keep previous version when uploading same filename
5. **Confirmation Dialog:** "Are you sure? This will also remove from AI memory"

---

## Success Criteria

**✅ All criteria met:**

1. ✅ Delete button removes PDF from filesystem
2. ✅ Delete button removes document from RAG database
3. ✅ Delete button removes metadata
4. ✅ AI cannot find deleted content in searches
5. ✅ API returns rag_deleted flag
6. ✅ Graceful error handling (RAG failures don't block file delete)
7. ✅ User can update yearly regulations without ghost data

---

## User Impact

**Problem Solved:**

User can now confidently:
- Delete old fishing regulations
- Upload new regulations
- Trust that AI will cite ONLY the current regulations
- No manual RAG cleanup needed via command line

**No More:**
- Ghost data in AI responses
- Confusion about which regulations are active
- Manual RAG database maintenance
- Command-line RAG delete commands

---

**Implementation Complete:** February 27, 2026
**Result:** Delete button now properly removes from both filesystem and RAG! 🎉

**User can delete old fishing regulations and trust they're truly gone.**
