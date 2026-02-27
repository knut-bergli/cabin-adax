### Updated Database ID Type and Admin Panels

I have updated the `Room` and `Heater` models to use integer IDs with automatic incrementing. Additionally, I have hidden these IDs from the admin management panels.

#### Changes Made:

1.  **Models (`app/models/`):**
    *   Changed `id` from `str` to `Optional[int]` in both `Room` and `Heater` classes.
    *   Added `default=None` and `primary_key=True` to these fields, which enables auto-increment in SQLModel/SQLAlchemy for integer primary keys.
    *   Updated `Heater.room_id` to be of type `Optional[int]`.

2.  **Services (`app/services/data_service.py`):**
    *   Updated all function signatures (e.g., `get_room_by_id`, `update_room`, `delete_room`) to accept `int` for ID parameters instead of `str`.

3.  **Routers (`app/routers/`):**
    *   In `admin.py`, updated route parameters to `int` and removed the `id` field from `add_room_post` and `add_heater_post` since they are now auto-generated.
    *   In `heaters_dashboard.py`, updated `set_temp` to accept `int` for `room_id`.

4.  **Templates (`app/templates/admin/`):**
    *   Removed "ID" columns from `rooms.pt` and `heaters.pt`.
    *   Removed the ID input fields from `edit_room.pt` and `edit_heater.pt`.

5.  **Database & Migration:**
    *   Updated `migrate_rooms.py` to support integer IDs and use `session.flush()` to retrieve generated IDs for foreign key relationships.
    *   Recreated the SQLite database (`cabin_adax_storage/db/cabin_adax.sqlite`) to apply the schema changes and re-migrated initial data from `app/data/rooms.json`.
