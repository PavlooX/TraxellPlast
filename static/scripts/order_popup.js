const DATASET_ORDER = document.currentScript.dataset;
let order, orderStatusChoices = [];

// datepickers
const datepickerInit = {
	uiLibrary: 'bootstrap4',
	showRightIcon: false,
	keyboardNavigation: true,
	format: 'yyyy-mm-dd'
};
$('#popup_in_process_datepicker').datepicker(datepickerInit);
$('#popup_shipped_datepicker').datepicker(datepickerInit);

function orderPopup(id) {
	fetch(DATASET_ORDER.orderPopupUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'id': id
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			order = data.order;
			orderStatusChoices = data.order_status_choices;
			openPopup();
		}
	})
}

function openPopup() {
	// setup popup
	setup();

	// show popup
	$('#popup').modal('show');
}

function setup() {
	// name
	$('#popup_name_text')[0].innerText = `ORDER #${order.id}`;

	// order status
	for (let i = 0; i < orderStatusChoices.length; i++) {
		let newOption = new Option(orderStatusChoices[i][1], orderStatusChoices[i][0]);
		$('#popup_order_status_select')[0].add(newOption);
	}
	$('#popup_order_status_select')[0].value = order.order_status;
	$('#popup_order_status_select').on('keydown', onInputEnter);
	$('#popup_order_status_select').on('focusin', { image: '#popup_status_image' }, onInputFocusIn);
	$('#popup_order_status_select').on('focusout', { image: '#popup_status_image' }, onInputFocusOut);

	// in process date
	$('#popup_in_process_datepicker')[0].value = order.in_process_date;
	$('#popup_in_process_datepicker').on('keydown', onInputEnter);
	$('#popup_in_process_datepicker').on('focusin', { image: '#popup_in_process_image' }, onInputFocusIn);
	$('#popup_in_process_datepicker').on('focusout', { image: '#popup_in_process_image' }, onInputFocusOut);

	// shipped date
	$('#popup_shipped_datepicker')[0].value = order.shipped_date;
	$('#popup_shipped_datepicker').on('keydown', onInputEnter);
	$('#popup_shipped_datepicker').on('focusin', { image: '#popup_shipped_image' }, onInputFocusIn);
	$('#popup_shipped_datepicker').on('focusout', { image: '#popup_shipped_image' }, onInputFocusOut);

	// button
	$('#popup_button_text')[0].innerText = 'SAVE';
	enableButton('#popup_button_div');
}

function isValidDate(dateString) {
	let regEx = /^\d{4}-\d{2}-\d{2}$/;
	if (!dateString.match(regEx)) return false;  // invalid format
	let d = new Date(dateString);
	let dNum = d.getTime();
	if (!dNum && dNum !== 0) return false; // NaN value, invalid date
	return d.toISOString().slice(0, 10) === dateString;
}

function onDateChange(el) {
	let dateString = $(el)[0].value;
	if (!isValidDate(dateString)) {
		$(el)[0].value = '';
	}
}

function orderSave() {
	// disable events
	disableEvents('#popup_button_div');

	// get values
	let orderStatusValue = $('#popup_order_status_select')[0].value;
	let inProcessValue = $('#popup_in_process_datepicker')[0].value;
	let shippedValue = $('#popup_shipped_datepicker')[0].value;

	fetch(DATASET_ORDER.orderSaveUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'id': order.id,
			'order_status': orderStatusValue,
			'in_process_date': inProcessValue,
			'shipped_date': shippedValue
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			$('#popup_button_text')[0].innerText = 'SAVED!';

			setTimeout(function() {
				closePopup();
			}, 400);

			location.reload();
			window.scrollTo(0, 0);
		} else {
			// error
			$('#popup_button_text')[0].innerText = 'Something went wrong, please try again!';
			activateError('#popup_button_div');
		}
	})
}

function closePopup() {
	$('#popup').modal('hide');
}

$('#popup').on('hidden.bs.modal', function() {
	// reset values
	order, orderStatusChoices = [];

	// name 
	$('#popup_name_text')[0].innerText = '';

	// order status
	$('#popup_order_status_select').empty();
	$('#popup_order_status_select').off('keydown');
	$('#popup_order_status_select').off('focusin');
	$('#popup_order_status_select').off('focusout');

	// in process date
	$('#popup_in_process_datepicker')[0].value = '';
	$('#popup_in_process_datepicker').off('keydown');
	$('#popup_in_process_datepicker').off('focusin');
	$('#popup_in_process_datepicker').off('focusout');

	// shipped date
	$('#popup_shipped_datepicker')[0].value = '';
	$('#popup_shipped_datepicker').off('keydown');
	$('#popup_shipped_datepicker').off('focusin');
	$('#popup_shipped_datepicker').off('focusout');

	// button
	$('#popup_button_text')[0].innerText = '';
	deactivateError('#popup_button_div');
	disableButton('#popup_button_div');
});