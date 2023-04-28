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
    # Send the SNMP request and receive the response
    try:
        for error_indication, error_status, error_index, var_binds in snmp_walk:
            # Check for errors
            try:
                if error_indication:
                    print(f'SNMP request failed: {error_indication}')
                    break
                elif error_status:
                    print(f'SNMP error: {error_status}')
                    break
                else:
                    # Print the result
                    for var_bind in var_binds:
                        try:
                            #print(f'SNMP response: {var_bind[0]} = {var_bind[1]}')
                            print(var_bind)
                        except KeyboardInterrupt:
                            sys.exit()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(str(e))
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
    snmp_comm(community_string, target_ip, target_port, oid_str)
