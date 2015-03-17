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

    def get_next_spot(self):
        read = self.cluster.read_until('\n')

        if read:
            self.spots.append(read)
            yield read
        else:
            time.sleep(1)

    def disconnect(self):
        print "Disconnecting 2..."
        self.cluster.close()

if __name__ == '__main__':
    try:
        d = DXClusterReader()
        spots = d.get_next_spot()
        print spots.next()
    except UsernameError:
        print "Login Error - Bad Username"
    except KeyboardInterrupt:
        print "Ending program!!!"
    finally:
        print "Disconnecting 1..."
        d.disconnect()
