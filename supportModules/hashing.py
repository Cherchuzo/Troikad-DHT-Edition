import os
import random
import json
import time
import tkinter as tk


class Hashing():

    @staticmethod
    def hashService(files, filepath, publicIp, dht, txtLog):
        txtLog.insert(tk.INSERT, "\nINFO:HASH Inizio")
        chiaviFile = []
        for singleFile in files:
            time.sleep(5)
            if os.path.exists(filepath) and os.path.isfile(filepath+singleFile):
                chiave = str(random.randint(100000000, 999999999))
                print("\nChiave per file:"+singleFile+" = "+chiave)
                chiaviFile.append((chiave, singleFile))
                print(os.stat(filepath+singleFile).st_size)
            else:
                print("Errore hashing")

        txtLog.insert(tk.INSERT, "\nINFO:HASH Finito")
        txtLog.insert(tk.INSERT, "\nINFO:STORE in 30sec")
        time.sleep(30)
        
        txtLog.insert(tk.INSERT, "\nINFO:STORING")
        for singleFile in chiaviFile:
            dht[singleFile[0]] = [json.dumps({"ip":publicIp[0], "port":publicIp[1], "filename":singleFile[1], "metadata":[os.stat(filepath+singleFile[1]).st_size]}, ensure_ascii=False)]
            time.sleep(1)
        
        txtLog.insert(tk.INSERT, "\nINFO:STORED")