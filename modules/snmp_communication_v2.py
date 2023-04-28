import sys
from pysnmp.hlapi import *
#from pysnmp import debug

def snmp_comm(community_string, target_ip, target_port, oid_str):
    oid = ObjectIdentity(oid_str)
#    debug.setLogger(debug.Debug('all'))
    # Create an SNMP walk request
    snmp_walk = nextCmd(
        SnmpEngine(),
        CommunityData(community_string),
        UdpTransportTarget((target_ip, target_port)),
        ContextData(),
        ObjectType(oid),
        lexicographicMode=False
    )
#    print(snmp_walk)
    # Send the SNMP request and receive the response
    try:
        #data = {}
        data = []
        current_id=0
        for error_indication, error_status, error_index, var_binds in snmp_walk:
            # Check for errors
            try:
                if error_indication:
                    #print(f'SNMP request failed: {error_indication}')
                    #data.update({str(current_id) : {"error": f"SNMP request failed: {error_indication}"}})
                    data.append({"error": f"SNMP request failed: {error_indication}"})
                    break
                elif error_status:
                    #print(f'SNMP error: {error_status}')
                    #data.update({str(current_id) : {"error": f"SNMP request failed: {error_status}"}})
                    data.append({"error": f"SNMP request failed: {error_status}"})
                    break
                else:
                    # Print the result
                    #print(var_binds)
                    for var_bind in var_binds:
                        try:
                            #print(f'SNMP response: {var_bind[0]} = {var_bind[1]}')
                            #data.update({current_id:[x.prettyPrint() for x in var_bind]})

                            #data.update({str(current_id) : {"data": [x.prettyPrint() for x in var_bind]}})
                            data.append({"data": [x.prettyPrint() for x in var_bind]})

                            #print(var_bind)
                        except KeyboardInterrupt:
                            sys.exit()
                current_id+=1
            except KeyboardInterrupt:
                break
            except Exception as e:
                #print(str(e))
                #data.update({str(current_id) : {"error": str(e)}})
                data.append({"error": str(e)})
        #print(data)
        return data
    except KeyboardInterrupt:
        sys.exit()

if __name__=="__main__":
    # Define the target device and SNMP credentials
    # community_string = 'public'
    community_string = sys.argv[1]
    target_ip = sys.argv[2].split(':')[0]
    try:
        target_port = int(sys.argv[2].split(':')[1])
    except:
        target_port = 161

    # Define the base OID to retrieve all information
    oid_str = sys.argv[3]
    print(snmp_comm(community_string, target_ip, target_port, oid_str))
