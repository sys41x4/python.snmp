import os, io, sys
import ujson
from typing import Optional, Union, List
from fastapi import FastAPI, Query
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
            self.server_info = self.get_server_info(self.base_config_data['fp_ip_info'])["snmp"]
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

@app.get("/api/snmp/cmd/get")
async def get_snmp_cmd_data(cmd: str = Query(...)):
    json_data = {'sent':cmd, 'data':''}
    try:
        request=cmd.split(' ')

        service_address = request[1].split(':')
        if(len(service_address)==1):service_address.insert(1, '')
        json_data['data'] = snmp_comm_v2.snmp_comm(request[0], service_address[0], service_address[1], request[2].replace(' ', '').split(","))
    except Exception as e:
        json_data['data'] = {"error": str(e)}
    return json_data


@app.get('/api/snmp/get/{request}')
async def get_snmp_data(request: str):
    json_data = {'sent':request, 'data':''}

    try:
        json_data['sent'] = ujson.loads(request) # Format {"data_by":<uuid/ip/cmd>, "ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        data_by = str(json_data['sent']['data_by'].lower())
        if(data_by=='ip'):
            service_address = json_data['sent']['service_address'].split(':')
            if(len(service_address)==1):service_address.insert(1, '')
            json_data['data'] = snmp_comm_v2.snmp_comm(json_data['sent']['community'], service_address[0], service_address[1], json_data['sent']['oid'].replace(' ', '').split(","))

        elif(data_by=='uuid'):
            for id in config.server_info.keys():
                if(config.server_info[id]["uuid"]==json_data['sent']['uuid']):
                    ip_detail = config.server_info[id]
                    if('oid' in json_data['sent'].keys()):oid=json_data['sent']['oid'].replace(' ', '').split(",")

                    json_data['data'] = snmp_comm_v2.snmp_comm(ip_detail['community'], ip_detail['ip'][0], ip_detail['ip'][1], oid)
                    break

    except Exception as e:
        json_data['data'] = {'error': str(e)}
    return json_data

@app.get('/api/snmp/get')
async def get_snmp_data_query(data_by: str = Query(...),
        service_name: str = Query(...),
        keys: str = Query(...),
        values: str = Query(...)):

    json_data = {'sent':[data_by, service_name, dict(zip(keys.split(','), values.split(',')))], 'data':''}

    try:
        #json_data['sent'] = ujson.loads(request) # Format {"data_by":<uuid/ip/cmd>, "ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        data_BY = str(json_data["sent"][0].lower())
        if(data_BY=='ip'):
            service_address = json_data["sent"][2]['service_address'].split(':')
            if(len(service_address)==1):service_address.insert(1, '')
            json_data['data'] = snmp_comm_v2.snmp_comm(json_data["sent"][2]['community'], service_address[0], service_address[1], json_data["sent"][2]['oid'].replace(' ', '').replace("\"", '').replace('\'', '').replace('-', ',').split(","))

        elif(data_BY=='uuid'):
            for id in config.server_info.keys():
                if(config.server_info[id]["uuid"]==json_data["sent"][2]['uuid']):
                    ip_detail = config.server_info[id]
                    if('oid' in json_data["sent"][2].keys()):oid=json_data["sent"][2]['oid'].replace(' ', '').replace("\"", '').replace('\'', '').replace('-', ',').split(",")

                    json_data['data'] = snmp_comm_v2.snmp_comm(ip_detail['community'], ip_detail['ip'][0], ip_detail['ip'][1], oid)
                    break

    except Exception as e:
        json_data['data'] = {'error': str(e)}
    except KeyboardInterrupt:pass
    return json_data


@app.post('/api/snmp/get/')
async def get_snmp_data_post(data_by: str = None, uuid: Optional[str] = None, service_address: Optional[str] = None, community: Optional[str] = None, oid: str = None):
    formated_json = {"data_by":data_by,
                     "uuid":uuid,
                     "service_address":service_address,
                     "community":community,
                     "oid":oid
                     }
    json_data = {'sent':{k: v for k, v in formated_json.items() if v is not None}, 'data':''}

    try:
        #json_data['sent'] = ujson.loads(request) # Format {"data_by":<uuid/ip/cmd>, "ip":<ip>, "uuid":<uuid>, "port":<port>, "community":<community_type>, "version":<snmp_version>, "oid":<oid>}
        if(json_data.data_by=='ip'):
            service_address = json_data['sent']['service_address'].split(':')
            if(len(service_address)==1):service_address.insert(1, '')
            json_data['data'] = snmp_comm_v2.snmp_comm(json_data['sent']['community'], service_address[0], service_address[1], json_data['sent']['oid'].replace(' ', '').split(","))

        elif(data_by=='uuid'):
            for id in config.server_info.keys():
                if(config.server_info[id]["uuid"]==json_data['sent']['uuid']):
                    ip_detail = config.server_info[id]
                    if('oid' in json_data['sent'].keys()):oid=json_data['sent']['oid'].replace(" ", '').split(",")

                    json_data['data'] = snmp_comm_v2.snmp_comm(ip_detail['community'], ip_detail['ip'][0], ip_detail['ip'][1], oid)
                    break

    except Exception as e:
        json_data['data'] = {'error': str(e)}
    return json_data

if __name__ == "__main__":
    uvicorn.run("pollerapi:app", reload=config.serverLoader_info["reload"], host=config.serverLoader_info["host"], port=config.serverLoader_info["port"])
