import sys
import os

# Ensure src is in the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app

if __name__ == "__main__":
    app.run(debug=True)