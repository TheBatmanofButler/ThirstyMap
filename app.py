from flask import Flask
import os
import image
app = Flask(__name__)

@app.route("/")
def hello():
    return image.waterImage(-73.961927, 40.785664, 17)

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)