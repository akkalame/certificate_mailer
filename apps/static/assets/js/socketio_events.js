$(function(){
    const socket = io();

    /*const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    */
    /*sendButton.addEventListener('click', () => {
            const message = messageInput.value;
            socket.emit('message', message);
            messageInput.value = '';
    });*/

    socket.on('open_new_tab', (data) => {
        window.open(data.url);
    });

    socket.on("dialog", (data) =>{
        if (data.type == "alert"){
            alert(data.msg);
        }
        else if (data.type == "msgprint"){
            alert(data.msg);
        }
        
    });

    socket.on("remove_tab_with_url", (data) => {
        const url = window.location.pathname;
        console.log("url pestana", url)
        // Comparar la URL con la cadena "/home"
        if (url.startsWith(data.url)){
            window.close();
        }
    });
});
