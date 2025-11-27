"""Simple runner to start the app when executed as a script.

Run with:
    python run.py

This imports the `app` package and calls its `main()` function, so package-relative
imports inside `app` work correctly.
"""

from app.main import main


if __name__ == "__main__":
    main()
