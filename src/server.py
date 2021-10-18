import sys
import signal
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.error import InputError
from src import config
<<<<<<< HEAD
from src.channels import channels_create_v1
from src.other import token_to_uid, clear_v1

=======
from src.other import clear_v1
from json import dumps
from src.auth import auth_register_v1,auth_login_v1
>>>>>>> master

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("channels/create/v2", methods=['POST'])
def channels_create_v2():
    token = request.args.get('token')
    name = request.args.get('name')
    is_public = request.args.get('is_public') == True

    auth_user_id = token_to_uid(token)

    return jsonify(channels_create_v1(auth_user_id, name, is_public))

#reset database through clearing the dictionaries
@APP.route("/clear/v1", methods=['DELETE'])
def delete_clear():
    clear_v1()
    return dumps({})

#reset database through clearing the dictionaries
@APP.route("/auth/register/v2", methods=['POST'])
def post_auth_register():
    request_data = request.get_json()
    auth_result = auth_register_v1(
        request_data['email'],
        request_data['password'],
        request_data['name_first'],
        request_data['name_last']
    )

    return dumps(auth_result)


#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
