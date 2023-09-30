# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.

def make_packet(filename):
    pass


if __name__ == '__main__':

    PACKET_SIZE = 1024
    f = open("C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/LAND2.BMP", "rb")
    print(f)

    packet_list = []
    packet = f.read(PACKET_SIZE)
    packet_list.append(packet)

    while len(packet) == PACKET_SIZE:
        print(f.tell())
        packet = f.read(PACKET_SIZE)
        packet_list.append(packet)


    f_write = open("C:/Users/Michael Burton/Documents/UML/Fall2023/Network/Project/LAND2_Copy.BMP", "wb")

    for i in packet_list:
        f_write.write(i)

    f.close()
    f_write.close()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
