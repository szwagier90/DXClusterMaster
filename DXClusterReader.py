import telnetlib

#tn = telnetlib.Telnet(host="sr4dxc.jestok.com", port=9000)
tn = telnetlib.Telnet(host="128.192.52.40", port=599)

print tn.read_some(),

callsign = "sq6sfs"
tn.write(callsign + "\n")

#(1)read whole welcome message
print tn.read_until(">"),
print tn.read_until("\n")
#(1)

telnetString = ""
spots = []

import time
while True:
    read = tn.read_eager()

    if read:
        telnetString += read
        lines = telnetString.split("\n")
        if len(lines) > 1:
            spots.extend(lines[:-1])
            telnetString = lines[-1]

        for i, spot in enumerate(spots):
            print i+1,
            print ": ",
            print spot
            
        print 20*"- ",
        print len(spots),
        print 20*" -"

        if telnetString:
            print telnetString

        print 80*'#'
    else:
        time.sleep(1)
