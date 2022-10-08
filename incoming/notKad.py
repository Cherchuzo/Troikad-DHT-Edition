import tkinter as tk
from kad import DHT
from threading import Thread
import socket
import time

class Finestra(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        
        # GLOBAL VARIABLES
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

        self.grid()
        self.CreaWidgets()


    def TcpServer(self):
        time.sleep(2)

        try:
            tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            localAddress = ("0.0.0.0", 2442)
            tcpServer.bind(localAddress)
            print("TCP:In avvio su:{}  Porta:{}".format(*localAddress))
            self.lblTcpVal.configure(text="Test (Insicuro)")
        except:
            print("Socket non avviato/inizializzato!")
            self.lblTcpVal.configure(text="ERROR")
            self.txtLog.insert(tk.INSERT, "\nERRORE:TCP error")
            self.txtLog.insert(tk.INSERT, "\nERRORE:riavvia")
    

    def DhtService(self, bootstrapIp):
        host = "0.0.0.0"
        port = 2442

        remoteHost = bootstrapIp.split(":")

        self.txtLog.insert(tk.INSERT, "Connessione KAD...")

        if bootstrapIp == "" or not ":" in bootstrapIp:
            remoteHost = []
            remoteHost.insert(0, "localhost")
            remoteHost.insert(1, 10000)
        
        self.dht = DHT(host, port, seeds=[(remoteHost[0], int(remoteHost[1]))])
        time.sleep(4)

        if len(self.dht.peers()) == 0:
            self.txtLog.insert(tk.INSERT, "\nKAD:remote host unreachable")
            self.txtLog.insert(tk.INSERT, "\nERRORE:riavvia")
        else:
            self.txtLog.insert(tk.INSERT, "\nKAD:Connesso")
            self.lblKadVal.configure(text="Connesso (Insicuro)")
            self.lblTcpVal.configure(text="Test")

            tcpService = Thread(target=self.TcpServer)
            tcpService.start()

    def Seleziona(self, pos):
        for i in range(15):
            if i==pos-1:
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
        self.lblBtstrp = tk.Label(self.frameBtstrp, text=" BOOTSTRAP:  ", highlightthickness=0, font=('Helvetica', 9, 'bold')).grid(row=0, column=1, pady=0, padx=3)
        self.enBtstrp = tk.Entry(self.frameBtstrp, textvar=self.enBtstrpVar, width=45, bd=self.globalBorderThicknessIn, relief="solid", justify="center").grid(row=0, column=2, pady=4, padx=5)
        self.btnBtstrp = tk.Button(self.frameBtstrp, image=self.imgInvio, command= lambda: self.DhtService(self.enBtstrpVar.get()), bd=self.globalBorderThicknessIn, relief="solid").grid(row=0, column=3, pady=0, padx=10)

        #ROW 2
        #   fillers
        tk.Label(self.frameCerca, text="    ").grid(row=0, column=4)
        tk.LabelFrame(self.frameRow2, text="", highlightbackground="black", highlightthickness=2, bd=0).grid(row=0, column=0, rowspan=2, sticky="nesw")
        tk.LabelFrame(self.frameRow2, text=" ", width=2, fg="black", bg="black", highlightbackground="black", highlightthickness=30, bd=0).grid(row=0, column=2, rowspan=2, sticky="nesw")
        tk.LabelFrame(self.frameRow2, text="", highlightbackground="black", highlightthickness=2, bd=0).grid(row=0, column=4, rowspan=2, sticky="nesw")

        #   COLUMN 1
        #       Cerca
        self.lblCerca = tk.Label(self.frameCerca, text=" CERCA:     ", font=('Helvetica', 9, 'bold')).grid(row=0, column=0, sticky="nesw")
        self.enCerca = tk.Entry(self.frameCerca, textvariable=self.enCercaVar, width=45, bd=self.globalBorderThicknessIn, relief="solid", justify="center").grid(row=0, column=1, columnspan=3, pady=3, padx=0)

        #       Options
        self.btnInizia = tk.Button(self.frameOptCerca, text="INIZIA", command=None, bd=self.globalBorderThicknessIn,relief="solid").grid(row=1, column=0, pady=5, padx=15)
        self.btnDownload = tk.Button(self.frameOptCerca, text="DOWNLOAD", command=None, bd=self.globalBorderThicknessIn,relief="solid").grid(row=1, column=1, pady=5, padx=15)
        self.btnPulisci = tk.Button(self.frameOptCerca, text="PULISCI", command=None, bd=self.globalBorderThicknessIn,relief="solid").grid(row=1, column=2, pady=5, padx=15)
        self.btnFiltra = tk.Button(self.frameOptCerca, text="FILTRA", command=None, bd=self.globalBorderThicknessIn,relief="solid").grid(row=1, column=3, pady=5, padx=15)

        #   COLUMN 2
        #       #Filtri
        self.lblFiltri = tk.Label(self.frameRow2, text="FILTRI", borderwidth=0, relief="solid", font=('Helvetica', 12, 'bold')).grid(row=0, column=3, rowspan=2, pady=0, ipadx=40, sticky="nesw")

        #ROW 3
        #   fillers
        tk.Label(self.frameFiles, text="               ", font=('Helvetica', 1, 'bold')).grid(row=0, column=0)
        tk.Label(self.frameFiles, text="     ", font=('Helvetica', 7, 'bold')).grid(row=4, column=5)
        tk.Label(self.frameLog, text="      ", font=('Helvetica', 1, 'bold')).grid(row=0, column=0)
        tk.Label(self.frameLog, text="      ", font=('Helvetica', 1, 'bold')).grid(row=0, column=2)

        #   COLUMN 1
        #       Tabella Risultati
        self.lblRisultati=tk.Label(self.frameFiles, text=" RISULTATI ", borderwidth=2, relief="solid").grid(row=1, column=1, sticky="w")

        self.lblNFile=tk.Label(self.frameBorderFile, text="Nome File                                        ", anchor="w", borderwidth=1, relief="solid").grid(row=2, column=1)
        self.lblDi=tk.Label(self.frameBorderFile, text="   Dim .   ", anchor="center", borderwidth=1, relief="solid").grid(row=2, column=2)
        self.lblFont=tk.Label(self.frameBorderFile, text="  Fonti  ", anchor="center", borderwidth=1, relief="solid").grid(row=2, column=3)
        self.lblTip=tk.Label(self.frameBorderFile, text="  Tipo   ", anchor="center", borderwidth=1, relief="solid").grid(row=2, column=4)

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
        self.lblLog=tk.Label(self.frameLog, text=" LOG    ", anchor="w", borderwidth=2, relief="solid").grid(row=1, column=1, sticky="w")
        self.txtLog=tk.Text(self.frameLog, width=13, height=19, font=('Helvetica', 11, 'bold'), bd=2, relief="solid")
        self.txtLog.grid(row=2, column=1)

        #ROW 4
        #   fillers
        tk.Label(self.frameUpDown, text="", font=('Helvetica', 2, 'bold')).grid(row=0)
        tk.Label(self.frameUpDown, text="", font=('Helvetica', 1, 'bold')).grid(row=2)

        #   COLUMN 1
        #       TCP
        self.lblTcp=tk.Label(self.frameTcpKad, text=" TCP: ").grid(row=0, column=0)
        self.lblTcpVal=tk.Label(self.frameTcpKad, text="", width=20)
        self.lblTcpVal.grid(row=0, column=1)
        #       KAD
        self.lblKad=tk.Label(self.frameTcpKad, text=" KAD: ").grid(row=1, column=0)
        self.lblKadVal = tk.Label(self.frameTcpKad, text="")
        self.lblKadVal.grid(row=1, column=1)

        #   COLUMN 2
        #       Up
        self.lblUp=tk.Label(self.frameUpDown, text=" UP: ").grid(row=1, column=0)
        self.lblUpVal = tk.Label(self.frameUpDown, text="", width=8)
        self.lblUpVal.grid(row=1, column=1)
        #       Down
        self.lblDown = tk.Label(self.frameUpDown, text="  DOWN: ").grid(row=1, column=3)
        self.lblDownVal = tk.Label(self.frameUpDown, text="", width=6)
        self.lblDownVal.grid(row=1, column=4)

        #   COLUMN 3
        #       Compagno
        self.lblCompagno=tk.Label(self.frameCompagno, text="  COMPAGNO:         ").grid(row=0, column=0)
        self.lblCompagnoVal = tk.Label(self.frameCompagno, text="")
        self.lblCompagnoVal.grid(row=1, column=0)

root=Finestra()
root.mainloop()
