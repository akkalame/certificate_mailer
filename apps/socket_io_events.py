from apps import _dict, socketio

def open_uri(uri):
    socketio.emit("open_new_tab", {"url": uri})

def show_alert(content):
    socketio.emit("dialog", {"type": "alert", "content": content})

def msgprint(msg="", title=None):
    socketio.emit("dialog", {"type": "msgprint", "msg": msg, "title": title})

def progress( count=0, total=100, title=None, description=""):
    socketio.emit("dialog", {
        "type": "progress", 
        "description": description, 
        "title": title,
        "count": count,
        "total":total
    })

def remove_tab_with_url(url):
    socketio.emit("remove_tab_with_url", {"url": url})

