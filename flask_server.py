#!/usr/bin/env python3
# --coding: utf-8 --
from flask import Flask, abort, redirect, url_for, render_template
from flask import Response,request
from flask import stream_with_context
from camera_pi_android import Camera
from gevent.pywsgi import WSGIServer

#import from other files
from multiprocessing import Process,Pipe 
from ultrasonic import *
from motor import *
app = Flask(__name__)


stream_headers = {
        'Age': 0,
        'Cache-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
}

flag_dict = {'pa':0, 'up':1, 'lef':2, "rig":3}

@app.route('/',methods=["post","get"])
def show_index():
    #global queue 
    global parent_pipe
    #global share_state
    try:
        button = request.form["button"]
        if button:
            parent_pipe.send(flag_dict[button])
            #queue.put(flag_dict[button])
            #share_state.value = flag_dict[button]
            print(button)
    except:
       None
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        wrapped_frame = (b'--frame\r\n' +
                         b'Content-Type: image/jpeg\r\n' +
                         bytes('Content-Length: {}\r\n\r\n'.format(len(frame)),encoding='UTF-8')
                         + frame + b'\r\n')
        yield wrapped_frame


@app.route('/video_feed')
def video_feed():
    global headers
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype=stream_headers['Content-Type'],
                    headers=stream_headers,
                    status=200)

if __name__=='__main__':
    #queue= Queue()
    parent_pipe,child_pipe = Pipe()
    #share_state = Value('i',-1,lock = False)
    p1 = Process(target=motion_ctrol,args=(child_pipe,))
    p1.start()
    http_server = WSGIServer(('', 80), app)
    try:
        http_server.serve_forever()
    except:
        sys.exit(0)        

   # app.run(host='0.0.0.0',port=80,debug=F:alse,threaded=True)#开启进程支持和线程支持
