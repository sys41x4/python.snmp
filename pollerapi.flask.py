from flask import Flask, json
from modules import snmp_walk
import io, sys

ip_config = {}

with open("config/ip.config", 'r') as f:
    ip_config = json.loads(f.read())

print(ip_config)

#exit()

app = Flask(__name__)

@app.route('/')
def index():
    return "SNMP BASIC API TESTING"

@app.route('/api/snmp/get/<string:request>', methods=['GET'])
def get_snmp_data(request):
    json_data = {'sent':request, 'data':''}
    try:
        request=request.split(' ')
        data = io.StringIO()
        sys.stdout = data
        snmp_walk.snmp_comm(request[0], request[1].split(':')[0], int(request[2].split(':')[1]), request[2])
        json_data['data'] = data.getvalue()
        data=None
        sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = str(e)
    return json_data

@app.route('/api/snmp/ip/get/<string:request>', methods=['GET'])
def get_snmp_data_by_ip(request):
    json_data = {'sent':request, 'data':''}

    try:
        # json_data['sent'] = request
        json_data['sent'] = json.loads(request) # Format {"ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        data = io.StringIO()
        sys.stdout = data
        snmp_walk.snmp_comm(json_data['sent']['community'], json_data['sent']['server_ip'], json_data['sent']['server_port'], json_data['sent']['oid'])
        json_data['data'] = data.getvalue()
        data=None
        sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = str(e)
    return json_data

@app.route('/api/snmp/uuid/get/<string:request>', methods=['GET'])
def get_snmp_data_by_uuid(request):
    json_data = {'sent':request, 'data':''}

    try:
        # json_data['sent'] = request
        json_data['sent'] = json.loads(json_data['sent']) # Format {"ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        ip_detail = ip_config[json_data['sent']['uuid']]
        print(ip_detail)
        data = io.StringIO()
        sys.stdout = data
        snmp_walk.snmp_comm(json_data['sent']['community'], ip_detail['server_ip'], ip_detail['server_port'], json_data['sent']['oid'])
        json_data['data'] = data.getvalue()
        data=None
        sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = str(e)
    return json_data

app.run(debug=True, host="0.0.0.0", port=8080)
