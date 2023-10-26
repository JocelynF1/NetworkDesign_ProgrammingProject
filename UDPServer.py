# Michael Burton, Jocelyn Frechette, Jesse Hayes-Lewis
# UDPServer.py
# Phase 2, EECE 5830, Fall 2023
# 1 October 2023


from socket import *
import hashlib
import random

# documentation link: https://docs.python.org/3/library/socket.html

# states
S_Wait_for_0_from_below = 0
S_Wait_for_1_from_below = 1

# structure of message from receiver:
# 16-bit checksum, 8-bit ACK, 8-bit SEQ, N-byte data

CHECKSUM_SIZE = 2
ACK = 255  # need to define the ack, should be bytes object with ACK and correct sequence number
SEQ_0 = 0
SEQ_1 = 255
ACK_SEQ_SIZE = 2

DATA_OFFSET = ACK_SEQ_SIZE + CHECKSUM_SIZE


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


def corrupt_data(data):
    data_length = len(data)
    corrupt_data = bytearray()
    for i in range(data_length):
        corrupt_data.append((data[i] + random.randint(0, 255)) % 256)
    return corrupt_data


def corrupt_ack(ack, seq):
    corrupt_ack = (ack + random.randint(0, 255)) % 256
    corrupt_seq = (seq + random.randint(0, 255)) % 256
    return corrupt_ack, corrupt_seq


def checksum(message):
    # Will put custom hashing function later, this is temporary for testing purposes
    h = hashlib.blake2b(digest_size=CHECKSUM_SIZE)
    h.update(message)
    return h.digest()


def split_packet(message):
    print(len(message))
    checksum = message[0:CHECKSUM_SIZE]
    ack_response = message[CHECKSUM_SIZE]
    seq_response = message[CHECKSUM_SIZE + 1]
    data = message[DATA_OFFSET:]

    return checksum, ack_response, seq_response, data


def is_ack(ack_received, seq_received, expected_seq_num):
    # First, we must split the message into its parts
    # Then, we have to confirm that the ACK sequence is what we are expecting
    return ack_received == ACK and seq_received == expected_seq_num


def is_corrupt(received_checksum, new_checksum):
    # First, we split the message into its parts
    # Then, we calculate the checksum of the ACK,
    return received_checksum != new_checksum


class UDPServer:
    # Initializes the UDP Server with name and port
    def __init__(self, name, port):
        self.state = S_Wait_for_0_from_below
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
            message, client_address = self.socket.recvfrom(bdata_size+DATA_OFFSET)

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

    def next_state(self, bdata_size):
        if self.state == S_Wait_for_0_from_below:
            msg, client_address = self.socket.recvfrom(bdata_size)
            checksum, ack_response, seq_response, data = split_packet(msg)
            cs_message = bytearray()
            cs_message.append(ack_response)
            cs_message.append(seq_response)
            cs_message.extend(data)
            new_checksum = checksum(cs_message)

            ack_msg = bytearray()
            ack_msg.append(checksum)
            ack_msg.append(ack_response)
            if not is_corrupt(checksum, new_checksum) and is_ack(ack_response, seq_response, SEQ_0):
                # deliver data
                # send pos ack
                ack_msg.append(SEQ_0)
                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_1_from_below
            else:
                ack_msg.append(SEQ_1)
                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_0_from_below

        elif self.state == S_Wait_for_1_from_below:
            msg, client_address = self.socket.recvfrom(bdata_size)
            checksum, ack_response, seq_response, data = split_packet(msg)
            cs_message = bytearray()
            cs_message.append(ack_response)
            cs_message.append(seq_response)
            cs_message.extend(data)
            new_checksum = checksum(cs_message)

            ack_msg = bytearray()
            ack_msg.append(checksum)
            ack_msg.append(ack_response)
            if not is_corrupt(checksum, new_checksum) and is_ack(ack_response, seq_response, SEQ_1):
                # deliver data
                # send pos ack
                ack_msg.append(SEQ_1)
                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_0_from_below
            else:
                ack_msg.append(SEQ_0)
                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_1_from_below
        else:
            return 10


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


