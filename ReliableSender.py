# Implemented by Chad Miller, Dec. 2013
import sys
import socket
import getopt
import Checksum
import BasicSender
import Ptr
import pdb
'''
Implements a reliable sender.
'''
class ReliableSender(BasicSender.BasicSender):

    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet
    
    # Main sending loop.
    def start(self):
        seqno = 0
        msg_type = Ptr.Ptr(None) # Need pointer to change its state in 'init'
        not_ack = {} # Packets that haven't been acknowledged
        msg = self.infile.read(500)
        done = False
        while 1:
            
            next_msg = self.infile.read(500)
            self.init(msg_type, seqno, next_msg)
            
            if not done:
                packet = self.make_packet(msg_type.get(),seqno,msg)
                self.send(packet)
                not_ack[seqno] = packet             
                print "sent: %s" % packet
                response = self.receive(.02) #start timer
                if response is not None:
                    self.handle_response(response)
                    del not_ack[seqno]

                else:
                    self.resend(Ptr.Ptr(not_ack)) # Look for unacknowledged messages and re-send
                     
                if msg_type.get() == 'end':
                    done = True

                seqno += 1
        
                if not_ack: #Continue until all messages acknowledged
                    continue
                else:
                    break


    # Verifies all msgs received, if not resends.
    def resend(self, not_ack):
        packet = 0
        dic = not_ack.get() #dic of seqno --> packet
        while 1:
            if dic:
                for seqno in dic.keys():
                    packet = dic[seqno]
                    self.send(packet)
                    response = self.receive(.02)
                    if response is not None:
                        self.handle_response(response)
                        del dic[seqno]
                        not_ack.set(dic)

            else:
                return 

    def init(self, msg_type, seqno, next_msg):
        msg_type.set('data')
        if seqno == 0:
            msg_type.set('start')
        elif next_msg == "":
            msg_type.set('end')
           
            
   
'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "Reliable Sender"
        print "Sends data unreliably from a file or STDIN."
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:", ["file=", "port=", "address="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a

    s = ReliableSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
