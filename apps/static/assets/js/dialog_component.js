
function createModal(options) {
	// Create the modal structure
	var modal = $(`<div class="modal fade" tabindex="-1" role="dialog" data-id="${options.dataId}" type="${options.type}"></div>`);
	var modalDialog = $('<div class="modal-dialog" role="document"></div>').appendTo(modal);
	var modalContent = $('<div class="modal-content"></div>').appendTo(modalDialog);
	var modalHeader = $('<div class="modal-header"></div>').appendTo(modalContent);
	var modalBody = $('<div class="modal-body"></div>').appendTo(modalContent);
	if (options.buttons)
		var modalFooter = $('<div class="modal-footer"></div>').appendTo(modalContent);

	// Set the title and body content from options
	$('<h5 class="modal-title"></h5>').text(options.title).appendTo(modalHeader);
	$('<button type="button" class="close" data-dismiss="modal" aria-label="Close">').append('<span aria-hidden="true">&times;</span>').appendTo(modalHeader);

	// Add buttons if provided
	if (options.buttons) {
		let btn;
		$.each(options.buttons, function(index, button) {
			btn = $('<button type="button" class="btn"></button>');
			btn.on("click", button.call || function(){});
			$.each(button.attrs || [], function(index, attr) {
				btn.attr(attr.name, attr.value);
			});
			btn.addClass(button.class).text(button.text).appendTo(modalFooter);
		});
	}

	// Append the modal to the body
	$('body > .wrapper').append(modal);

	// Return the modal object for further manipulation
	return modal;
}

function modal_form(options={}){
	let title = options.title || "Formulário"
	let dataId = title.toLowerCase().replace(" ","_");
	//let msg = options.msg || "";
	let modal = $(`div[data-id='${dataId}'][type='form']`);
	let confirm = function(){
		let formData = $(`#form_${dataId}`).serializeArray();
		options.confirm(formData);
	} || function(){};
	if (modal.length < 1){
		modal = createModal(
			{
				title: title, 
				type: "form", 
				dataId: dataId,
				buttons: [
					{
						class: "btn-primary",
						text: "Salvar",
						call: confirm,
						attrs: [{name:"data-dismiss", value:"modal"}]
					},
					{
						class: "btn-danger",
						text: "Cancel",
						attrs: [{name:"data-dismiss", value:"modal"}]
					}
				]
			}
		);
	}
	let modalBody = modal.find(".modal-body");
	modalBody.empty();
	let form = $(`<form id="form_${dataId}"></form>`).appendTo(modalBody);
	console.log(form);
	let row;
	$.each(options.fields || [], function(index, field){
		row = $(`<div class="row"></div>`).appendTo(form);
		$(`<label>${field.label}</label>`).appendTo(row);
		$(field.content).appendTo(row);
	});
	modal.modal("show");
}

function modal_msgprint(options={}){
	let title = options.title || "Notification"
	let dataId = title.toLowerCase();
	let msg = options.msg || "";
	let modal = $(`div[data-id='${dataId}'][type='msgprint']`);
	if (modal.length < 1){
		modal = createModal({title: title, type: "msgprint", dataId: dataId});
	}
	let modalBody = modal.find(".modal-body");
	$(`<p>${msg}</p>`).appendTo(modalBody);
	modal.modal("show")
}

function modal_progress(options={}){
	let title = options.title || "Progress"
	let dataId = title.toLowerCase();
	let description = options.description || "";
	let count = options.count || 0;
	let total = options.total || 100
	let modal = $(`div[data-id='${dataId}'][type='progress']`);

	let bar, progress, barDesc;

	if (modal.length < 1){
		modal = createModal({title: title, type: "progress", dataId: dataId});
		bar = $(`<div class="progress"></div>`);
		progress = $(`<div class="progress-bar bg-primary" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="${total}" ></div>`).appendTo(bar);
		barDesc = $(`<span class="progress-description"></span>`);
		modal.modal("show");
	}else{
		progress = modal.find(".progress-bar");
	}
	
	
	let modalBody = modal.find(".modal-body");
	if (bar)
		bar.appendTo(modalBody)
	if (barDesc)
		barDesc.appendTo(modalBody)

	let percentage = count * 100 / total;
	progress.attr("aria-valuenow", `${count}`);
	progress.css("width", `${percentage}%`);
	modalBody.find(".progress-description").text(description);
	
	if (count >= total)
		modal.modal("dispose");
}

function alertToast(options={}){
	
	var Toast = Swal.mixin({
		toast: true,
		position: 'top-end',
		showConfirmButton: false,
		timer: 4000
	});
	let args = {
		icon: options.icon || "info",
		title: options.title || ""
	}

	Toast.fire(args);
}