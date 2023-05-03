import sys
from pysnmp.hlapi import *
#from pysnmp import debug

def snmp_comm(community_string, target_ip, target_port, oid_list):
    if((type(target_port)==str) and (target_port=='' or target_port.lower()=='default')):target_port=161
    print(community_string, target_ip, target_port, oid_list)
    data = {}
    for oid_str in oid_list:
        data.update({oid_str:[]})

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
    # Send the SNMP request and receive the response
        try:
            #data[oid_str] = []
            current_id=0
            for error_indication, error_status, error_index, var_binds in snmp_walk:
                # Check for errors
                try:
                    if error_indication:
                        data[oid_str].append({"error": f"SNMP request failed: {error_indication}"})
                        break
                    elif error_status:
                        data[oid_str].append({"error": f"SNMP request failed: {error_status}"})
                        break
                    else:
                        # Print the result
                        for var_bind in var_binds:
                            try:
                                # data.append({"data": [x.prettyPrint() for x in var_bind]})
                                data[oid_str].append({var_bind[0].prettyPrint():var_bind[1].prettyPrint()})

                                #print(var_bind)
                            except KeyboardInterrupt:
                                sys.exit()
                    current_id+=1
                except KeyboardInterrupt:
                    break
        except Exception as e:
            data[oid_str].append({"error": str(e)})
        except KeyboardInterrupt:
            sys.exit()
    return data

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
    oid_str = sys.argv[3].replace(' ', '').split(',')
    print(snmp_comm(community_string, target_ip, target_port, oid_str))
