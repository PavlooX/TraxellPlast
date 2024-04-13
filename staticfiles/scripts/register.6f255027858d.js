const DATASET_REGISTER = document.currentScript.dataset;
$(document).ready(prepareRegister());

function hideShowPwd() {
	if ($('#password_input')[0].type == 'password') {
		$('#password_input')[0].type = 'text';
		$('#hide_show_image')[0].src = DATASET_REGISTER.visibilityOn;
	} else {
		$('#password_input')[0].type = 'password';
		$('#hide_show_image')[0].src = DATASET_REGISTER.visibilityOff;
	}
}

function prepareRegister() {
	// events
	$('#first_name_input').on('keydown', onInputEnter);
	$('#first_name_input').on('focusin', { image: '#customer_image' }, onInputFocusIn);
	$('#first_name_input').on('focusout', { image: '#customer_image' }, onInputFocusOut);

	$('#last_name_input').on('keydown', onInputEnter);
	$('#last_name_input').on('focusin', { image: '#customer_image' }, onInputFocusIn);
	$('#last_name_input').on('focusout', { image: '#customer_image' }, onInputFocusOut);

	$('#company_input').on('keydown', onInputEnter);
	$('#company_input').on('focusin', { image: '#customer_image' }, onInputFocusIn);
	$('#company_input').on('focusout', { image: '#customer_image' }, onInputFocusOut);

	$('#email_input').on('keydown', onInputEnter);
	$('#email_input').on('focusin', { image: '#email_image' }, onInputFocusIn);
	$('#email_input').on('focusout', { image: '#email_image' }, onInputFocusOut);

	$('#password_input').on('keydown', onInputEnter);
	$('#password_input').on('focusin', { image: '#password_image' }, onInputFocusIn);
	$('#password_input').on('focusout', { image: '#password_image' }, onInputFocusOut);

	$('#country_input').on('keydown', onInputEnter);
	$('#country_input').on('focusin', { image: '#location_image' }, onInputFocusIn);
	$('#country_input').on('focusout', { image: '#location_image' }, onInputFocusOut);

	$('#address_input').on('keydown', onInputEnter);
	$('#address_input').on('focusin', { image: '#location_image' }, onInputFocusIn);
	$('#address_input').on('focusout', { image: '#location_image' }, onInputFocusOut);

	$('#phone_input').on('keydown', onInputEnter);
	$('#phone_input').on('focusin', { image: '#phone_image' }, onInputFocusIn);
	$('#phone_input').on('focusout', { image: '#phone_image' }, onInputFocusOut);

	// enable or disable button
	checkRegister();
}

function checkRegister() {
	let firstNameValue = $('#first_name_input')[0].value;
	let lastNameValue = $('#last_name_input')[0].value;
	let emailValue = $('#email_input')[0].value;
	let passwordValue = $('#password_input')[0].value;
	let countryValue = $('#country_input')[0].value;
	let addressValue = $('#address_input')[0].value;

	if (firstNameValue != '' &&
		lastNameValue != '' &&
		emailValue != '' &&
		passwordValue != '' &&
		countryValue != '' &&
		addressValue != '') {
		enableButton('#register_button_div');
	} else {
		disableButton('#register_button_div');
	}

	// hide failed text if it is shown
	deactivateElement('#failed_div');
}

function register() {
	// disable events
	disableEvents('#register_button_div');

	// get values
	let firstNameValue = $('#first_name_input')[0].value;
	let lastNameValue = $('#last_name_input')[0].value;
	let companyValue = $('#company_input')[0].value;
	let emailValue = $('#email_input')[0].value;
	let passwordValue = $('#password_input')[0].value;
	let countryValue = $('#country_input')[0].value;
	let addressValue = $('#address_input')[0].value;
	let phoneValue = $('#phone_input')[0].value;

	fetch(DATASET_REGISTER.registerAccountUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'first_name': firstNameValue,
			'last_name': lastNameValue,
			'company': companyValue,
			'email': emailValue,
			'password': passwordValue,
			'country': countryValue,
			'address': addressValue,
			'phone': phoneValue
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			$('#register_button_text')[0].innerText = 'DONE!';
			approvalPopup(redirect=true);
		} else if (data.response == 'failed_email_taken') {
			checkRegister();

			// show failed text
			$('#failed_text')[0].innerText = 'Registration failed. Email already in use!';
			activateElement('#failed_div');
		} else {
			checkRegister();

			// show failed text
			$('#failed_text')[0].innerText = 'Registration failed. Please try again!';
			activateElement('#failed_div');
		}
	});
}