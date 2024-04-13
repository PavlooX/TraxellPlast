const DATASET_ACCOUNT = document.currentScript.dataset;
$(document).ready(prepareAccount());

function prepareAccount() {
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
	checkSave();
}

function checkSave() {
	let firstNameValue = $('#first_name_input')[0].value;
	let lastNameValue = $('#last_name_input')[0].value;
	let emailValue = $('#email_input')[0].value;
	let countryValue = $('#country_input')[0].value;
	let addressValue = $('#address_input')[0].value;

	if (firstNameValue != '' &&
		lastNameValue != '' &&
		emailValue != '' &&
		countryValue != '' &&
		addressValue != '') {
		enableButton('#account_button_div');
	} else {
		disableButton('#account_button_div');
	}

	// hide failed text if it is shown
	deactivateElement('#failed_div');
}

function accountSave() {
	// disable events
	disableEvents('#account_button_div');

	// get values
	let firstNameValue = $('#first_name_input')[0].value;
	let lastNameValue = $('#last_name_input')[0].value;
	let companyValue = $('#company_input')[0].value;
	let emailValue = $('#email_input')[0].value;
	let countryValue = $('#country_input')[0].value;
	let addressValue = $('#address_input')[0].value;
	let phoneValue = $('#phone_input')[0].value;

	fetch(DATASET_ACCOUNT.accountSaveUrl, {
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
			'country': countryValue,
			'address': addressValue,
			'phone': phoneValue
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			$('#account_button_text')[0].innerText = 'SAVED!';
			openPage(DATASET_ACCOUNT.homeViewUrl);
		} else if (data.response == 'success_email_changed') {
			$('#account_button_text')[0].innerText = 'SAVED!';
			openPage(DATASET_ACCOUNT.logoutAccountUrl);
		} else if (data.response == 'failed_email_taken') {
			checkSave();

			// show failed text
			$('#failed_text')[0].innerText = 'Save failed. Entered email is already in use!';
			activateElement('#failed_div');
		} else {
			checkSave();

			// show failed text
			$('#failed_text')[0].innerText = 'Save failed. Please try again!';
			activateElement('#failed_div');
		}
	});
}