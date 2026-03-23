# Piddy Desktop App - Rebuild Instructions

## Issue Summary
The packaged .exe was missing critical files:
- `start_piddy.py` (Python backend script)
- `frontend/dist/` (Frontend React build)

This prevented the backend from starting and frontend from loading.

## Solutions Applied

### 1. **Fixed electron-builder Package Configuration** (`desktop/package.json`)
Changed from `"files"` array to `"extraFiles"` with explicit source→destination mappings:

```json
"extraFiles": [
  {"from": "../frontend/dist", "to": "frontend/dist"},
  {"from": "../start_piddy.py", "to": "start_piddy.py"},
  {"from": "../requirements.txt", "to": "requirements.txt"}
]
```

This ensures files from parent directories are properly included in the built app.

### 2. **Fixed Path Resolution** (`desktop/main.js` and `piddy/desktop/main.js`)
Added `getResourcePath()` function that handles both development and packaged modes:

```javascript
function getResourcePath(relativePath) {
  if (isDevelopment) {
    return path.join(__dirname, '..', relativePath);
  } else {
    // In packaged app, files are at app root
    return path.join(app.getAppPath(), relativePath);
  }
}
```

Updated both `startStaticServer()` and `startPythonBackend()` to use this function, with better logging:
- Shows which paths it's looking for
- Confirms when files are found: ✅
- Warns with full path if files are missing

## Rebuild Steps

### On Windows Machine:

1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Delete Old Build**
   ```bash
   cd desktop
   rm -r dist node_modules
   ```

3. **Build Fresh**
   ```bash
   npm install
   npm run build          # Builds React frontend AND creates .exe
   # OR for Windows only:
   npm run dist:win       # Just builds Windows .exe
   ```

4. **Test New App**
   ```bash
   .\dist\win-unpacked\Piddy.exe
   ```

## What to Expect

### Console Output (App Starting)
```
[INFO] 🚀 Piddy Desktop App starting...
[INFO] App path: C:\Users\...\Piddy\dist\win-unpacked\resources\app
[INFO] Starting Python backend...
[INFO] Python script path: C:\Users\...\Piddy\dist\win-unpacked\resources\app\start_piddy.py
[INFO] ✅ Found start_piddy.py
[INFO] Attempting to serve static files from: C:\Users\...\Piddy\dist\win-unpacked\resources\app\frontend\dist
[INFO] ✅ Found frontend dist directory
[INFO] Static server running on http://localhost:4000
[INFO] ✅ Backend is ready!
[INFO] Creating main window...
```

### Dashboard Display
- Frontend loads via HTTP static server on http://localhost:4000
- Backend accessible on http://localhost:8000
- Dashboard displays system overview data
- No "ERR_FILE_NOT_FOUND" errors

## File Structure in Built App

```
dist/win-unpacked/Piddy.exe              (Main executable)
dist/win-unpacked/resources/
  app/
    desktop/main.js                      (Electron main process)
    desktop/preload.js
    start_piddy.py                       (Python backend script) ← NEW
    frontend/dist/                       (React app) ← NEW
      index.html
      assets/
        ...
```

## If Still Getting Errors

### "start_piddy.py not found"
- Check if file exists: `dir dist\win-unpacked\resources\app\start_piddy.py`
- Verify `package.json` has the correct `extraFiles` config
- Rebuild with `npm run dist:win`

### "Frontend dist directory not found"  
- Check: `dir dist\win-unpacked\resources\app\frontend\dist`
- Ensure `npm run build` completed without errors
- Rebuild with `npm run build`

### CORS/File Loading Errors
- Should NOT see these anymore (using HTTP static server now)
- If still seeing: app likely fell back to file:// protocol
- Check console for "Static server running on http://localhost:4000"

## Testing Checklist

After rebuilding and running the .exe:

- [ ] App launches without errors
- [ ] See `Static server running on http://localhost:4000` in console
- [ ] Backend starts successfully (no timeout errors)
- [ ] Dashboard displays with data (system overview, menu options)
- [ ] No CORS or "ERR_FILE_NOT_FOUND" errors in console
- [ ] Navigation works (can click dashboard menu items)
- [ ] Dev tools show React components loaded

## Questions?

Check the app console (always open in dev mode) for detailed error messages showing:
- Exact file paths attempted
- Which files were found (✅) or missing (⚠️)
- Backend health check attempts and results

This logging helps identify any remaining path resolution issues.
