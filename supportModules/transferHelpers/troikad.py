import os
import socket
import tkinter as tk
import time
import json
from .transferHelper import ConnectionHelper
from ..crypto import DiffieHellman, chacha20poly1305
from .progressBar import progressBar as pb
import traceback

import base64 #to send bytes inside JSON


class TroikadFileHandler(object):

    @staticmethod
    def send(filepath, filename, connection, publicKey):     
        hellman = DiffieHellman()
        hellman.genKey(publicKey)
        sharedKey = hellman.getKey()
        nonce = base64.b64encode(os.urandom(12))
        nonce = nonce.decode('ascii')
        cipher = chacha20poly1305.ChaCha20Poly1305(sharedKey)
        if os.path.exists(filepath) and os.path.isfile(filepath+filename):
            try:
                sendFile = open(filepath+filename, 'rb')
                flag = True
                message = json.dumps({"operation_code":11, "address":None, "filename":filename, "options":[os.stat(filepath+filename).st_size, hellman.publicKey, nonce], "flag_buddy":None})
                if not ConnectionHelper.send(connection, message, False):
                    print("Errore in invio comando")
                    flag = False
            except IOError:
                print("IOError")
                message = json.dumps({"operation_code":12, "address":None, "filename":filename, "options":False, "flag_buddy":None})
                if not ConnectionHelper.send(connection, message, False):
                    print("Errore in invio comando")
                flag = False

            time.sleep(2)
            if flag:
                data = sendFile.read(5120)
                nonce = base64.b64decode(nonce)
                data = cipher.encrypt(nonce, data)

                flag = False
                while data:
                    if ConnectionHelper.sendBytes(connection, data, False):
                        data = sendFile.read(5120)

                        if data:
                            data = cipher.encrypt(nonce, data)
                        flag = True
                    else:
                        print("Errore in invio file: "+ filename)
                        flag = False
                        break
                if flag:
                    connection.shutdown(socket.SHUT_WR)
                sendFile.close()
        else:
            print("File Richiesto non esistente")
            message = json.dumps({"operation_code":12, "address":None, "filename":filename, "options":False, "flag_buddy":None})
            if not ConnectionHelper.send(connection, message, False):
                print("Errore in invio comando")
            
        connection.close()


    @staticmethod
    def request(filename, peer, diffie):
        try:
            tcpSocketPeer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpSocketPeer.settimeout(5)
            tcpSocketPeer.connect(peer)
            flag = True
        except:
            print("HOST: "+peer[0]+":"+str(peer[1])+"  non raggiungibile\n")
            tcpSocketPeer.close()
            flag = False
                
        if flag:
            message = json.dumps({"operation_code":10, "address":None, "filename":filename, "options":diffie.publicKey, "flag_buddy":None})
            if not ConnectionHelper.send(tcpSocketPeer, message, False):
                print("HOST: "+peer[0]+":"+str(peer[1])+"  errore avvenuto in invio\n")
                return False, None, None
            else:
                msg = ConnectionHelper.receive(tcpSocketPeer, 3096, False)
                try:
                    msg = json.loads(msg)
                except TypeError:
                    msg = None
                if msg != None and isinstance(msg["options"], list):
                    return True, msg, tcpSocketPeer
                else:
                    return False, None, None
        else:
            return False, None, None


    @staticmethod
    def download(fileStats, connection, parent, sharedKey, nonce):
        parent.geometry("300x100")
        progressBar = pb(parent, [0, 0, 0])

        f = open("incoming/{}".format(fileStats["filename"]), 'wb')

        cipher = chacha20poly1305.ChaCha20Poly1305(sharedKey)

        offset = 0
        realSize = fileStats["options"][0]
        networkReceived, networkSpeed = 0, 0
        second, start_time = 2, time.time()
        data, overData = ConnectionHelper.receiveBytes(connection, 6144, False)
        
        nonce = base64.b64decode(nonce)
        data = cipher.decrypt(nonce, data)

        currentSize = offset + len(data)
        flag = True
        while data and flag:
            try:
                f.write(data)
                
                if overData:
                    data, overData = ConnectionHelper.receiveBytes(connection, 6144, False, overData)
                else:
                    data, overData = ConnectionHelper.receiveBytes(connection, 6144, False)

                if data:
                    data = cipher.decrypt(nonce, data)
                currentSize += len(data)
                networkReceived += len(data)
            except:
                print("\n\nErrore durante la ricezione del file --- ")
                traceback.print_exc()
                f.close()
                connection.close()
                os.remove('incoming/'+fileStats["filename"])
                flag = False
                time.sleep(2)

            if int(time.time() - start_time) >= int(second):
                start_time = time.time()
                networkSpeed = networkReceived
                networkReceived = 0

            progressBar.progress([int((currentSize/realSize) * 100), networkSpeed, realSize - currentSize])

        if flag:        
            f.close()

        if os.path.isfile('incoming/'+fileStats["filename"]):
            print("File ricevuto correttamente!\n")
            time.sleep(2)
        else:
            print("Errore sconosciuto rilevato durante scrittura su disco\n")

        parent.destroy()
        time.sleep(3)