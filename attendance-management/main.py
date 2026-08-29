import sys
import os

# Root directory Python PATH pe configure ha!
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import init_db
from views.main_window import MainWindow


def main():
    print("Initializing Database...")
    init_db()  # For Tables to exist

    print("Launching GUI Application...")
    app = MainWindow()
    app.mainloop()  # Starts Tkinter event handling loop


if __name__ == "__main__":
    main()