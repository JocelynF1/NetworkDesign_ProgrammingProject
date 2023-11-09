# Michael Burton, Jocelyn Frechette, Jesse Haynes-Lewis
# UDPServer.py
# Phase 4, EECE 5830, Fall 2023
# 13 November 2023

from socket import *
import hashlib
import random
import numpy as np
import time

# documentation link: https://docs.python.org/3/library/socket.html

# states
S_Wait_for_0_from_below = 0
S_Wait_for_1_from_below = 1

# structure of message from receiver:
# 16-bit checksum, 8-bit ACK, 8-bit SEQ

CHECKSUM_SIZE = 2
ACK = 255  # need to define the ack, should be bytes object with ACK and correct sequence number
SEQ_0 = 0
SEQ_1 = 255
ACK_SEQ_SIZE = 2

# PROPER_CHECKSUM = bytearray(b'\x00\x00')  # temporary value to use until checksum implemented

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


def checksum(message):

    result = bytearray()
    byte_sum = 0
    i = 0

    for bytes in message:
        byte_sum = message[i] + message[1]
        i = i + 1
    #       print(byte_sum)

    cksum = byte_sum.to_bytes(2, 'big')
    #    print(cksum)
    result.append(cksum[0])
    result.append(cksum[1])
    # print(result)
    return result


def split_packet(message):
    copy_msg = bytearray(message)
    checksum = copy_msg[0:CHECKSUM_SIZE]
    ack_response = copy_msg[CHECKSUM_SIZE]
    seq_response = copy_msg[CHECKSUM_SIZE + 1]
    data = copy_msg[DATA_OFFSET:]

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

        self.oncethru = 0
        self.name_receiver = name
        self.port_receiver = port
        self.socket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = using IPv4, SOCK_DGRAM = Datagram,
        # UDP = User Datagram Protocol
        # Windows socket API: https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-socket
        # By default, the socket object is in blocking mode
        self.data_buffer = []
        print("Server initialized")

        self.num_corrupt_acks = 0

    def send(self, message):
        self.socket.sendto(message, (self.name_receiver, self.port_receiver))
        # client sends message (converted to Bytes) to server

    # receive
    # input: bdata_size
    def receive(self, bdata_size):
        message, server_address = self.socket.recvfrom(bdata_size)

        return message, server_address

    def next_state(self, bdata_size, corrupt_level): # need to add
        if self.state == S_Wait_for_0_from_below:
            msg, client_address = self.receive(bdata_size)
            csum, ack_response, seq_response, data = split_packet(msg)

            cs_message = bytearray()
            cs_message.append(ack_response)
            cs_message.append(seq_response)
            cs_message.extend(data)
            new_checksum = checksum(cs_message)

            # ack message to send back
            ack_msg = bytearray()

            # everything except the checksum field is passed to the checksum function
            ack_cs_msg = bytearray()
            ack_cs_msg.append(ACK)

            if not is_corrupt(csum, new_checksum) and is_ack(ack_response, seq_response, SEQ_0):
                # deliver data
                self.data_buffer.append(data)
                # send pos ack
                ack_cs_msg.append(SEQ_0)
                ack_cs = checksum(ack_cs_msg)

                ack_msg.extend(ack_cs)
                ack_msg.extend(ack_cs_msg)

                corrupted = np.random.choice([0,1], size=1, replace=True, p=[1-corrupt_level,corrupt_level])
                if corrupted == 1: # corrupt the ack
                    self.num_corrupt_acks += 1
                    # print("Number of Corrupt acks so far: ",self.num_corrupt_acks)
                    ack_msg = bytearray(corruptor(ack_msg))
                self.socket.sendto(ack_msg, client_address)

                self.oncethru = 1
                return S_Wait_for_1_from_below
            else:

                if self.oncethru == 1:
                    ack_cs_msg.append(SEQ_1)
                    ack_cs = checksum(ack_cs_msg)

                    ack_msg.extend(ack_cs)
                    ack_msg.extend(ack_cs_msg)

                    corrupted = np.random.choice([0, 1], size=1, replace=True, p=[1 - corrupt_level, corrupt_level])
                    if corrupted == 1:  # corrupt the ack
                        self.num_corrupt_acks += 1
                        # print("Number of Corrupt acks so far: ", self.num_corrupt_acks)
                        ack_msg = bytearray(corruptor(ack_msg))

                    self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_0_from_below

        elif self.state == S_Wait_for_1_from_below:
            msg, client_address = self.receive(bdata_size)
            csum, ack_response, seq_response, data = split_packet(msg)

            cs_message = bytearray()
            cs_message.append(ack_response)
            cs_message.append(seq_response)
            cs_message.extend(data)
            new_checksum = checksum(cs_message)

            # ack message to send back
            ack_msg = bytearray()

            # everything except the checksum field is passed to the checksum function
            ack_cs_msg = bytearray()
            ack_cs_msg.append(ACK)

            if not is_corrupt(csum, new_checksum) and is_ack(ack_response, seq_response, SEQ_1):
                # deliver data
                self.data_buffer.append(data)
                # send pos ack
                ack_cs_msg.append(SEQ_1)
                ack_cs = checksum(ack_cs_msg)

                ack_msg.extend(ack_cs)
                ack_msg.extend(ack_cs_msg)

                corrupted = np.random.choice([0, 1], size=1, replace=True, p=[1 - corrupt_level, corrupt_level])
                if corrupted == 1:  # corrupt the ack
                    self.num_corrupt_acks += 1
                    # print("Number of Corrupt acks so far: ", self.num_corrupt_acks)
                    ack_msg = bytearray(corruptor(ack_msg))

                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_0_from_below
            else:
                ack_cs_msg.append(SEQ_0)
                ack_cs = checksum(ack_cs_msg)

                ack_msg.extend(ack_cs)
                ack_msg.extend(ack_cs_msg)

                corrupted = np.random.choice([0, 1], size=1, replace=True, p=[1 - corrupt_level, corrupt_level])
                if corrupted == 1:  # corrupt the ack
                    self.num_corrupt_acks += 1
                    # print("Number of Corrupt acks so far: ", self.num_corrupt_acks)
                    ack_msg = bytearray(corruptor(ack_msg))

                self.socket.sendto(ack_msg, client_address)
                return S_Wait_for_1_from_below
        else:
            return 10  # error


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match client)#: "))
    # sender port is not specified since OS specifies that, and we do not care what it is
    # This is the receiver port, so whichever system is designated as a receiver will use this to listen

    cor_percent = int(input("Specify level of corruption as a percentage to the nearest whole number: "))
    cor_prob = cor_percent/100

    server = UDPServer(name_receiver, port_receiver)
    server.socket.bind(('', server.port_receiver))

    buffer_size = 1028
    # Receives packets from client with a message buffer size on each packet as 2048 Bytes


    receiver_state = server.next_state(buffer_size, cor_prob)
    server.state = receiver_state
    while server.state != S_Wait_for_1_from_below:  # we must receive the first packet successfully to move on
        receiver_state = server.next_state(buffer_size, cor_prob)
        server.state = receiver_state

    # print("Got Here!")
    data = server.data_buffer.pop(0)
    # print(data)
    num_packets = int.from_bytes(data)

    packet_index = 0
    tick = time.perf_counter_ns()
    while packet_index < num_packets:
        receiver_state = server.next_state(buffer_size, cor_prob)
        if server.state != receiver_state:
            packet_index += 1

        server.state = receiver_state

    tock = time.perf_counter_ns()

    delt = tock - tick
    print("time elapsed (ns): ", delt)

    # "copy.bmp" is where the data from the packets received get written to, location is local to the code directory
    deliver_data(server.data_buffer, "copy.bmp")
