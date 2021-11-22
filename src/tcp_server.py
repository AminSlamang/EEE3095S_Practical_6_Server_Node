# EEE3095S Practical 6 - IoT Application
# Pi 2 - Web server
# KTNRIO001 - Rio Katundulu
# SLMAMI010 - Amin Slamang

import socket
import threading 
from typing import Text
from flask import Flask, send_file, render_template
from datetime import datetime

app = Flask(__name__)
l_10_Received = []
status_received = False
current_status = ""
HOST = '192.168.137.162' 
PORT = 10000        

# setup tcp socket and listen for a new connection.
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    newconnection, addr = s.accept()
    print ('Connected on address: ', addr)

#Turns on sampling of Pi 1 and returns a confirmation message when it does.
@app.route("/on")
def sending():
    message = "0,on"
    newconnection.sendall(str.encode(message))
    return "<center>Sensor turned on</center>"

# Turns off sampling of Pi 1 and returns a confirmation message when it does.
@app.route("/off")
def not_sending():
    message = "0,off"
    newconnection.sendall(str.encode(message))
    return "<center>Sensor turned off</center>"

# Returns whether the pi is sampling or not and the last time it sampled.
@app.route("/status")
def get_status():
    global status_received
    message = "1,Status"
    newconnection.sendall(str.encode(message))
    while(not status_received):
        pass
    status_received = False
    return "<center>"+current_status+"</center>"

# Returns the last 10 samples that were obtained (or however many they are if less than 10).
@app.route("/logs")
def log():
    log = "<center><pre>Light Level  | Temperature |   Date   |   Time  <br>"
    for entry in l_10_Received:
        data = entry.split(";")
        log = log + "    " + data[0] + "    |    " + data[1] + "    | " + data[2] + " | " + data[3] + "<br>"
    log += "</pre></center>"
    return log

# Downloads a csv file with all the recorded samples.
@app.route("/get-csv", methods=['GET','POST'])
def download_logs():
    return send_file("../sensorlog.csv",as_attachment=True,mimetype="text/csv")

# Stops sampling and shows a shutdown screen.
@app.route("/exit")
def exit():
    global run_thread
    run_thread = False
    message = "X,EXIT"
    newconnection.sendall(str.encode(message))
    return "<center>Server shutting down.</center>"

# Starting of threads that <???> and loads webpage.
@app.route("/")
def main():   
    thread = threading.Thread(target=receive_data)
    thread.daemon = True
    thread.start()
    return render_template('Webserver.html', title='Webserver')

# Recieves data, processes it, stores it in a csv file and stores last 10 recorded.
def receive_data():
    global l_10_Received, current_status, status_received,newconnection
    path = "/usr/src/app/sensorlog.csv"
    with newconnection:
        f = open(path,"w")
        f.write("Light;Temperature;Date;Time\n")
        f.close()
        while True:
            data = newconnection.recv(1024)
            data = data.decode("utf-8")
            if(data[0] =="D"):
                print('\nReceived', data)
                if (len(l_10_Received) == 10):
                    l_10_Received.pop(0)
                data_write = (data[1:]+";"+datetime.now().date().strftime("%d:%m:%y")+";"+str(datetime.now().time())[0:8])
                l_10_Received.append(data_write)
                f = open(path,"a")
                f.write(data_write + '\n')
                f.close()
                if not data: break
            elif(data[0] == "S"):
                current_status = data[2:]
                status_received = True
    quit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
quit()
