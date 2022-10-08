import tkinter as tk
from kad import DHT
from transferHelpers import TroikadFileHandler
from transferHelpers import ConnectionHelper
from threading import Thread
import random
import logging
import socket
import json
import os
import time

class Finestra(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        
        # GLOBAL VARIABLES
        self.HOST = "0.0.0.0"
        self.PORT = 2443

        self.globalBorderThicknessOut = 1
        self.globalBorderThicknessIn = 2
        self.sceltaMenu = tk.StringVar(value="   MENU   ")  # "MENU" è il valore di default dello spinner in questo caso quindi lo fa sembrare un menu dato che il menu si puo solo attaccare sopra alla finestra e quindi non sarebbe stato in linea con il resto
        self.enBtstrpVar = tk.StringVar(value="")
        self.enCercaVar = tk.StringVar(value="")
        self.imgInvio = tk.PhotoImage(file="Files/enterArrow.png")
        self.nomiFile=[]
        self.dimFile=[]
        self.fontiFile=[]
        self.tipiFile=[]

        self.dht = None
        self.buddy = False
        self.searchKey = None
        self.fileToDownload = None
        #self.replyMessage = None

        self.grid()
        self.CreaWidgets()
        
        if not os.path.exists("incoming"):
      	    os.mkdir("incoming")


    def BuddyServer(self, conn, client):
        while True:
            msg = ConnectionHelper.receive(conn, 2048, False)
            if msg != None:
                    msg = msg.decode('utf-8')
            else:
                self.buddy = False
                self.lblCompagnoVal.configure(text="In attesa")
                break

            msg = self.dht[msg]

            if not ConnectionHelper.send(conn, msg, False):
                self.buddy = False
                self.lblCompagnoVal.configure(text="In attesa")
                break


    def BuddyClient(self):
        time.sleep(10)
        while True:

            if self.buddy:
                self.btnInizia.config(state = "normal")
            else:
                self.btnInizia.config(state = "disabled")

            while not self.buddy:
                for peer in self.dht.peers():
                    flag = False
                    try:
                        tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcpSocketTest.settimeout(3)
                        tcpSocketTest.connect((peer.get("host"), peer.get("port")))
                        flag = True
                    except:
                        print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  non raggiungibile\n")
                        tcpSocketTest.close()
                    
                    if flag:
                        message = json.dumps({"operation_code":0, "address":(None, 2442), "filename":None, "options":None, "flag_buddy":None})
                        if ConnectionHelper.send(tcpSocketTest, message, False):
                            metadata = ConnectionHelper.receive(tcpSocketTest, 2048, False)
                            if metadata != None:
                                metadata = metadata.decode('utf-8')
                                jsonData = json.loads(metadata)
                                if jsonData["operation_code"] == 1 and jsonData["flag_buddy"] == None:
                                    self.buddy = True
                                else:
                                    tcpSocketTest.shutdown(socket.SHUT_WR)
                                    tcpSocketTest.close()
                        
                                break
                            else:
                                print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  errore avvenuto in ricezione\n")
                        else:
                            print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  errore avvenuto in invio\n")

                time.sleep(5)

            if self.buddy:
                self.btnInizia.config(state = "normal")
            else:
                self.btnInizia.config(state = "disabled")

            while self.buddy:
                if self.searchKey != None:
                    if not ConnectionHelper.send(tcpSocketTest, self.searchKey, False):
                        self.searchKey = None
                        self.buddy = False
                        self.lblCompagnoVal.configure(text="Ricerca")
                        break

                    self.searchKey = None

                    msg = ConnectionHelper.receive(tcpSocketTest, 2048, False)
                    if msg != None:
                        msg = msg.decode('utf-8')
                    else:
                        self.buddy = False
                        self.lblCompagnoVal.configure(text="Ricerca")
                        break
                else:
                    time.sleep(2)
                
        
        
    def HashService(self, files, filepath, publicIp):
        self.txtLog.insert(tk.INSERT, "\nINFO:HASH Inizio")
        chiaviFile = []
        for singleFile in files:
            time.sleep(5)
            if os.path.exists(filepath) and os.path.isfile(filepath+singleFile):
                chiave = str(random.randint(100000000, 999999999))
                print("\nChiave per file:"+singleFile+" = "+chiave)
                chiaviFile.append((chiave, singleFile))
                print(os.stat(filepath+singleFile).st_size)

        self.txtLog.insert(tk.INSERT, "\nINFO:HASH Finito")
        self.txtLog.insert(tk.INSERT, "\nINFO:STORE in 90sec")
        time.sleep(90)
        
        self.txtLog.insert(tk.INSERT, "\nINFO:STORING")
        for singleFile in chiaviFile:
            self.dht[singleFile[0]] = [json.dumps({"ip":publicIp, "port":2442, "filename":singleFile[1], "metadata":[os.stat(filepath+singleFile[1]).st_size]}, ensure_ascii=False)]
            time.sleep(1)
        
        self.txtLog.insert(tk.INSERT, "\nINFO:STORED")


    def TcpFirewallTester(self, host, port):
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


    def TcpFirewallForwarder(self, addressJson, clientPublicInfo):
        if not self.dht.peers():    #this shouldn't never happen
            flag = False
            try:
                tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpSocketTest.settimeout(3)
                tcpSocketTest.connect((clientPublicInfo[0], addressJson[1]))
                flag = True
            except:
                print("HOST: "+clientPublicInfo[0]+":"+str(addressJson[1])+"  non raggiungibile\n")
                tcpSocketTest.close()
                
            if flag:
                message = json.dumps({"operation_code":7, "address":(clientPublicInfo[0], addressJson[1]), "filename":None, "options":None, "flag_buddy":None})
                if not ConnectionHelper.send(tcpSocketTest, message, True):
                    print("HOST: "+clientPublicInfo[0]+":"+str(addressJson[1])+"  errore avvenuto in invio\n")
        else:
            for peer in self.dht.peers():
                flag = False

                if peer.get("port") is not clientPublicInfo[1]:
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

    
    def FileSender(self, connection, data, filepath):
        filename = data["filename"]
        message = json.dumps({"operation_code":11, "address":None, "filename":filename, "options":None, "flag_buddy":None})
        if ConnectionHelper.send(connection, message, False):
            TroikadFileHandler.send(filepath, filename, connection)
        else:
            print("Connessione abortita(errore)")


    def FileRequest(self):
        while True:
            if self.fileToDownload != None:
                download_window = tk.Toplevel(self)
                download_window.geometry("200x50")
                download.resizable(0, 0)
                tmpLabel = tk.Label(search_window, text = "Contattando peer...")
                tmpLabel.pack()


    def TcpClient(self):
        while True:
            if self.searchKey != None:
                search_window = tk.Toplevel(self)
                search_window.geometry("200x50")
                search_window.resizable(0, 0)
                tmpLabel = tk.Label(search_window, text = "Ricerca...")
                tmpLabel.pack()
                try:
                    replyMessage = self.dht[self.searchKey]
                    flag = True
                except KeyError:
                    flag = False
                    
                if flag:
                    tmpLabel.config(text = "Valore trovato")
                    time.sleep(2)
                    search_window.destroy()
                    print(replyMessage)
                    jsonReply = json.loads(replyMessage[0])

                    self.nomiFile[0].config(state = "normal", text = jsonReply["filename"])
                    self.dimFile[0].config(text = jsonReply["metadata"][0])
                    self.btnPulisci.config(state = "normal", command = self.CleanButton)
                else:
                    tmpLabel.config(text = "Valore non trovato")
                    time.sleep(2)
                    search_window.destroy()

                self.searchKey = None
            else:
                time.sleep(2)
    

    def TcpServer(self):
        time.sleep(2)

        try:
            tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            localAddress = ("0.0.0.0", self.PORT)
            tcpServer.bind(localAddress)
            print("TCP:In avvio su:{}  Porta:{}".format(*localAddress))
            self.lblTcpVal.configure(text="Connesso (Insicuro)")
        except:
            print("Socket non avviato/inizializzato!")
            self.lblTcpVal.configure(text="ERROR")
            self.txtLog.insert(tk.INSERT, "\nERRORE:TCP error")
            self.txtLog.insert(tk.INSERT, "\nERRORE:riavvia")
            
        tcpServer.listen(1)
        globalFlag = True
        time.sleep(2)
        #while True:
            #tcpServer.settimeout(30)

            #for peer in self.dht.peers():
                #flag = False
                #try:
                    #tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #tcpSocketTest.settimeout(3)
                    #tcpSocketTest.connect((peer.get("host"), peer.get("port")))
                    #flag = True
                #except:
                    #print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  non raggiungibile\n")
                    #tcpSocketTest.close()
                
                #if flag:
                   # message = json.dumps({"operation_code":5, "address":(None, 2442), "filename":None, "options":None, "flag_buddy":None})
                    #if not ConnectionHelper.send(tcpSocketTest, message, True):
                       # print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  errore avvenuto durante invio\n")
                    #else:
                        #break
            
            #try:
                #connection, client_address = tcpServer.accept()
                #publicIp = connection.recv(2048)
                #publicIp = publicIp.decode("utf-8")
                #publicIp = json.loads(publicIp)
                #publicIp = publicIp["address"][0]
                #flag = True
            #except TimeoutError:
                #tcpServer.close()
                #self.lblTcpVal.configure(text="Firewalled")
                #self.lblKadVal.configure(text="Firewalled")
                #self.lblCompagnoVal.configure(text="Ricerca")
                #self.txtLog.insert(tk.INSERT, "\nWARN:TCP sotto NAT")
                #self.txtLog.insert(tk.INSERT, "\nWARN:TCP NO CONDIVISIONE")
                #tcpBuddyFinder = Thread(target=self.BuddyClient)
                #tcpBuddyFinder.start()
                #flag = False
                
            #if flag:
                #self.txtLog.insert(tk.INSERT, "\nTCP:Connesso")
                #self.lblTcpVal.configure(text="Connesso")
                #self.lblCompagnoVal.configure(text="In attesa")

                #self.btnInizia.config(state = "normal")
                
                #tcpServer.settimeout(None)
                #globalFlag = True
                #break
            #else:
                #break
       
        if globalFlag:
            tcpServer.listen(4)
            files = os.listdir("incoming/")
            filepath = "incoming/"
        
            if len(files) != 0:
                hashFiles = Thread(target=self.HashService, args = (files,filepath, "192.168.1.13"))
                hashFiles.start()

            tcpClient = Thread(target=self.TcpClient)
            tcpClient.start()

            while globalFlag:
                connection, client_address = tcpServer.accept()
                print('connessione da {} porta:{}'.format(*client_address))
                metadata = ConnectionHelper.receive(connection, 2048, False)
                if metadata != None:
                    metadata = metadata.decode('utf-8')
                    jsonData = json.loads(metadata)

                    if not self.buddy and jsonData["operation_code"] == 0:
                        self.buddy = True
                        self.lblCompagnoVal.configure(text="Offrendo")

                        message = json.dumps({"operation_code":1, "address":None, "filename":None, "options":None, "flag_buddy":None})
                        if ConnectionHelper.send(connection, message, False):
                            buddyThread = Thread(target=self.BuddyServer, args = (connection, client_address))
                            buddyThread.start()
                        else:
                            self.buddy = False

                    elif jsonData["operation_code"] == 0:
                        if buddyThread.is_alive():
                            message = json.dumps({"operation_code":1, "address":None, "filename":None, "options":None, "flag_buddy":1})
                            ConnectionHelper.send(connection, message, True)
                    elif jsonData["operation_code"] == 5:
                        tcpForwarder = Thread(target=self.TcpFirewallForwarder, args = (jsonData["address"], client_address))
                        tcpForwarder.start()
                    elif jsonData["operation_code"] == 6:
                        tcpTester = Thread(target=self.TcpFirewallTester, args = (jsonData["address"]))
                        tcpTester.start()
                    #elif jsonData["operation_code"] == 10:
                        #fileSender = Thread(target=self.FileSender, args = (connection, jsonData, filepath))
                        #fileSender.start()
                else:
                    print("HOST: "+client_address[0]+":"+str(client_address[1])+"  errore avvenuto durante ricezione\n")

            
    def DhtService(self, bootstrapIp):
        self.btnBtstrp.config(state = "disabled")
        host = "0.0.0.0"
        port = self.PORT

        remoteHost = bootstrapIp.split(":")

        self.txtLog.insert(tk.INSERT, "Connessione KAD...")

        if bootstrapIp == "" or not ":" in bootstrapIp:
            remoteHost = []
            remoteHost.insert(0, "localhost")
            remoteHost.insert(1, 10000)
        
        self.dht = DHT(host, port)
        time.sleep(2)

        if False:
            self.txtLog.insert(tk.INSERT, "\nKAD:remote host unreachable")
            self.txtLog.insert(tk.INSERT, "\nERRORE:riavvia")
            self.lblKadVal.configure(text="ERROR")
        else:
            self.txtLog.insert(tk.INSERT, "\nKAD:Connesso")
            self.lblKadVal.configure(text="Connesso (Insicuro)")
            self.lblTcpVal.configure(text="Test")

            tcpService = Thread(target=self.TcpServer)
            tcpService.start()


    def SearchButton(self, key):
        self.searchKey = key


    def CleanButton(self):
        for element in range(len(self.nomiFile)):
            self.nomiFile[element].config(text=" ", state="disabled", bg="white")
            self.dimFile[element].config(text=" ", state="disabled", bg="white")
            self.fontiFile[element].config(text=" ", state="disabled", bg="white")
            self.tipiFile[element].config(text=" ", state="disabled", bg="white")

        self.btnPulisci.config(state = "disabled")

    
    def DownloadButton(self, pos):
        self.fileToDownload = self.nomiFile[pos]["text"]
            

    def Seleziona(self, pos):
        for i in range(15):
            if i==pos-1:
                self.btnDownload.config(state = "normal", command = lambda: self.DownloadButton(i))

                self.nomiFile[i].config(bg="#00FF00")
                self.dimFile[i].config(bg="#00FF00")
                self.fontiFile[i].config(bg="#00FF00")
                self.tipiFile[i].config(bg="#00FF00")
            else:
                self.nomiFile[i].config(bg="white")
                self.dimFile[i].config(bg="white")
                self.fontiFile[i].config(bg="white")
                self.tipiFile[i].config(bg="white")

    def CreaWidgets(self):
        # Frames
        #   ROW 1
        self.frameRow1 = tk.Frame(self, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameRow1.grid(row=1, column=0)
        self.frameBtstrp = tk.Frame(self.frameRow1, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut,bd=0)
        self.frameBtstrp.grid(row=0, column=1, sticky="nesw")
        #   ROW 2
        self.frameRow2 = tk.Frame(self, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameRow2.grid(row=2, column=0, sticky="nesw")
        self.frameCerca = tk.Frame(self.frameRow2, bd=0)
        self.frameCerca.grid(row=0, column=1, sticky="nesw")
        self.frameOptCerca = tk.Frame(self.frameRow2, bd=0)
        self.frameOptCerca.grid(row=1, column=1, sticky="nesw")
        #   ROW 3
        self.frameRow3 = tk.Frame(self, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameRow3.grid(row=3, column=0, sticky="nesw")
        self.frameFiles=tk.Frame(self.frameRow3, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameFiles.grid(row=0, column=0, sticky="w")
        self.frameBorderFile=tk.Frame(self.frameFiles, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameBorderFile.grid(row=3, column=1, columnspan=4, sticky="nesw", ipady=0, ipadx=0)
        self.frameNomiFile=tk.Frame(self.frameBorderFile, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameNomiFile.grid(row=3, column=1)
        self.frameDimFile=tk.Frame(self.frameBorderFile, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameDimFile.grid(row=3, column=2)
        self.frameFontiFile=tk.Frame(self.frameBorderFile, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameFontiFile.grid(row=3, column=3)
        self.frameTipiFile=tk.Frame(self.frameBorderFile, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameTipiFile.grid(row=3, column=4)
        self.frameLog=tk.Frame(self.frameRow3, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameLog.grid(row=0, column=1, sticky="nesw")
        #   ROW 4
        self.frameRow4=tk.Frame(self, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameRow4.grid(row=4, column=0, sticky="nesw")
        self.frameTcpKad=tk.Frame(self.frameRow4, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameTcpKad.grid(row=0, column=0, sticky="nesw")
        self.frameUpDown=tk.Frame(self.frameRow4, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameUpDown.grid(row=0, column=1, sticky="nesw")
        self.frameBorderUpDown=tk.Frame(self.frameUpDown, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameBorderUpDown.grid(row=1, column=2, sticky="nesw")
        self.frameCompagno = tk.Frame(self.frameRow4, highlightbackground="black", highlightthickness=self.globalBorderThicknessOut, bd=0)
        self.frameCompagno.grid(row=0, column=2, sticky="nesw")

        #ROW 1
        #   COLUMN 1
        #       MENU
        self.Menu = tk.OptionMenu(self.frameRow1, self.sceltaMenu, "Option1", "Option2", "Option3")
        self.Menu.config(indicatoron=0, bd=self.globalBorderThicknessOut, relief="solid", highlightthickness=0, font=('Helvetica', 9, 'bold'))
        self.Menu.grid(row=0, column=0, sticky="nesw", pady=0, padx=0)

        #   COLUMN 2
        #       Bootstrap
        self.lblBtstrp = tk.Label(self.frameBtstrp, text=" BOOTSTRAP:  ", highlightthickness=0, font=('Helvetica', 9, 'bold'))
        self.lblBtstrp.grid(row=0, column=1, pady=0, padx=3)
        self.enBtstrp = tk.Entry(self.frameBtstrp, textvar=self.enBtstrpVar, width=45, bd=self.globalBorderThicknessIn, relief="solid", justify="center")
        self.enBtstrp.grid(row=0, column=2, pady=4, padx=5)
        self.btnBtstrp = tk.Button(self.frameBtstrp, image=self.imgInvio, command= lambda: self.DhtService(self.enBtstrpVar.get()), bd=self.globalBorderThicknessIn, relief="solid")
        self.btnBtstrp.grid(row=0, column=3, pady=0, padx=10)

        #ROW 2
        #   fillers
        tk.Label(self.frameCerca, text="    ").grid(row=0, column=4)
        tk.LabelFrame(self.frameRow2, text="", highlightbackground="black", highlightthickness=2, bd=0).grid(row=0, column=0, rowspan=2, sticky="nesw")
        tk.LabelFrame(self.frameRow2, text=" ", width=2, fg="black", bg="black", highlightbackground="black", highlightthickness=30, bd=0).grid(row=0, column=2, rowspan=2, sticky="nesw")
        tk.LabelFrame(self.frameRow2, text="", highlightbackground="black", highlightthickness=2, bd=0).grid(row=0, column=4, rowspan=2, sticky="nesw")

        #   COLUMN 1
        #       Cerca
        self.lblCerca = tk.Label(self.frameCerca, text=" CERCA:     ", font=('Helvetica', 9, 'bold'))
        self.lblCerca.grid(row=0, column=0, sticky="nesw")
        self.enCerca = tk.Entry(self.frameCerca, textvariable=self.enCercaVar, width=45, bd=self.globalBorderThicknessIn, relief="solid", justify="center")
        self.enCerca.grid(row=0, column=1, columnspan=3, pady=3, padx=0)

        #       Options
        self.btnInizia = tk.Button(self.frameOptCerca, text="INIZIA", command= lambda: self.SearchButton(self.enCercaVar.get()), bd=self.globalBorderThicknessIn,relief="solid", state="disabled")
        self.btnInizia.grid(row=1, column=0, pady=5, padx=15)
        self.btnDownload = tk.Button(self.frameOptCerca, text="DOWNLOAD", command=None, bd=self.globalBorderThicknessIn,relief="solid", state="disabled")
        self.btnDownload.grid(row=1, column=1, pady=5, padx=15)
        self.btnPulisci = tk.Button(self.frameOptCerca, text="PULISCI", command= lambda: self.CleanButton(), bd=self.globalBorderThicknessIn,relief="solid", state="disabled")
        self.btnPulisci.grid(row=1, column=2, pady=5, padx=15)
        self.btnFiltra = tk.Button(self.frameOptCerca, text="FILTRA", command=None, bd=self.globalBorderThicknessIn,relief="solid", state="disabled")
        self.btnFiltra.grid(row=1, column=3, pady=5, padx=15)

        #   COLUMN 2
        #       #Filtri
        self.lblFiltri = tk.Label(self.frameRow2, text="FILTRI", borderwidth=0, relief="solid", font=('Helvetica', 12, 'bold'))
        self.lblFiltri.grid(row=0, column=3, rowspan=2, pady=0, ipadx=40, sticky="nesw")

        #ROW 3
        #   fillers
        tk.Label(self.frameFiles, text="               ", font=('Helvetica', 1, 'bold')).grid(row=0, column=0)
        tk.Label(self.frameFiles, text="     ", font=('Helvetica', 7, 'bold')).grid(row=4, column=5)
        tk.Label(self.frameLog, text="      ", font=('Helvetica', 1, 'bold')).grid(row=0, column=0)
        tk.Label(self.frameLog, text="      ", font=('Helvetica', 1, 'bold')).grid(row=0, column=2)

        #   COLUMN 1
        #       Tabella Risultati
        self.lblRisultati = tk.Label(self.frameFiles, text=" RISULTATI ", borderwidth=2, relief="solid")
        self.lblRisultati.grid(row=1, column=1, sticky="w")

        self.lblNFile = tk.Label(self.frameBorderFile, text="Nome File                                        ", anchor="w", borderwidth=1, relief="solid")
        self.lblNFile.grid(row=2, column=1)

        self.lblDi = tk.Label(self.frameBorderFile, text="   Dim .   ", anchor="center", borderwidth=1, relief="solid")
        self.lblDi.grid(row=2, column=2)

        self.lblFont = tk.Label(self.frameBorderFile, text="  Fonti  ", anchor="center", borderwidth=1, relief="solid")
        self.lblFont.grid(row=2, column=3)

        self.lblTip = tk.Label(self.frameBorderFile, text="  Tipo   ", anchor="center", borderwidth=1, relief="solid")
        self.lblTip.grid(row=2, column=4)

        #PORCAMADONNA :-/
        #per poterli cliccare devi mettere 'state="normal"' quando inserisci i file
        btnN1 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", width=24, bd=0, command=lambda: self.Seleziona(1))
        btnN2 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(2))
        btnN3 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(3))
        btnN4 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(4))
        btnN5 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(5))
        btnN6 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(6))
        btnN7 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(7))
        btnN8 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(8))
        btnN9 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(9))
        btnN10 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(10))
        btnN11 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(11))
        btnN12 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(12))
        btnN13 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(13))
        btnN14 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(14))
        btnN15 = tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(15))
        self.nomiFile.append(btnN1)
        self.nomiFile.append(btnN2)
        self.nomiFile.append(btnN3)
        self.nomiFile.append(btnN4)
        self.nomiFile.append(btnN5)
        self.nomiFile.append(btnN6)
        self.nomiFile.append(btnN7)
        self.nomiFile.append(btnN8)
        self.nomiFile.append(btnN9)
        self.nomiFile.append(btnN10)
        self.nomiFile.append(btnN11)
        self.nomiFile.append(btnN12)
        self.nomiFile.append(btnN13)
        self.nomiFile.append(btnN14)
        self.nomiFile.append(btnN15)

        btnDim1 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", width=6, bd=0, command=lambda: self.Seleziona(1))
        btnDim2 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(2))
        btnDim3 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(3))
        btnDim4 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(4))
        btnDim5 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(5))
        btnDim6 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(6))
        btnDim7 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(7))
        btnDim8 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(8))
        btnDim9 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(9))
        btnDim10 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(10))
        btnDim11 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(11))
        btnDim12 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(12))
        btnDim13 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(13))
        btnDim14 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(14))
        btnDim15 = tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(15))
        self.dimFile.append(btnDim1)
        self.dimFile.append(btnDim2)
        self.dimFile.append(btnDim3)
        self.dimFile.append(btnDim4)
        self.dimFile.append(btnDim5)
        self.dimFile.append(btnDim6)
        self.dimFile.append(btnDim7)
        self.dimFile.append(btnDim8)
        self.dimFile.append(btnDim9)
        self.dimFile.append(btnDim10)
        self.dimFile.append(btnDim11)
        self.dimFile.append(btnDim12)
        self.dimFile.append(btnDim13)
        self.dimFile.append(btnDim14)
        self.dimFile.append(btnDim15)

        btnFonti1 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", width=5, bd=0, command=lambda: self.Seleziona(1))
        btnFonti2 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(2))
        btnFonti3 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(3))
        btnFonti4 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(4))
        btnFonti5 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(5))
        btnFonti6 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(6))
        btnFonti7 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(7))
        btnFonti8 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(8))
        btnFonti9 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(9))
        btnFonti10 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(10))
        btnFonti11 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(11))
        btnFonti12 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(12))
        btnFonti13 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(13))
        btnFonti14 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(14))
        btnFonti15 = tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(15))
        self.fontiFile.append(btnFonti1)
        self.fontiFile.append(btnFonti2)
        self.fontiFile.append(btnFonti3)
        self.fontiFile.append(btnFonti4)
        self.fontiFile.append(btnFonti5)
        self.fontiFile.append(btnFonti6)
        self.fontiFile.append(btnFonti7)
        self.fontiFile.append(btnFonti8)
        self.fontiFile.append(btnFonti9)
        self.fontiFile.append(btnFonti10)
        self.fontiFile.append(btnFonti11)
        self.fontiFile.append(btnFonti12)
        self.fontiFile.append(btnFonti13)
        self.fontiFile.append(btnFonti14)
        self.fontiFile.append(btnFonti15)

        btnTipo1 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", width=5, bd=0, command=lambda: self.Seleziona(1))
        btnTipo2 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(2))
        btnTipo3 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(3))
        btnTipo4 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(4))
        btnTipo5 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(5))
        btnTipo6 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(6))
        btnTipo7 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(7))
        btnTipo8 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(8))
        btnTipo9 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(9))
        btnTipo10 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(10))
        btnTipo11 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(11))
        btnTipo12 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(12))
        btnTipo13 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(13))
        btnTipo14 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(14))
        btnTipo15 = tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(15))
        self.tipiFile.append(btnTipo1)
        self.tipiFile.append(btnTipo2)
        self.tipiFile.append(btnTipo3)
        self.tipiFile.append(btnTipo4)
        self.tipiFile.append(btnTipo5)
        self.tipiFile.append(btnTipo6)
        self.tipiFile.append(btnTipo7)
        self.tipiFile.append(btnTipo8)
        self.tipiFile.append(btnTipo9)
        self.tipiFile.append(btnTipo10)
        self.tipiFile.append(btnTipo11)
        self.tipiFile.append(btnTipo12)
        self.tipiFile.append(btnTipo13)
        self.tipiFile.append(btnTipo14)
        self.tipiFile.append(btnTipo15)

        self.frameBorderFile.grid(row=3, column=1, columnspan=4, sticky="nesw")

        for i in range(15):
            self.nomiFile[i].grid(row=i, column=0, sticky="nesw", ipadx=2)
            self.dimFile[i].grid(row=i, column=0, sticky="nesw")
            self.fontiFile[i].grid(row=i, column=0, sticky="nesw")
            self.tipiFile[i].grid(row=i, column=0, sticky="nesw")

        #   COLUMN 2
        #       #Log
        self.lblLog=tk.Label(self.frameLog, text=" LOG    ", anchor="w", borderwidth=2, relief="solid")
        self.lblLog.grid(row=1, column=1, sticky="w")
        self.txtLog=tk.Text(self.frameLog, width=13, height=19, font=('Helvetica', 11, 'bold'), bd=2, relief="solid")
        self.txtLog.grid(row=2, column=1)

        #ROW 4
        #   fillers
        tk.Label(self.frameUpDown, text="", font=('Helvetica', 2, 'bold')).grid(row=0)
        tk.Label(self.frameUpDown, text="", font=('Helvetica', 1, 'bold')).grid(row=2)

        #   COLUMN 1
        #       TCP
        self.lblTcp=tk.Label(self.frameTcpKad, text=" TCP: ")
        self.lblTcp.grid(row=0, column=0)
        self.lblTcpVal=tk.Label(self.frameTcpKad, text="", width=20)
        self.lblTcpVal.grid(row=0, column=1)
        #       KAD
        self.lblKad=tk.Label(self.frameTcpKad, text=" KAD: ")
        self.lblKad.grid(row=1, column=0)
        self.lblKadVal = tk.Label(self.frameTcpKad, text="")
        self.lblKadVal.grid(row=1, column=1)

        #   COLUMN 2
        #       Up
        self.lblUp=tk.Label(self.frameUpDown, text=" UP: ")
        self.lblUp.grid(row=1, column=0)
        self.lblUpVal = tk.Label(self.frameUpDown, text="", width=8)
        self.lblUpVal.grid(row=1, column=1)
        #       Down
        self.lblDown = tk.Label(self.frameUpDown, text="  DOWN: ")
        self.lblDown.grid(row=1, column=3)
        self.lblDownVal = tk.Label(self.frameUpDown, text="", width=6)
        self.lblDownVal.grid(row=1, column=4)

        #   COLUMN 3
        #       Compagno
        self.lblCompagno=tk.Label(self.frameCompagno, text="  COMPAGNO:         ")
        self.lblCompagno.grid(row=0, column=0)
        self.lblCompagnoVal = tk.Label(self.frameCompagno, text="")
        self.lblCompagnoVal.grid(row=1, column=0)

root=Finestra()
root.mainloop()
