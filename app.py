from flask import Flask, render_template, request
import os
import image
app = Flask(__name__)

@app.route("/")
def index():
	 return render_template('index.html', data = {})

@app.route('/', methods=['POST'])
def form_post():

    state_code = request.form['stateCode']
    number_of_hits = int(request.form['numberOfHits'])

    data = image.get_water_sources(state_code, number_of_hits)

    return render_template('index.html', state_code = state_code,
    					number_of_hits = number_of_hits,
    					data = data
    					)

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)