const DATASET_APPROVAL = document.currentScript.dataset;
let openLogin;

function approvalPopup(redirect=false) {
	openLogin = redirect;

	// setup popup
	setup();

	// show popup
	$('#popup').modal('show');
}

function setup() {
	// name
	$('#popup_name_text')[0].innerText = 'ACCOUNT APPROVAL';

	// content
	$('#popup_content_text')[0].innerText = 'Your registration request has been sent.\nPlease wait while we approve your account.\nYou will recieve confirmation on your email when account becomes ready for use.\n\nThank you,\nTraxellPlast';
}

function closePopup() {
	$('#popup').modal('hide');
}

$('#popup').on('hidden.bs.modal', function() {
	// name 
	$('#popup_name_text')[0].innerText = '';

	// content
	$('#popup_content_text')[0].innerText = '';

	if (openLogin) {
		openPage(DATASET_APPROVAL.loginViewUrl);
	}
});