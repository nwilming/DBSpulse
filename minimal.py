import sys
import zmq

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5558")

zip_filter = 'ET:'
# Subscribe to zipcode, default is NYC, 10001
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"

socket.setsockopt_string(zmq.SUBSCRIBE, u'ET')

# Process 5 updates
total_temp = 0
for update_nbr in range(5):
    print 'waiting for msg'
    string = socket.recv_string()
    print string
