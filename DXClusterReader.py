import telnetlib
import time

class UsernameError(ValueError):
    def __init__(self, arg):
        self.args = arg

class DXClusterReader:
    def __init__(self, host="128.192.52.40", port=599, callsign="sq6sfs"):
        self.callsign = callsign
        self.spots = []

        self.cluster = telnetlib.Telnet(host=host, port=port)
        self.login(self.callsign)
        self.cluster.read_until(">"),
        self.cluster.read_until("\n")

    def login(self, callsign):
        self.cluster.read_some()
        self.cluster.write(callsign + "\r\n")
        welcome = self.cluster.read_some()
        if "invalid" in welcome:
            raise UsernameError

    def get_new_spots(self):
        while True:
            read = self.cluster.read_until('\n')

            if read:
                self.spots.append(read)

                for i, spot in enumerate(self.spots):
                    print i+1,
                    print ": ",
                    print spot,
                    
                print 20*"- ",
                print len(self.spots),
                print 20*" -"
            else:
                time.sleep(1)

    def disconnect(self):
        print "Disconnecting 2..."
        self.cluster.close()

if __name__ == '__main__':
    try:
        d = DXClusterReader()
    except UsernameError:
        print "Login Error - Bad Username"
    except KeyboardInterrupt:
        print "Ending program!!!"
    else:
        d.get_new_spots()
    finally:
        print "Disconnecting 1..."
        d.disconnect()
