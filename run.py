from app import app
import os

if __name__ == "__main__":
    app.run(debug=os.getenv('APIDEBUG', True),
        host=os.getenv('APIHOST', '127.0.0.01'),
        port=os.getenv('APIPORT', 5000))
