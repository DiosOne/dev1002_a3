import sys
import os

# Add the root of the project to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from api.app import app

if __name__ == "__main__":
    # Only for local development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
