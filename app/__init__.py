from pathlib import Path

backend_app = Path(__file__).resolve().parent.parent / "backend" / "app"
__path__.append(str(backend_app))

