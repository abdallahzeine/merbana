# API and Services Integration

Merbana is unique in that it lacks a traditional REST API Backend containing multiple endpoints (e.g., `/api/users`, `/api/orders`). All business logic executes directly inside the React browser session. 

The Python backend exists exclusively as a dumb storage sink with TWO custom endpoints active alongside static file serving.

## The Singular Storage Endpoint (`/api/save-db`)

### Request
`POST /api/save-db`
- **Body**: The entire serialized `db.json` document.
- **Headers**: `Content-Type: application/json`
- **Method**: Triggered directly by the `/src/services/database.ts` functions (`navigator.sendBeacon` or standard `fetch`).

### Python Backend Handling (`Deployment/merbana_launcher.py`)
When the launcher receives this HTTP POST:
1. It reads the whole payload immediately.
2. It generates a temporary file `db.json.tmp`.
3. It performs a natively atomic OS replacement function utilizing `os.replace(tmp, _data_path)`.
4. Returns a simple JSON `{"ok": True}`. 

### Why this Model?
By moving all calculation (totals, inventory checks, report aggregation) into React, the Python backend requires absolutely zero domain knowledge of the POS system. It simply receives bytes and secures them to the hard drive. 
- Fast frontend execution for employees.
- Unbreakable database architecture preventing partial states during crashes. 
- Dead-simple migration (exporting/importing functionality just overwrites the JSON payload).

## Static File Serving & The Read Endpoint
Besides the save endpoint, the Python server strictly serves the `dist/` directory React files, fulfilling the static site generation.

Additionally, a specific custom `GET` endpoint exists for fetching the database:
```python
if path == "/data/db.json":
   # serve the database purely
```
This avoids a REST API fetch to parse specific rows. It just downloads the JSON which is evaluated immediately upon the `loadDatabase()` frontend call initializing the session.
