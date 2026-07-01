from dotenv import load_dotenv
import os

from flask import Flask
from flask_smorest import Api

from resources.members import blp as MemberBlueprint
from resources.contributions import blp as ContributionsBlueprint

app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['API_TITLE'] = 'Jalod Server API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.3'
app.config['OPENAPI_URL_PREFIX'] = '/'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

api = Api(app)
api.register_blueprint(MemberBlueprint)
api.register_blueprint(ContributionsBlueprint)


@app.route('/')
def hello_world():
    return "Welcome to the Jalod Server App!"

if __name__ == '__main__':
    app.run(debug=True)