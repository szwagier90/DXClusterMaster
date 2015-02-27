import telnetlib

#tn = telnetlib.Telnet(host="sr4dxc.jestok.com", port=9000)
tn = telnetlib.Telnet(host="128.192.52.40", port=599)

print tn.read_some(),

callsign = "sq6sfs"
tn.write(callsign + "\n")

print tn.read_until(">"),

m = list(tn.read_until("\n"))
print m
