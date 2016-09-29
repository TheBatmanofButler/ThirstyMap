from flask import Flask, render_template, request, url_for
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

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)