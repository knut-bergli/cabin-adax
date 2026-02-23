### Cabin Adax/Mill Heating Dashboard (Starter App)

This is a starter FastAPI + fastapi-chameleon application focused on the frontend (presentation layer) for monitoring and controlling temperature setpoints of Adax and Mill electrical panel heaters.

At this stage, the app uses mocked data and simple in-memory update logic so you can iterate on the UI before integrating real devices/APIs.

---

### What’s included
- FastAPI application with Chameleon templates
- Mock data for rooms and heaters
- Dashboard that displays:
  - Average temperature per room
  - Current setpoint per room
  - List of heaters per room with current temperature/setpoint and ON/OFF badge
- Simple form to update a room’s setpoint (affects all heaters in that room in-memory)
- Basic responsive styling

---

### Project structure
```
/Users/knb/pyCharm_projects/cabin-adax
├── main.py                       # FastAPI app & routes
├── models.py                     # Pydantic models: Room, Heater
├── data_service.py               # Mock data + setpoint update
├── templates/
│   ├── shared/
│   │   └── _layout.pt            # Base layout template
│   └── home/
│       └── index.pt              # Dashboard view
├── static/
│   └── css/
│       └── site.css              # Basic styles
└── pyproject.toml
```

---

### Installation
Create/activate your virtual environment and install dependencies:
```bash
pip install fastapi uvicorn fastapi-chameleon chameleon
```

---

### Running the app
```bash
uvicorn main:app --reload
```
Then navigate to:
- http://127.0.0.1:8000/

---

### Core files and responsibilities
- `models.py`
  - `Heater`: `id`, `name`, `type` ("Adax" or "Mill"), `current_temp`, `setpoint`, `is_on`
  - `Room`: `id`, `name`, `heaters`
    - Convenience properties for `average_temp` and `current_setpoint` (assuming uniform setpoint within a room for now)

- `data_service.py`
  - In-memory list of `Room` instances with sample heaters and readings
  - `get_rooms()` returns the current mock dataset
  - `update_room_setpoint(room_id, new_setpoint)` updates all heaters in a given room

- `main.py`
  - Initializes FastAPI and fastapi-chameleon
  - Static files mounted at `/static`
  - Routes:
    - `GET /` renders the dashboard
    - `POST /set_temp/{room_id}` updates a room’s setpoint and redirects back to `/`

- `templates/shared/_layout.pt`
  - Page layout with a named slot for content (Chameleon METAL/TAL)

- `templates/home/index.pt`
  - Dashboard iterating rooms and heaters
  - Displays average temp, setpoint, and per-heater info
  - A form per room to post new setpoint

- `static/css/site.css`
  - Simple, clean styles for cards and lists

---

### Notes on templating
- Uses Chameleon (ZPT) with TAL/METAL for layout and binding values.
- The layout defines a `content` slot; the `home/index.pt` view fills that slot and renders the dashboard.

---

### Next steps (suggested)
- Replace mock store with real Adax/Mill integrations; wire reads/updates into `data_service.py`.
- Add per-heater setpoint controls and room/heater management UIs.
- Persist data via SQLite/SQLModel or similar instead of in-memory.
- Add tests (e.g., FastAPI TestClient for routes and HTML checks).
- Consider a background refresh task or WebSocket updates for live temperatures.

---

### Troubleshooting
- If the editor reports unresolved imports for `fastapi`/`uvicorn`/`chameleon`, ensure your venv is activated and packages are installed in that environment.
- For templating syntax errors, verify TAL/METAL attributes and Python expressions (avoid f-strings inside `${...}` in templates; prefer `tal:replace` with `python:` expressions).
