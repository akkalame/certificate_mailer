$(function(){
	const socket = io();

	socket.on('open_new_tab', (data) => {
		window.open(data.url);
	});

	socket.on("dialog", (data) =>{
		if (data.type == "progress"){
			modal_progress(data);
		}
		else if (data.type == "msgprint"){
			modal_msgprint(data);
		}
		else if (data.type == "alert"){
			alertToast(data.content);
		}
		
	});

});
