# Michael Burton
# UDPServer.py
# Phase 1, EECE 5830, Fall 2023
# 18 September 2023


from socket import *
import os

# documentation link: https://docs.python.org/3/library/socket.html

# input_validation
# description: Will continually ask for the user to provide input until valid
# Inputs: string input_text, list of string option_list
# Output: user input that matches one of the strings in option_list
def input_validation(input_text, option_list):
    answer = input(input_text)
    while answer not in option_list:
        print("try again")
        answer = input(input_text)
    return answer

def deliver_data(packet_array, file_name):
    path = "C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/"

    name_and_path = "C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/" + file_name
    f_write = open(name_and_path, "wb")

    for i in packet_array:
        f_write.write(i)

    f_write.close()

class UDPServer:
    # Initializes the UDP Server with name and port
    def __init__(self, name, port):
        self.name_receiver = name
        self.port_receiver = port
        self.socket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = using IPv4, SOCK_DGRAM = Datagram,
        # UDP = User Datagram Protocol
        # Windows socket API: https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-socket
        # By default, the socket object is in blocking mode

        print("Server initialized")

    # receive
    # description: receives data from the client
    # echo it back to client
    # Input: bdata_size, buffer size in bytes
    # Output: Message to Console confirming that the server is ready to receive
    def receive(self, bdata_size):

        self.socket.bind(('', self.port_receiver))  # bind binds the socket to a particular port to listen on
        # The argument is a tuple in the form (,) , where the first part of the tuple corresponds to
        # the host address ('' represents INADDR_ANY, which binds to any local interface)
        # and the second part is the port to listen on
        # Linked python socket documentation for this piece near the import statement

        print("Server \"", self.name_receiver, "\" is ready on port \"", self.port_receiver, "\"")

        message = None
        while message is None:
            message, client_address = self.socket.recvfrom(bdata_size)

        num_packets_encoded = message

        num_packets = int(message.decode())

        print(num_packets)
        received_packets = []

        message = bytes()

        while message != num_packets_encoded:
            message, client_address = self.socket.recvfrom(bdata_size)
            modified_message = message  # this is where to specify message modifications using string methods
            # to send back to the sender
            # self.socket.sendto(modified_message, client_address)
            received_packets.append(message)
        received_packets.pop()  # TODO what happens if the number of packets is zero?
        print(received_packets)
        print(len(received_packets))

        return received_packets

    # Sends message to client, prints response
    def send(self, bdata_size, message):
        self.socket.sendto(message, (self.name_receiver, self.port_receiver))
        # server sends message (converted to Bytes) to client

        modified_message, client_address = self.socket.recvfrom(bdata_size)
        # server receives the response (Bytes) from client

        # print(modified_message.decode())  # convert message from a bytes object to string, then prints
        # Won't close socket here in case user wants to send more

    # Selects the mode for the Server, receiving, sending, or closing socket
    # Relies on user to not put the system in receive-receive mode, where both
    # client and server set up to receive, which would not be very useful
    # returns "Continue" for the outer event loop to run this again, "End" otherwise
    def mode_select(self):
        yes_no = ["Y", "N"]
        answer_rx = input_validation("Receive Messages? Y/N: ", yes_no)
        if answer_rx == "Y":
            buf_size = int(input("Give a buffer size to receive message (Match the client send buffer size): "))
            self.receive(buf_size)
            return "Continue"  # Will never get here since receive puts this program into an infinite loop
        else:
            answer_tx = input_validation("Send Messages? (make sure your client is ready to receive) Y/N: ", yes_no)
            if answer_tx == "Y":
                buf_size = int(input("Give a buffer size to send message (Match the client receive buffer size): "))
                message_server = input("Message: ")
                self.send(buf_size, message_server)
                return "Continue"
            else:
                answer_csocket = input_validation("Close Socket? Y/N: ", yes_no)
                if answer_csocket == "Y":
                    print("Server will close socket")
                    self.socket.close()
                    return "End"
                    # Not Specified within requirements for Phase 1, state is explicitly handled
                else:
                    print("No options were specified, try again.")
                    return "Continue"


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match client)#: "))
    # sender port is not specified since OS specifies that, and we do not care what it is
    # This is the receiver port, so whichever system is designated as a receiver will use this to listen

    server = UDPServer(name_receiver, port_receiver)

    received_packets = server.receive(1024)

    deliver_data(received_packets,"copy.bmp")




    # socket_closed = "Continue"
   # while socket_closed != "End":
    #     # Main Event loop for server. Covers the case if the
    #     # user continually wants to send or idle on the server side.
    #     # Will not affect receive mode, since that is an infinite loop
    #     socket_closed = server.mode_select()
