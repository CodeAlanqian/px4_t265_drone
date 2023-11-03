import serial
import time

serial_port = serial.Serial(
        port="/dev/ttyUSB0",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        )
data1 = ""
flag = True
x = float()
y = float()



while(True):
    
    while serial_port.inWaiting() > 0:
        start = time.time()
        data = serial_port.read()
        if data != ",":
            data1 = data1+data
        else:    
            if len(data1) > 0:      
                if flag:
                        x = float(data1)
                else:
                        y = float(data1)
                data1 = ""  
                flag = not flag
            else:
                flag = not flag
    print("FPS",1/(time.time() - start))
    print(x,y)
    
    




    