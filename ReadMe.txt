EECE 5830 Network Design Principles, Protocols and Applications
Section 201
10/30/2023
Title: Phase 3
Michael Burton, Jocelyn Frechette, Jesse Haynes-Lewis
Environment
OS: Windows
Language: Python
Versions: 3.11.5
IDE: PyCharm 2023.2.1
Files Included in Submission:
1. UDPClient.py
    This application contains the relevant code required to generate the Client side of the UDP connection. In this configuration the Client side 
    of the connection is responsible for locating and packetizing the file-for-transfer, as well as sending individual packets across the link to the Server side. 
    For this phase, it also contains functions for sender side message corruption, adding sequence numbers, ack, and checksum to the data being sent.
    There is also timing code for benchmarking how long the sender remained active.

    To include data packet error, input an integer when prompted indicating the percentage of packets that will be initially sent corrupt.
    
2. UDPServer.py
    
    This Application contains the relevant code required to generate the Server side of the UDP connection. In this configuration the Server side 
    is responsible for receiving each individual packet and parsing each to recreate the original file from the Client side. For this phase, it also contains functions for receiver side message corruption, adding sequence numbers, ack, and checksum of the ack packet. There is also timing code for benchmarking how long the receiver remained active.

    To include ack packet error, input an integer when prompted indicating the chance any one ack packet will be sent corrupt.

3. Lavender.jpg
    This is the test file used for verification of the applications described above. The file is 1.01 MB in length and is in the Joint Photographic Experts Group file format. 
    Sourced from: https://www.istockphoto.com/photos/prairie-praise

4. ReadMe.txt
    Descriptor of relevant project items submitted
5. Design.docx
    In depth design document describing the functionality of the UDPClient.py and UDPServer.py applications.
Set Up Instructions:
    -This project uses Python 3.11.5 (noted above)
        -This code is not guaranteed to work on any other version, especially 3.10 and below
    -IDE: PyCharm 2023.2.1 (noted above)
        -Pycharm is not a requirement, just ensure that both programs can be executed at the same time on the same host
            -NOTE: The provided UDPClient.py and UDPServer.py applications are configured to run on the SAME host, within the same directory.
            - You must install the numpy library, which can be done by going to File->Settings->Project: NetworkDesign_ProgrammingProject->Python Interpreter
            - Then, in the right pane, press the "+", then type "numpy" in the search bar, check the box for "Install to user's site packages directory".
            - Click install package. Then, wait for numpy to be installed. The code should be runnable.

        -Guide for pycharm is also in the execution, ensure you have access to the socket library (should be available in standard configuration)
        -If you would like to use a different image than LAND2.BMP, add the file to the same directory as the code, and change the line in UDPClient.py 
         that says "packets = Make_Packet("LAND2.BMP", 2048)" to "packets = Make_Packet("<<your file name>>", 2048)"
        -If you would like to change the packet size, both the "packets = Make_Packet("LAND2.BMP", <<packet_size>>)" in UDPClient.py and "received_packets = 
         server.receive(<<packet_size>>)" in UDPServer.py should be updated to the desired value, in bytes
