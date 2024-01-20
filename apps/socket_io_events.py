from apps import _dict, socketio

def open_uri(uri):
    socketio.emit("open_new_tab", {"url": uri})

def show_alert(msg):
    socketio.emit("dialog", {"type": "alert", "msg": msg})

def msgprint(msg):
    socketio.emit("dialog", {"type": "msgprint", "msg": msg})

def remove_tab_with_url(url):
    socketio.emit("remove_tab_with_url", {"url": url})

