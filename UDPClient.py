# Michael Burton,Jocelyn Frechette, Jesse Haye-Lewis
# UDPClient.py
# Phase 2, EECE 5830, Fall 2023
# 1 October 2023


from socket import *

# documentation link: https://docs.python.org/3/library/socket.html

# states
S_Wait_for_call_0_from_above = 0
S_Wait_for_ACK_0 = 1
S_Wait_for_call_1_from_above = 2
S_Wait_for_ACK_1 = 3

# structure of message from sender:
# SEQ BIT, 16-bit checksum, N-byte data

ACK = b'1'  # need to define the ack, should be bytes object with ACK and correct sequence number
SEQ_0 = b'0'
SEQ_1 = b'1'


# Make_Packet
# Input: file_name: string representing the path to the file to read from
# Input: packet_size: integer representing the number of Bytes in a packet
# Output: packet_list: a list of Bytes objects to be sent to the server
def Make_Packet(file_name, packet_size):
    # If the .bmp file is not in the same directory as the code, the full path should be prepended to the file name
    # e.g., path = "C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/",
    # file_name = path + file_name
    f = open(file_name, "rb")

    packet_list = []

    # first packet is the number of packets being sent
    packet = f.read(packet_size)
    packet_list.append(packet)

    # While there is still data left in the file, read another packet.
    # On the last packet, it will be smaller than the packet_size specified, so we know we are done
    while len(packet) == packet_size:
        packet = f.read(packet_size)
        packet_list.append(packet)

    print("Packets Made. Number of packets: ", len(packet_list), "file position: ", f.tell())
    print("First packet: ", packet_list[0])
    f.close()
    return packet_list

def split_packet(message):
    pass
def is_ack(message, expected_seq_num):
    # First, we must split the message into its parts
    # Then, we have to confirm that the ACK sequence is what we are expecting
    pass

def is_corrupt(message):
    # First, we split the message into its parts
    # Then, we calculate the checksum of the ACK,
    pass


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

    # receive
    # input: bdata_size
    def receive(self, bdata_size):
        message, server_address = self.socket.recvfrom(bdata_size)

        return message

    def next_state(self, state, message, bdata_size):
        if state == S_Wait_for_call_0_from_above:
            # send the packet out
            self.send(message)
            return S_Wait_for_ACK_0
        elif state == S_Wait_for_ACK_0:
            ack_msg = self.receive(bdata_size)
            if ack_msg == ACK:
                return S_Wait_for_call_1_from_above
            else:
                return S_Wait_for_ACK_0
        elif state == S_Wait_for_call_1_from_above:
            return 1
        elif state == S_Wait_for_ACK_1:
            return 1
        else:
            return 1


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match server)#: "))
    # # sender port is not specified since OS specifies that, and we do not care what it is
    # # This is the receiver port, so whichever system is designated as a receiver will use this to listen
    #

    client = UDPClient(name_receiver, port_receiver)

    # Sends packets to the server with a message packet size as 2048 Bytes
    packets = Make_Packet("LAND2.BMP", 2048)

    # Test case for when the file size = 0
    # packets = Make_Packet("unknown.BMP", 2048)

    # packet_length gets the length of the packet array, and converts it to a string
    packet_length = str(len(packets))

    # message is converted from a string to a bytes object, and then sent to the server as the message that
    # client is sending packets
    client.send(packet_length.encode())

    # for each packet in the list packets, send them to the client
    for x in packets:
        client.send(x)

    # Tell the server we are f
    client.send(packet_length.encode())

    sender_state = 0

    message = bytes()

    # In Loop will handle the application layer, in state machine will handle transport layer
    while True:
        sender_state = client.next_state(sender_state, message, 2048)
