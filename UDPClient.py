# Michael Burton
# UDPClient.py
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


def Make_Packet(file_name, packet_size):
    f = open(file_name, "rb")

    packet_list = []
    packet = f.read(packet_size)
    packet_list.append(packet)

    while len(packet) == packet_size:
        packet = f.read(packet_size)
        packet_list.append(packet)

    print("Packets Made. Number of packets: ", len(packet_list), "file position: ", f.tell())
    f.close()
    return packet_list


class UDPClient:
    # Initializes the UDP Client with name and port
    def __init__(self, name, port):
        self.name_receiver = name
        self.port_receiver = port
        self.socket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = using IPv4, SOCK_DGRAM = Datagram,
        # UDP = User Datagram Protocol
        # By default, the socket object is in blocking mode

        print("Client initialized")

    # Sends message to server, prints response
    def send(self, message):
        self.socket.sendto(message, (self.name_receiver, self.port_receiver))
        # client sends message (converted to Bytes) to server

        # modified_message, server_address = self.socket.recvfrom(bdata_size)
        # client receives the response (Bytes) from server

        # print(modified_message)  # convert message from a bytes object to string, then prints
        # Won't close socket here in case user wants to send more

    # receive
    # description: receives data from the server
    # echo it back to server
    # Input: bdata_size, buffer size in bytes
    # Output: Message to Console confirming that the client is ready to receive
    def receive(self, bdata_size):
        self.socket.bind(('', self.port_receiver))  # bind binds the socket to a particular port to listen on
        # The argument is a tuple in the form (,) , where the first part of the tuple corresponds to
        # the host address ('' represents INADDR_ANY, which binds to any local interface)
        # and the second part is the port to listen on
        # Linked python socket documentation for this piece near the import statement
        print("Client \"", self.name_receiver, "\" is ready on port \"", self.port_receiver, "\"")
        while True:
            message, server_address = self.socket.recvfrom(bdata_size)
            modified_message = message.decode()  # this is where to specify message modifications
            # to send back to the sender
            self.socket.sendto(modified_message.encode(), server_address)

    # Selects the mode for the Client, receiving, sending, or closing socket
    # Relies on user to not put the system in receive-receive mode, where both
    # client and server set up to receive, which would not be very useful
    # returns "Continue" for the outer event loop to run this again, "End" otherwise
    def mode_select(self):
        yes_no = ["Y", "N"]
        answer_rx = input_validation("Receive Messages? Y/N: ", yes_no)
        if answer_rx == "Y":
            buf_size = int(input("Give a buffer size to receive message (Match the server send buffer size): "))
            self.receive(buf_size)
            return "Continue"  # Will never get here since receive puts this program into an infinite loop
        else:
            answer_tx = input_validation("Send Messages? (make sure your server is ready to receive) Y/N: ", yes_no)
            if answer_tx == "Y":
                buf_size = int(input("Give a buffer size to send message (Match the server receive buffer size): "))
                message_client = input("Message: ")
                self.send(buf_size, message_client)
                return "Continue"
            else:
                answer_csocket = input_validation("Close Socket? Y/N: ", yes_no)
                if answer_csocket == "Y":
                    print("Client will close socket")
                    self.socket.close()
                    return "End"
                    # Not Specified within requirements for Phase 1, state is explicitly handled
                else:
                    print("No options were specified, try again.")
                    return "Continue"


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match server)#: "))
    # # sender port is not specified since OS specifies that, and we do not care what it is
    # # This is the receiver port, so whichever system is designated as a receiver will use this to listen
    #

    client = UDPClient(name_receiver, port_receiver)

    packets = Make_Packet("C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/LAND2.BMP", 1024)

    # packet_length gets the length of the packet array, and converts it to a string
    packet_length = str(len(packets))

    # message is converted from a string to a bytes object, and then sent to the server
    client.send(packet_length.encode())

    for x in packets:
        client.send(x)
    client.send(packet_length.encode())


