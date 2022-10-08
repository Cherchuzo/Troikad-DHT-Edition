import socket
import json
from ..transferHelpers import ConnectionHelper


class TCPFirewall(object):

    @staticmethod
    def TcpFirewallTester(host, port):
        flag = False
        try:
            tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpSocketTest.settimeout(3)
            tcpSocketTest.connect((host, port))
            flag = True
        except:
            print("HOST: "+host+":"+str(port)+"  TEST fallito\n")
            tcpSocketTest.close()
                
        if flag:
            message = json.dumps({"operation_code":7, "address":(host, port), "filename":None, "options":None, "flag_buddy":None})
            if not ConnectionHelper.send(tcpSocketTest, message, True):
                print("HOST: "+host+":"+str(port)+"  errore avvenuto in invio\n")

    @staticmethod
    def TcpFirewallForwarder(addressJson, clientPublicInfo, peerList):
        for peer in peerList:
            flag = False

            if (peer.get("port"), peer.get("ip")) != (clientPublicInfo[1], clientPublicInfo[0]):
                try:
                    tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcpSocketTest.settimeout(3)
                    tcpSocketTest.connect((peer.get("host"), peer.get("port")))
                    flag = True
                except:
                    print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  non raggiungibile\n")
                    tcpSocketTest.close()
            
                if flag:
                    message = json.dumps({"operation_code":6, "address":(clientPublicInfo[0], addressJson[1]), "filename":None, "options":None, "flag_buddy":None})
                    if not ConnectionHelper.send(tcpSocketTest, message, True):
                        print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  errore avvenuto in invio\n")
                    else:
                        break