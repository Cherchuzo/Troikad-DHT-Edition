import tkinter as tk
from kad import DHT # Libreria per il protocollo P2P Kademlia
from supportModules.transferHelpers import TroikadFileHandler, ConnectionHelper, Utils  # Moduli (TroikadFileHandler per la gestione trasferimenti | ConnectionHelper per le connessioni a basso livello | Utils per delle utility)
from supportModules.TCPTools import TCPFirewall # Modulo per test dei client che richiedono controllo Firewall/NAT
from supportModules.hashing import Hashing  # Modulo per generare le chiavi per i file condivisi
from supportModules.crypto import DiffieHellman # Diffiehellman key exchange protocollo
from threading import Thread
import socket, os
import json, time

import re   #RegEx module

class Finestra(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, name="troikad")
        
        # GLOBAL VARIABLES
        self.HOST = "127.0.0.1"
        self.PORT = 2442

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
        self.peerFile=[]

        self.dht = None     # Attributo contenente poi una instanza della classe DHT
        self.buddy = False  # Variabile booleana per controllo presenza del Compagno
        self.searchKey = None
        self.fileToDownload = None

        self.grid()
        self.CreaWidgets()
        
        if not os.path.exists("incoming"):
            os.mkdir("incoming")    # Crea la cartella se non esiste già


    def BuddyServer(self, conn):    # Metodo per gestione del compagno connesso
        while True:
            msg = ConnectionHelper.receive(conn, 2048, False)
            if msg != None:
                pass
            else:
                self.buddy = False
                self.lblCompagnoVal.configure(text="In attesa")
                break

            try:
                msg = self.dht[msg]
                print(msg)
            except KeyError:
                msg = "None"

            if not ConnectionHelper.send(conn, msg, False):
                self.buddy = False
                self.lblCompagnoVal.configure(text="In attesa")
                break


    def BuddyClient(self):  # Metodo per ricerca e gestione del compagno a cui si è connessi
        time.sleep(10)
        while True:

            if self.buddy:
                self.btnInizia.config(state = "normal")
                self.lblCompagnoVal.configure(text="Connesso")
            else:
                self.btnInizia.config(state = "disabled")
                self.lblCompagnoVal.configure(text="Ricerca")

            while not self.buddy:
                for peer in self.dht.peers():
                    flag = False
                    try:
                        tcpSocketTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcpSocketTest.settimeout(3)
                        if (peer.get("host"), peer.get("port")) != (self.HOST, self.PORT):
                            tcpSocketTest.connect((peer.get("host"), peer.get("port")))
                        flag = True
                    except:
                        print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  non raggiungibile\n")
                        tcpSocketTest.close()
                    
                    if flag:
                        message = json.dumps({"operation_code":0, "address":(self.HOST, self.PORT), "filename":None, "options":None, "flag_buddy":None})
                        if ConnectionHelper.send(tcpSocketTest, message, False):
                            metadata = ConnectionHelper.receive(tcpSocketTest, 2048, False)
                            if metadata != None:
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
                self.lblCompagnoVal.configure(text="Connesso")
            else:
                self.btnInizia.config(state = "disabled")
                self.lblCompagnoVal.configure(text="Ricerca")

            while self.buddy:
                if self.searchKey != None:
                    search_window = tk.Toplevel(self)
                    search_window.title("Ricerca files")
                    search_window.geometry("200x50")
                    search_window.resizable(0, 0)
                    tmpLabel = tk.Label(search_window, text = "Ricerca...")
                    tmpLabel.pack()
                    if not ConnectionHelper.send(tcpSocketTest, self.searchKey, False):
                        self.searchKey = None
                        self.buddy = False
                        self.lblCompagnoVal.configure(text="Ricerca")
                        break

                    self.searchKey = None

                    msg = ConnectionHelper.receive(tcpSocketTest, 2048, False)
                    if msg != None and msg != "None":
                        tmpLabel.config(text = "Corrispondenza trovata")
                        time.sleep(2)
                        search_window.destroy()
                        print(msg)
                        jsonReply = json.loads(msg[0])

                        self.nomiFile[0].config(state = "normal", text = jsonReply["filename"])
                        self.dimFile[0].config(text = Utils.humansizeBytes(jsonReply["metadata"][0]))
                        self.fontiFile[0].config(text = "1")
                        self.peerFile.append((jsonReply["ip"], jsonReply["port"]))
                        self.btnPulisci.config(state = "normal", command = self.CleanButton)

                        fileDownloader = Thread(target=self.FileRequest)
                        fileDownloader.start()
                    else:
                        tmpLabel.config(text = "Connessione con compagno persa")
                        time.sleep(2)
                        search_window.destroy()

                        self.buddy = False
                    self.searchKey = None
                else:
                    time.sleep(2)


    def FileSender(self, connection, data, filepath):   # Metodo che avvia l'upload del file richiesto
        filename = data["filename"]
        TroikadFileHandler.send(filepath, filename, connection, data["options"])


    def FileRequest(self):  # Medoto che richiede le info necessarie per il download del file richiesto e lo inizia
        while True:
            if self.fileToDownload != None:
                tmpFileStats = self.fileToDownload
                self.fileToDownload = None
                print("FileRequest")
                download_window = tk.Toplevel(self)
                download_window.title("Ricerca peer")
                download_window.geometry("200x100")
                download_window.resizable(0, 0)
                download_window.title("Download di "+tmpFileStats[0]+"")
                tmpLabel = tk.Label(download_window, text = "Contattando peer...")
                tmpLabel.pack()

                hellman = DiffieHellman()
                result, fileStats, connection = TroikadFileHandler.request(tmpFileStats[0], (tmpFileStats[1], tmpFileStats[2]), hellman)
                if result:
                    time.sleep(1)
                    tmpLabel.destroy()
                    hellman.genKey(fileStats["options"][1])
                    sharedKey = hellman.getKey()
                    download_window.title("Download di "+tmpFileStats[0]+" in corso...")
                    TroikadFileHandler.download(fileStats, connection, download_window, sharedKey, fileStats["options"][2])
                else:
                    tmpLabel.config(text = "Peer non raggiungibile")
                    time.sleep(2)
                    download_window.destroy()
                    #far partire di nuovo hashservice
                
                self.fileToDownload = None
            else:
                time.sleep(2)


    def TcpClient(self):    # Metodo che controlla quando il tasto Inizia viene premuto, poi ricerca il valore nella rete Kademlia e stampa i metadati nella tabella
        while True:
            if self.searchKey != None:
                search_window = tk.Toplevel(self)
                search_window.title("Ricerca files")
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
                    tmpLabel.config(text = "Corrispondenza trovata")
                    time.sleep(2)
                    search_window.destroy()
                    print(replyMessage)
                    jsonReply = json.loads(replyMessage[0])

                    self.nomiFile[0].config(state = "normal", text = jsonReply["filename"])
                    self.dimFile[0].config(text = Utils.humansizeBytes(jsonReply["metadata"][0]))
                    self.fontiFile[0].config(text = "1")
                    self.peerFile.append((jsonReply["ip"], jsonReply["port"]))
                    self.btnPulisci.config(state = "normal", command = self.CleanButton)
                else:
                    tmpLabel.config(text = "Corrispondenza non trovata")
                    time.sleep(2)
                    search_window.destroy()

                self.searchKey = None

                fileDownloader = Thread(target=self.FileRequest)
                fileDownloader.start()
            else:
                time.sleep(2)
    

    def TcpServer(self):    # Metodo principale TCP che avvia TCPFirewall, Hashing e Buddy. Inoltre funge da handler per i pacchetti in arrivo smistandoli
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
        globalFlag = False
        time.sleep(2)
        while True:
            tcpServer.settimeout(30)

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
                    message = json.dumps({"operation_code":5, "address":(None, 2442), "filename":None, "options":None, "flag_buddy":None})
                    if not ConnectionHelper.send(tcpSocketTest, message, True):
                        print("HOST: "+peer.get("host")+":"+str(peer.get("port"))+"  errore avvenuto durante invio\n")
                    else:
                        break
            
            try:
                connection, client_address = tcpServer.accept()
                publicIp = []
                publicIp.append((json.loads((connection.recv(2048)).decode("utf-8")))["address"][0])
                publicIp.append(self.PORT)
                flag = True
            except (TimeoutError, socket.timeout):
                tcpServer.close()
                self.lblTcpVal.configure(text="Firewalled")
                self.lblKadVal.configure(text="Firewalled")
                self.lblCompagnoVal.configure(text="Ricerca")
                self.txtLog.insert(tk.INSERT, "\nWARN:TCP FIREWALLED")
                self.txtLog.insert(tk.INSERT, "\nWARN:TCP NO CONDIVISIONE")
                tcpBuddyFinder = Thread(target=self.BuddyClient)
                tcpBuddyFinder.start()
                flag = False
                
            if flag:
                self.txtLog.insert(tk.INSERT, "\nTCP:Connesso")
                self.lblTcpVal.configure(text="Connesso")
                self.lblCompagnoVal.configure(text="In attesa")

                self.btnInizia.config(state = "normal")
                
                tcpServer.settimeout(None)
                globalFlag = True
                break
            else:
                break
       
        if globalFlag:
            tcpServer.listen(10)
            files = os.listdir("incoming/")
            filepath = "incoming/"
        
            if len(files) != 0:
                hashFiles = Thread(target=Hashing.hashService, args = (files, filepath, publicIp, self.dht, self.txtLog))
                hashFiles.start()

            tcpClient = Thread(target=self.TcpClient)
            tcpClient.start()

            while globalFlag:
                connection, client_address = tcpServer.accept()
                print('connessione da {} porta:{}'.format(*client_address))
                metadata = ConnectionHelper.receive(connection, 2048, False)
                if metadata != None:
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
                        tcpForwarder = Thread(target=TCPFirewall.TcpFirewallForwarder, args = (jsonData["address"], client_address, self.dht.peers()))
                        tcpForwarder.start()
                    elif jsonData["operation_code"] == 6:
                        tcpTester = Thread(target=TCPFirewall.TcpFirewallTester, args = (jsonData["address"]))
                        tcpTester.start()
                    elif jsonData["operation_code"] == 10:
                        fileSender = Thread(target=self.FileSender, args = (connection, jsonData, filepath))
                        fileSender.start()
                else:
                    print("HOST: "+client_address[0]+":"+str(client_address[1])+"  errore avvenuto durante ricezione\n")

            
    def DhtService(self, bootstrapIp):  # Medoto che instanzia kademlia e ne fa il bootstrap
        host = self.HOST
        port = self.PORT

        bootstrapIp = re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', bootstrapIp) #RegEx to control if given ip address+port is correct

        if not bootstrapIp:
            error_window = tk.Toplevel(self)
            error_window.geometry("200x100")
            error_window.title("IP")
            error_window.resizable(0, 0)
            tmpLabel = tk.Label(error_window, text = "L'indirizzo ip inserito non è valido")
            tmpLabel.pack(expand=True, pady=10)
            tk.Button(error_window, text="RIPROVA", command=error_window.destroy).pack(side=tk.BOTTOM, expand=True)
        else:
            remoteHost = bootstrapIp[0].split(":")
            self.btnBtstrp.config(state = "disabled")
            self.txtLog.insert(tk.INSERT, "Connessione KAD...")
            
            try:
                self.dht = DHT(host, port, seeds=[(remoteHost[0], int(remoteHost[1]))])
            except OSError:
                print("OSError")
                self.after(1000)
                self.dht = DHT(host, port, seeds=[(remoteHost[0], int(remoteHost[1]))])

            if len(self.dht.peers()) == 0:
                self.txtLog.insert(tk.INSERT, "\nKAD:remote host unreachable\nERRORE:riavvia")
                self.lblKadVal.configure(text="ERROR")
            else:
                self.txtLog.insert(tk.INSERT, "\nKAD:Connesso")
                self.lblKadVal.configure(text="Connesso (Insicuro)")
                self.lblTcpVal.configure(text="Test")

                tcpService = Thread(target=self.TcpServer)
                tcpService.start()


    def SearchButton(self, key):    # Aggiorna l'attributo searchkey
        self.searchKey = key


    def CleanButton(self):  # Pulisce la tabella da tutti i valori se il tasto pulisci viene premuto
        for element in range(len(self.nomiFile)):
            self.nomiFile[element].config(text=" ", state="disabled", bg="white")
            self.dimFile[element].config(text=" ", state="disabled", bg="white")
            self.fontiFile[element].config(text=" ", state="disabled", bg="white")
            self.tipiFile[element].config(text=" ", state="disabled", bg="white")

        self.btnPulisci.config(state = "disabled")

    
    def DownloadButton(self, pos):
        print(self.nomiFile[pos]["text"])
        self.fileToDownload = (self.nomiFile[pos]["text"], self.peerFile[pos][0], self.peerFile[pos][1])
            

    def Seleziona(self, pos):
        for i in range(15):
            if i==pos-1:
                self.btnDownload.config(state = "normal", command = lambda: self.DownloadButton(0))
                print(i)

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
        self.Menu = tk.OptionMenu(self.frameRow1, self.sceltaMenu, "Uploads", "Kad Jobs", "Debug")
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

        # FrameNomiFile :-/
        # Button per selezione File
        self.nomiFile.append(tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", width=24, bd=0, command=lambda: self.Seleziona(1)))
        self.dimFile.append(tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", width=6, bd=0, command=lambda: self.Seleziona(1)))
        self.fontiFile.append(tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", width=5, bd=0, command=lambda: self.Seleziona(1)))
        self.tipiFile.append(tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", width=5, bd=0, command=lambda: self.Seleziona(1)))
        for n in range(2, 16): 
            self.nomiFile.append(tk.Button(self.frameNomiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(n)))
            self.dimFile.append(tk.Button(self.frameDimFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(n)))
            self.fontiFile.append(tk.Button(self.frameFontiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(n)))
            self.tipiFile.append(tk.Button(self.frameTipiFile, text=" ", state="disabled", relief="solid", bd=0, command=lambda: self.Seleziona(n)))

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

mainRoot = tk.Tk()
mainRoot.title("TROIKAD")
root=Finestra(mainRoot)
mainRoot.resizable(0, 0)
root.mainloop()