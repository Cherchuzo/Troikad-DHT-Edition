import socket

class ConnectionHelper(object):

    @staticmethod
    def send(connection, message, flag):     
        successful = False
        try:
            connection.sendall(message.encode('utf-8'))
            if flag:
                connection.shutdown(socket.SHUT_WR)
                connection.close()
            successful = True
        except:
            connection.close()

        if successful:
            return True
        else:
            return False
        

    @staticmethod
    def receive(connection, buffer, flag):
        successful = False
        try:
            msg = connection.recv(buffer)
            if flag:
                connection.shutdown(socket.SHUT_WR)
                connection.close()
            successful = True
        except:
            connection.close()

        if successful:
            return msg.decode('utf-8')
        else:
            return None


    @staticmethod
    def sendBytes(connection, message, flag):     
        successful = False
        try:
            connection.sendall(message)
            #print(message)
            if flag:
                connection.shutdown(socket.SHUT_WR)
                connection.close()
            successful = True
        except:
            connection.close()

        if successful:
            #print("True")
            return True
        else:
            return False


    @staticmethod
    def receiveBytes(connection, buffer, flag, overData = None):
        successful = False
        exitFlag = False
        
        if overData:
            msg = overData
        else:
            msg = bytes

        while not exitFlag:
            try:
                msg += connection.recv(buffer)
                if flag:
                    connection.shutdown(socket.SHUT_WR)
                    connection.close()
                if msg:
                    if len(msg) > buffer:
                        completeMsg, overData = (msg[:buffer], msg[buffer:])
                        exitFlag = True
                    elif len(msg) == buffer:
                        exitFlag = True
                successful = True
            except:
                connection.close()
                successful = False
                exitFlag = True

        if successful:
            return completeMsg, overData
        else:
            return None, None