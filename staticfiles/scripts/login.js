const DATASET_LOGIN = document.currentScript.dataset;
$(document).ready(prepareLogin());

function hideShowPwd() {
	if ($('#password_input')[0].type == 'password') {
		$('#password_input')[0].type = 'text';
		$('#hide_show_image')[0].src = DATASET_LOGIN.visibilityOn;
	} else {
		$('#password_input')[0].type = 'password';
		$('#hide_show_image')[0].src = DATASET_LOGIN.visibilityOff;
	}
}

function prepareLogin() {
	// events
	$('#email_input').on('keydown', onInputEnter);
	$('#email_input').on('focusin', { image: '#email_image' }, onInputFocusIn);
	$('#email_input').on('focusout', { image: '#email_image' }, onInputFocusOut);

	$('#password_input').on('keydown', onInputEnter);
	$('#password_input').on('focusin', { image: '#password_image' }, onInputFocusIn);
	$('#password_input').on('focusout', { image: '#password_image' }, onInputFocusOut);

	// enable or disable button
	checkLogin();
}

function checkLogin() {
	let emailValue = $('#email_input')[0].value;
	let passwordValue = $('#password_input')[0].value;

	if (emailValue != '' &&
		passwordValue != '') {
		enableButton('#login_button_div');
	} else {
		disableButton('#login_button_div');
	}

	// hide failed text if it is shown
	deactivateElement('#failed_div');
}

function login() {
	// disable events
	disableEvents('#login_button_div');

	// get values
	let emailValue = $('#email_input')[0].value;
	let passwordValue = $('#password_input')[0].value;

	fetch(DATASET_LOGIN.loginAccountUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'email': emailValue,
			'password': passwordValue
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			openPage(DATASET_LOGIN.homeViewUrl);
		} else if (data.response == 'awaiting_approval') {
			checkLogin();
			approvalPopup();
		} else {
			checkLogin();

			// show failed text
			$('#failed_text')[0].innerText = 'Login failed. Please try again!';
			activateElement('#failed_div');
		}
	});
}