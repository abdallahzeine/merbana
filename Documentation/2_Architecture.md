# Architecture

Merbana adopts an unconventional, ultra-lightweight architecture intended to bypass the complexities of traditional client-server-database triads natively. Everything lives on a single machine running entirely locally.

## Core Flow
1. **The Python Launcher (`Deployment/merbana_launcher.py`)** acts as the engine of the application.
2. It spins up a `socketserver.TCPServer` running standard Python `http.server`.
3. The server locates an open port locally and serves the compiled React Single Page Application (SPA), which operates from the `dist/` directory.
4. It also searches for a file named `data/db.json` placed parallel to the `dist/` folder.
5. Once the server is live, the launcher spawns a native OS window utilizing `pywebview` connected to the local server.

## The Database
There is no SQLite, Postgres, or MongoDB. The entire data layer operates exclusively as a centralized JSON object.
- **Read Phase**: The React SPA boots and issues a `GET /data/db.json` request. The Python server simply serves the JSON file. The frontend maps this into memory.
- **Write Phase**: Any change made inside the React SPA immediately triggers the whole data object to be converted back into a JSON string and posted to `POST /api/save-db`, where the Python launcher atomically overwrites the physical `db.json` file.

### Fault Tolerance & Atomicity
`merbana_launcher.py` explicitly uses an atomic renaming mechanic to avoid data corruption if the system crashes during serialization.
```python
tmp = _data_path + ".tmp"
with open(tmp, "wb") as f:
    f.write(body)
os.replace(tmp, _data_path)  # atomic write
```

## Window Compilation
The `build_windows.py` file builds the system for end-users on Windows.
- It executes `npm run build` to generate the Vite-bundled React assets.
- It leverages PyInstaller using the `--onefile` flag to bundle Python, `pywebview`, and `merbana_launcher.py` into `Merbana.exe`.
- It generates a distribution folder copying `dist/` and `data/db.json` directly next to the `.exe`.
- It provides a `Merbana.bat` script that accurately sets `MERBANA_DIST_PATH` routing the `.exe` to the unzipped React build. 
