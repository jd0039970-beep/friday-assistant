# F.R.I.D.A.Y

Local Iron-Man AI. Runs on your PC only.

## Build the real .exe (native window — not a browser)

```powershell
cd C:\Users\frost\friday-assistant
git pull
powershell -ExecutionPolicy Bypass -File scripts\BUILD_EXE.ps1
```

When it finishes:

```
backend\dist\Friday\Friday.exe
```

Double-click **Friday.exe** (or the Desktop shortcut).  
Native OS window via pywebview. Backend starts inside the same process. No browser.

## First-time machine setup (if needed)

```powershell
powershell -ExecutionPolicy Bypass -File INSTALL_EVERYTHING.ps1
```

Then run `BUILD_EXE.ps1` as above.

Tab = talk · Esc = shut down · Everything local.
