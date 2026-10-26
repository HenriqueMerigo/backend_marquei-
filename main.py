from api.api_center import app
import os


if __name__ == "__main__":
    os.system('cls')
    app.run(port=5000, debug=True)