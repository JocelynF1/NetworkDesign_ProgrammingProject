# Michael Burton, Jocelyn Frechette, Jesse Hayes-Lewis
# UDPServer.py
# Phase 2, EECE 5830, Fall 2023
# 1 October 2023


from socket import *



# documentation link: https://docs.python.org/3/library/socket.html

# deliver_data
# Input: packet_array: List of the message sections of packets received from the client
# Input: file_name: string representing the path to the file to write to make the copy
# Output: writes the data from packet_array to the file location specified
def deliver_data(packet_array, file_name):
    # If the .bmp file is not in the same directory as the code, the full path should be prepended to the file name
    # e.g., path = "C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/",
    # file_name = path + file_name

    f_write = open(file_name, "wb")

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
    # Input: bdata_size, buffer size in bytes
    # Output: Message to Console confirming that the server is ready to receive
    # Output: test data, such as number of packets received, the list of packets,
    # and then the length of the list of packets to make sure it matched the number of packets received
    # Output: received_packets, the list of Bytes objects containing packet messages

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
            received_packets.append(message)
        received_packets.pop()

        # Q: What happens if the number of packets is zero?
        # A: client only sends one packet, an empty string of bytes (b'')
        print(received_packets)
        print(len(received_packets))

        return received_packets


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match client)#: "))
    # sender port is not specified since OS specifies that, and we do not care what it is
    # This is the receiver port, so whichever system is designated as a receiver will use this to listen

    server = UDPServer(name_receiver, port_receiver)

    # Receives packets from client with a message buffer size on each packet as 2048 Bytes
    received_packets = server.receive(2048)

    # "copy.bmp" is where the data from the packets received get written to, location is local to the code directory
    deliver_data(received_packets, "copy.bmp")
