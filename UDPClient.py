# Michael Burton,Jocelyn Frechette, Jesse Haynes-Lewis
# UDPClient.py
# Phase 4, EECE 5830, Fall 2023
# 13 November 2023
import struct
from socket import *
import numpy as np
from math import floor
import time

# documentation link: https://docs.python.org/3/library/socket.html


# structure of message from sender:
# 16-bit checksum, 8-bit ACK, 8-bit SEQ, N-byte data

CHECKSUM_SIZE = 2
ACK = 255  # need to define the ack, should be bytes object with ACK and correct sequence number
SEQ_0 = 0
SEQ_1 = 255
ACK_SEQ_SIZE = 2

DATA_OFFSET = ACK_SEQ_SIZE + CHECKSUM_SIZE


#
def inc_seq_num(seq_num):
    seq_num = (seq_num + 1) % 256
    return seq_num


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

    # first packet is the number of packets being sent, this is setting up the second packet sent, so seq=2 is used
    seq_to_send = 2
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

    seq_to_send = 3
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
        packet_list.append(packet)

        seq_to_send = inc_seq_num(seq_to_send)

    data = struct.pack(">I", len(packet_list))

    packet = bytearray()

    cs_packet = bytearray()
    cs_packet.append(ACK)
    cs_packet.append(1)
    cs_packet.extend(data)
    csum = checksum(cs_packet)

    packet.extend(csum)
    packet.append(ACK)
    packet.append(1)
    packet.extend(data)

    packet_list.insert(0, packet)

    print("Packets Made. Number of packets: ", len(packet_list), "file position: ", f.tell())
    print("First packet: ", packet_list[0])
    f.close()
    return packet_list
def corruptor(byte_object):
    cor_byte_object = [0]*len(byte_object)
    # Function takes in the packet list and will perform a randomized corruption on a certain percetage of packets
    for j in range(len(byte_object)):
        cor_byte_object[j] = ~byte_object[j] & 255
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


# Takes a list of packets and a percentage
# returns a random percentage-sized selection of indices from the list of packets,
def rand_indices(pack_list, percent_ind):
    num_pack = int(floor(len(pack_list) * (percent_ind / 100)))
    ind = np.random.choice(len(pack_list), size=num_pack, replace=False, )
    ind.sort()
    return ind

class UDPClient:
    # Initializes the UDP Client with name and port
    def __init__(self, name, port, tt, window, packet_list, cor_percent, dropped_percent):
        self.time_timeout = tt
        self.name_receiver = name
        self.port_receiver = port
        self.socket = socket(AF_INET, SOCK_DGRAM)  # AF_INET = using IPv4, SOCK_DGRAM = Datagram,
        self.base = 1
        self.nextseqnum = 1
        self.window = window
        self.packet_list = packet_list
        self.packet_list_length = len(packet_list)
        self.ind_next_seq = 0  # keeps track of the index in packet_list the nextseqnumber is referring to
        self.ind_base = 0  # keeps track of the index in packet_list the base is referring to
        self.corr_prob= cor_percent / 100 # list(rand_indices(self.packet_list, cor_percent))
        self.loss_prob = dropped_percent / 100 # list(rand_indices(self.packet_list, dropped_percent))
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
        self.socket.settimeout(self.time_timeout)

        # if the recvfrom function takes longer than time_timeout to receive data from the server
        # Timeout
        try:
            message, server_address = self.socket.recvfrom(bdata_size)
        except TimeoutError:
            message = "TimeoutError"

        return message

#    def toggle_timeout(self):
#        self.timeout = not self.timeout

    def corr_loss_send(self, index_to_send):
        # if index_to_send in self.loss_ind and index_to_send in self.corr_ind:
        #     self.loss_ind.remove(index_to_send)
        #     self.corr_ind.remove(index_to_send)
        # elif index_to_send in self.loss_ind:
        #     self.loss_ind.remove(index_to_send)
        # elif index_to_send in self.corr_ind:
        #     self.corr_ind.remove(index_to_send)
        #     self.send(bytearray(corruptor(self.packet_list[index_to_send])))
        # else:
        #     self.send(self.packet_list[index_to_send])
        corrupted = np.random.choice([0, 1], size=1, replace=True, p=[1 - self.corr_prob, self.corr_prob])
        if corrupted == 1:  # corrupt the data packet
            self.send(bytearray(corruptor(self.packet_list[index_to_send])))
        lost = np.random.choice([0, 1], size=1, replace=True, p=[1 - self.loss_prob, self.loss_prob])
        if lost == 0:
            self.send(self.packet_list[index_to_send])

    def next_state(self, bdata_size):
        if (self.nextseqnum - self.base) % 256 < self.window and self.ind_next_seq < self.packet_list_length:
            # print("Sending ind_next_seq: ", self.ind_next_seq)
            self.corr_loss_send(self.ind_next_seq)
            self.nextseqnum = inc_seq_num(self.nextseqnum)
            self.ind_next_seq += 1
    #        print("Sent")
        else:
            received_msg = self.receive(bdata_size)
            if received_msg == "TimeoutError":
                # print("Timeout: Sending up to nextseqnum starting with: ", self.ind_base)
                for i in range(0, (self.nextseqnum - self.base) % 256):
                    if self.ind_base + i < self.packet_list_length:
                        self.corr_loss_send(self.ind_base + i)
                        # print(self.ind_base+i, self.ind_next_seq)
            else:
                csum, ack_response, seq_response = split_ack_packet(received_msg)
                cs_packet = bytearray()
                cs_packet.append(ack_response)
                cs_packet.append(seq_response)
                new_checksum = checksum(cs_packet)
                if not is_corrupt(csum, new_checksum):
                    # recalculating the new absolute index in the array of packets for the base
                    # The difference between the seq_response and the base value, wrapped around
                    # Then add 1 to get to the next unacknowledged packet number
                    # Then add that difference to the ind_base

                    self.ind_base += (seq_response - self.base + 1) % 256
                    self.base = inc_seq_num(seq_response)
                    # print("self.indbase: ", self.ind_base)
                    # print("incremented base")


# Run the program from here
if __name__ == '__main__':
    name_receiver = '127.0.0.1'  # data via the loopback connector
    port_receiver = int(input("Specify receiver port (should match server)#: "))

    time_of_timeout_ms = int(input("Specify the timeout duration in whole milliseconds: "))
    cor_percent = int(input("Specify level of corruption as a percentage to the nearest whole number: "))
    dropped_percent = int(input("Specify level of packet loss as a percentage to the nearest whole number: "))
    N_w = int(input("Specify the sender window size: "))
    # # sender port is not specified since OS specifies that, and we do not care what it is
    # # This is the receiver port, so whichever system is designated as a receiver will use this to listen
    #
    time_of_timeout_s = time_of_timeout_ms/1000

    # make packets
    packets = Make_Packet("Lavender.jpg", 1024)

    # instantiate the client
    client = UDPClient(name_receiver, port_receiver, time_of_timeout_s, N_w, packets, cor_percent, dropped_percent)

    # Calculate the number of packets needed to be corrupted, a uniform distribution is used to select which index in
    # the packet list that will be corrupted

    packet_index = 0
    tick = time.perf_counter_ns()

    while client.ind_base < len(packets):
        client.next_state(4)

    tock = time.perf_counter_ns()
    delt = tock-tick
    print("time elapsed (ns): ", delt)
