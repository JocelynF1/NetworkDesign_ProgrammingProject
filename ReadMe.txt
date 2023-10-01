EECE 5830 Network Design Principles, Protocols and Applications
Section 201
10/01/2023
Title: Phase 2
Michael Burton, Jocelyn Frechette, Jesse Haynes-Lewis
Environment
OS: Windows
Language: Python
Versions: 3.11.5
IDE: PyCharm 2023.2.1
Files Included in Submission:
1. UDPClient.py
    This application contains the relevant code required to generate the Client side of the UDP connection. In this configuration the Client side 
    of the connection is responsible for locating and packetizing the file-for-transfer, as well as sending individual packets across the link 
    to the Server side.
2. UDPServer.py
    
    This Application contains the relevant code required to generate the Server side of the UDP connection. In this configuration the Server side 
    is responsible for receiving each individual packet and parsing each to recreate the original file from the Client side.
3. LAND2.bmp
    This is the test file used for verification of the applications described above. The file is 769 kB in length and is in the bitmap file format. 
    Sourced from: https://www.fileformat.info/format/bmp/sample/dc59e50046b84768b5df4191ec16b9c3/view.htm
4. ReadMe.txt
    Descriptor of relevant project items submitted
5. Design.docx
    In depth design document describing the functionality of the UDPClient.py and UDPServer.py applications.
Set Up Instructions:
    -This project uses Python 3.11.5 (noted above)
    -IDE: PyCharm 2023.2.1 (noted above)
        -Pycharm is not a requirement, just ensure that both programs can be executed at the same time on the same host
            -NOTE: The provided UDPClient.py and UDPServer.py applications are configured to run on the SAME host, within the same directory.
        -Guide for pycharm is also in the execution, ensure you have access to the socket library (should be available in standard configuration)
        -Guide for IDLE:
            -Open IDLE
            -Open and run UDPServer.py
            -Open another instance of IDLE
            -Open and run UDPClient.py
            -Follow the prompts within the console for each application running, starting with the server side console.
            -INFO: Ensure that the system that is receiving is set up first (I.e. the Server side of the UDP connection (there will be a prompt to enter
                   the name and port number when it is ready)
            -The prompts within the console should guide the user through the process.
            -Once sending and receiving is complete, the Copy of the file received on the Server side should be located in the same directory as the 
             UDPClient.py and UDPServer.py applications.
        -If you would like to use a different image than LAND2.BMP, add the BMP file to the same directory as the code, and change the line in UDPClient.py 
         that says "packets = Make_Packet("LAND2.BMP", 2048)" to "packets = Make_Packet("<<your file name>>", 2048)"
        -If you would like to change the packet size, both the "packets = Make_Packet("LAND2.BMP", <<packet_size>>)" in UDPClient.py and "received_packets = 
         server.receive(<<packet_size>>)" in UDPServer.py should be updated to the desired value, in bytes
