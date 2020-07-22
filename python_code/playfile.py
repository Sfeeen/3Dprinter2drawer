import serial
import time
import usbcom

port = usbcom.serial_ports()[0]
# Open grbl serial port
s = serial.Serial(port, 115200)

# Open g-code file

f = open('foto_bycontour.gcode', 'r');

# Wake up grbl
#s.write(str.encode("\r\n\r\n"))
time.sleep(5)  # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input -> flush everything printer says at startup

# Stream g-code to grbl
for line in f:
    l = line.strip()  # Strip all EOL characters for streaming
    print('Sending: ' + l,)
    s.write(str.encode(l + '\n'))  # Send g-code block to grbl
    grbl_out = s.readline()  # Wait for grbl response with carriage return
    print(' : ' + str(grbl_out.strip()))

# Close file and serial port
name = input("Click enter to stop")
f.close()
s.close()