# Michael Burton,Jocelyn Frechette, Jesse Haye-Lewis
# UDPClient.py
# Phase 2, EECE 5830, Fall 2023
# 1 October 2023
import struct
from socket import *
import numpy as np
import os
from math import floor
import hashlib
import random


# documentation link: https://docs.python.org/3/library/socket.html

# states
S_Wait_for_call_0_from_above = 0
S_Wait_for_ACK_0 = 1
S_Wait_for_call_1_from_above = 2
S_Wait_for_ACK_1 = 3

# structure of message from sender:
# 16-bit checksum, 8-bit ACK, 8-bit SEQ, N-byte data

CHECKSUM_SIZE = 2
ACK = 255  # need to define the ack, should be bytes object with ACK and correct sequence number
SEQ_0 = 0
SEQ_1 = 255
ACK_SEQ_SIZE = 2

DATA_OFFSET = ACK_SEQ_SIZE + CHECKSUM_SIZE


# Make_Packet
# Input: file_name: string representing the path to the file to read from
# Input: packet_size: integer representing the number of Bytes in a packet
# Output: packet_list: a list of Bytes objects to be sent to the server
def Make_Packet(file_name, data_size):
    # If the .bmp file is not in the same directory as the code, the full path should be prepended to the file name
    # e.g., path = "C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/",
    # file_name = path + file_name
    f = open(file_name, "rb")

    packet_list = []

    # first packet is the number of packets being sent, this is setting up the second packet sent, so SEQ_1 is used
    seq_to_send = SEQ_1
    packet = bytearray()

    data = f.read(data_size)

    # cs_packet is the proto-header (missing checksum) and the data for creating checksum
    cs_packet = bytearray()
    cs_packet.append(ACK)
    cs_packet.append(seq_to_send)
    cs_packet.extend(data)
    csum = checksum(cs_packet)

    packet.extend(csum)
    packet.append(ACK)
    packet.append(seq_to_send)
    packet.extend(data)

    packet_list.append(packet)

    seq_to_send = SEQ_0
    # While there is still data left in the file, read another packet.
    # On the last packet, it will be smaller than the packet_size specified, so we know we are done
    while len(data) == data_size:
        data = f.read(data_size)

        packet = bytearray()

        # cs_packet is the proto-header (missing checksum) and the data for creating checksum
        cs_packet = bytearray()
        cs_packet.append(ACK)
        cs_packet.append(seq_to_send)
        cs_packet.extend(data)

        csum = checksum(cs_packet)

        packet.extend(csum)
        packet.append(ACK)
        packet.append(seq_to_send)
        packet.extend(data)
        print(packet)
        packet_list.append(packet)

        if seq_to_send == SEQ_1:
            seq_to_send = SEQ_0
        else:
            seq_to_send = SEQ_1

    data = struct.pack(">I", len(packet_list))

    packet = bytearray()

    cs_packet = bytearray()
    cs_packet.append(ACK)
    cs_packet.append(SEQ_0)
    cs_packet.extend(data)
    csum = checksum(cs_packet)

    packet.extend(csum)
    packet.append(ACK)
    packet.append(SEQ_0)
    packet.extend(data)

    # print(packet)
    # print(packet_list[0])

    # print(split_packet(packet))
    packet_list.insert(0, packet)

    print("Packets Made. Number of packets: ", len(packet_list), "file position: ", f.tell())
    print("First packet: ", packet_list[0])
    f.close()
    return packet_list
def corruptor(byte_object):
    cor_byte_object = [0]*len(byte_object)
    #print(len(cor_packet))
    #Function takes in the packet list and will perform a randomized corruption on a certain percetage of packets
    for j in range(len(byte_object)):
        cor_byte_object[j] = ~byte_object[j] & 255
     #  print("Corrupted Packets: ",bin(~packet[j]&255))
    #print("corrupt packet")
    #cor_packet=packet
    return cor_byte_object

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
    return bytearray.fromhex(h.hexdigest())


def split_packet(message):
    print(message)
    csum = message[0:CHECKSUM_SIZE]
    ack_response = message[CHECKSUM_SIZE]
    seq_response = message[CHECKSUM_SIZE + 1]
    data = message[DATA_OFFSET:]

    return csum, ack_response, seq_response, data


def split_ack_packet(received_msg):
    csum = received_msg[0:CHECKSUM_SIZE]
    ack_response = received_msg[CHECKSUM_SIZE]
    seq_response = received_msg[CHECKSUM_SIZE + 1]

    return csum, ack_response, seq_response


def is_ack(ack_received, seq_received, expected_seq_num):
    # First, we must split the message into its parts
    # Then, we have to confirm that the ACK sequence is what we are expecting
    return ack_received == ACK and seq_received == expected_seq_num


def is_corrupt(received_checksum, new_checksum):
    # First, we split the message into its parts
    # Then, we calculate the checksum of the ACK,
    return received_checksum != new_checksum


class UDPClient:
    # Initializes the UDP Client with name and port
    def __init__(self, name, port):
        self.state = S_Wait_for_call_0_from_above
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

    def next_state(self, message, bdata_size):
        if self.state == S_Wait_for_call_0_from_above:
            # send the packet out
            self.send(message)
            return S_Wait_for_ACK_0
        elif self.state == S_Wait_for_ACK_0:
            received_msg = self.receive(bdata_size)
            csum, ack_response, seq_response = split_ack_packet(received_msg)
            cs_packet = bytearray()
            cs_packet.append(ack_response)
            cs_packet.append(seq_response)
            new_checksum = checksum(cs_packet)
            print("Inputs to New checksum Client side ACK_0: ", received_msg)
            print("New checksum Client side ACK_0: ", new_checksum)
            if not is_corrupt(csum, new_checksum) and is_ack(ack_response, seq_response, SEQ_0):
                return S_Wait_for_call_1_from_above
            else:
                self.send(message)
                return S_Wait_for_ACK_0
        elif self.state == S_Wait_for_call_1_from_above:
            self.send(message)
            return S_Wait_for_ACK_1
        elif self.state == S_Wait_for_ACK_1:
            received_msg = self.receive(bdata_size)
            csum, ack_response, seq_response = split_ack_packet(received_msg)
            cs_packet = bytearray()
            cs_packet.append(ack_response)
            cs_packet.append(seq_response)
            new_checksum = checksum(cs_packet)
            if not is_corrupt(csum, new_checksum) and is_ack(ack_response, seq_response, SEQ_1):
                return S_Wait_for_call_0_from_above
            else:
                self.send(message)
                return S_Wait_for_ACK_1
        else:  # error state, if state == 10, this should be an error
            return 10


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match server)#: "))
    cor_percent = int(input("Specify level of corruption as a percentage to the nearest whole number: "))
    # # sender port is not specified since OS specifies that, and we do not care what it is
    # # This is the receiver port, so whichever system is designated as a receiver will use this to listen
    #
    #Add as a command option, but hard coding for now:
    #cor_percent = 5

    #instantiate the client
    client = UDPClient(name_receiver, port_receiver)


    #make packets
    packets = Make_Packet("Lavender.jpg", 1024)

    #Calculate the number of packets needed to be corrupted, a uniform distribution is used to select which index in
    #the packet list that will be corrupted
    num_pack_cor = int(floor(len(packets) * (cor_percent / 100)))
    cor_ind = np.random.randint(0, len(packets), size=num_pack_cor)
    cor_ind.sort()
    
    print(cor_ind)

    ## packet_length gets the length of the packet array, and converts it to a string
    #packet_length = str(len(packets))

    # message is converted from a string to a bytes object, and then sent to the server
    #client.send(packet_length.encode())
    #i=0
    #for x in packets:
    #    if i in cor_ind:
    #        print("Corrupt Packet",i)
    #        x=corruptor(x)
    #        x=bytearray(x)
    #    client.send(x)
    #    i = i+1
    #client.send(packet_length.encode())
    

    packet_index = 0

    seq_to_send = SEQ_0
    # In Loop will handle the application layer, in state machine will handle transport layer
    while packet_index < len(packets):
        packet = packets[packet_index]
        if packet_index in cor_ind:
          print("Corrupt Packet",packet_index)
          packet = bytearray(corruptor(packets[packet_index]))
          cor_ind.pop(0)
          
        sender_state = client.next_state(packet, 2048)
        if sender_state == S_Wait_for_call_0_from_above or sender_state == S_Wait_for_call_1_from_above:
            packet_index += 1  # we can advance the index since the packet was sent properly

        client.state = sender_state  # advance the state
