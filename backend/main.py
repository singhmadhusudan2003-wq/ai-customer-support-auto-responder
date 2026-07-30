"""
main.py (backend entrypoint)
------------------------------
Run the backend with:
    python main.py
or (recommended, with hot reload):
    uvicorn main:app --reload

Serves the API at http://localhost:8000  (interactive docs at /docs)
"""

import uvicorn

from app.main import app  # noqa: F401  (re-exported for `uvicorn main:app`)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
