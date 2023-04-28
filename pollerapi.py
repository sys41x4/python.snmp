import os, io, sys
import ujson
from typing import Union
from fastapi import FastAPI
import uvicorn

from modules import snmp_communication_v2 as snmp_comm_v2


print("--- PYTHON.SNMP_POLLER ---")


class CONFIG:
    def __init__(self, base_config_fp):
        '''Load core config data'''
        if(os.path.isfile(base_config_fp)):
            self.base_config_data = self.get_json_data(base_config_fp)
            print("Base CONFIG | Loaded Successfully | :)")
        else:
            print("\n\nBase CONFIG PATH | Not Found : at "+base_config_fp+" | :/")
            sys.exit()

    def get_json_data(self, fp):
        '''Get JSON File Data'''
        with open(fp, 'r') as f:
            data = ujson.loads(f.read())
        return data

    def get_server_info(self, config_fp=''):
        '''Get Server info Config file'''
        return self.get_json_data(config_fp)

    def get_serverLoader_info(self, config_fp=''):
        '''Get Server Loader Config File'''
        return self.get_json_data(config_fp)

    def load(self,):
        '''LOAD CONFIG Data'''

        # Load server_info | config
        if(os.path.isfile(self.base_config_data['fp_server_info'])):
            self.serverLoader_info = self.get_serverLoader_info(self.base_config_data['fp_server_info'])
            print("SERVER LOADER CONFIG | Loaded Successfully")
        else:
            print("SERVER LOADER INFO CONFIG FilePath | Not Found | :/")
            sys.exit()

        if(os.path.isfile(self.base_config_data['fp_ip_info'])):
            self.server_info = self.get_server_info(self.base_config_data['fp_ip_info'])
            print("SERVER INFO CONFIG | Loaded Successfully")
        else:
            print("SERVER INFO CONFIG FilePath | Not Found | :/")
            self.serverLoader_info={}


# sys.argv assignments
# Format : python3 <filename>.py <BASE_CONFIG_FILE_PATH>
#          BASE_CONFIG_FILE_PATH | format: JSON

def help_msg():
    help_info = """
Format : python3 "+sys.argv[0]+" <BASE_CONFIG_FILE_PATH>
         BASE_CONFIG_FILE_PATH | format: JSON
"""

try:
    if(len(sys.argv)>1):
        if(sys.argv[1].lower()=='help'):
            print(help_msg)
            sys.exit()
        base_config_fp = sys.argv[1]
    else:
        base_config_fp = '/etc/python.snmp_poller/config/base.config'

    config = CONFIG(base_config_fp)
    config.load()
except:
   print(help_msg())
   sys.exit()

app = FastAPI()


@app.get("/")
def root_index():
    return {"status": 200}


@app.get("/api/")
def api_info():
    return {"api": {"version":"1.0.0"}}

@app.get("/api/{service_name}")
def service_info(service_name: str):
    return {"service": service_name}

@app.get("/api/snmp/get/{request}")
async def get_snmp_data(request: str):
    json_data = {'sent':request, 'data':''}
    try:
        request=request.split(' ')
        #data = io.StringIO()
        #sys.stdout = data
        json_data['data'] = snmp_comm_v2.snmp_comm(request[0], request[1].split(':')[0], int(request[1].split(':')[1]), request[2])
        #json_data['data'] = data.getvalue()
        #data=None
        #sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = {"error": str(e)}
    return json_data


@app.get('/api/snmp/ip/get/{request}')
async def get_snmp_data_by_ip(request: str):
    json_data = {'sent':request, 'data':''}

    try:
        # json_data['sent'] = request
        json_data['sent'] = ujson.loads(request) # Format {"ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        #data = io.StringIO()
        #sys.stdout = data
        json_data['data'] = snmp_comm_v2.snmp_comm(json_data['sent']['community'], json_data['sent']['server_ip'], json_data['sent']['server_port'], json_data['sent']['oid'])
        #json_data['data'] = data.getvalue()
        #data=None
        #sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = {'error': str(e)}
    return json_data

@app.get('/api/snmp/uuid/get/{request}')
async def get_snmp_data_by_uuid(request: str):
    json_data = {'sent':request, 'data':''}
    try:
        json_data['sent'] = ujson.loads(json_data['sent']) # Format {"ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        ip_detail = config.server_info[json_data['sent']['uuid']]
        #print(ip_detail)
        #data = io.StringIO()
        #sys.stdout = data
        json_data['data'] = snmp_comm_v2.snmp_comm(json_data['sent']['community'], ip_detail['server_ip'], ip_detail['server_port'], json_data['sent']['oid'])
        #json_data['data'] = ujson.loads(data.getvalue())
        #data=None
        #sys.stdout = sys.__stdout__
    except Exception as e:
        json_data['data'] = {"error": str(e)}
    return json_data

if __name__ == "__main__":
    uvicorn.run("pollerapi:app", reload=config.serverLoader_info["reload"], host=config.serverLoader_info["host"], port=config.serverLoader_info["port"])
