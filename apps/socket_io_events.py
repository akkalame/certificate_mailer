from apps import _dict, socketio

def open_uri(uri):
    socketio.emit("open_new_tab", {"url": uri})

def show_alert(msg):
    socketio.emit("dialog", {"type": "alert", "msg": msg})