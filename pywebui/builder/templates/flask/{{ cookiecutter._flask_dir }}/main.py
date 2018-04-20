from flask import Flask, url_for, redirect, request
from pywebui.bridge import Bridge
from six import StringIO
app = Flask(__name__)

bridge_out = StringIO()
bridge = Bridge(None, bridge_out)

@app.route('/pywebui', methods=['POST'])
def bridge_call():
    bridge.handle_request(request.data.decode('utf-8'))
    bridge_out.seek(0)
    response = bridge_out.readline()
    bridge_out.seek(0)
    return response

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))
