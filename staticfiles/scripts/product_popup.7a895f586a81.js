const DATASET_PRODUCT = document.currentScript.dataset;
let product, item = [];

function productPopup(id, model) {
	fetch(DATASET_PRODUCT.productPopupUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'id': id,
			'model': model
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			product = data.product;
			openPopup('product');
		}
	});
}

function itemPopup(id, model) {
	fetch(DATASET_PRODUCT.itemPopupUrl, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'id': id,
			'model': model
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			item = data.item;
			product = item.product;
			openPopup('item');
		}
	});
}

function openPopup(type) {
	// setup popup
	setup(type);

	// show popup
	$('#popup').modal('show');
}

function setup(type) {
	// name
	$('#popup_name_text')[0].innerText = product.name;

	// model viewer
	let modelViewer = createModelViewer();
	$('#popup_left_div')[0].append(modelViewer);

	// materials
	for (let i = 0; i < product.materials.length; i++) {
		let newOption = new Option(product.materials[i].display, product.materials[i].name);
		$('#popup_material_select')[0].add(newOption);
	}
	$('#popup_material_select').on('keydown', onInputEnter);
	$('#popup_material_select').on('focusin', { image: '#popup_material_image' }, onInputFocusIn);
	$('#popup_material_select').on('focusout', { image: '#popup_material_image' }, onInputFocusOut);

	// colors
	for (let i = 0; i < product.colors.length; i++) {
		let newOption = new Option(product.colors[i].display, product.colors[i].name);
		$('#popup_color_select')[0].add(newOption);
	}
	$('#popup_color_select').on('keydown', onInputEnter);
	$('#popup_color_select').on('focusin', { image: '#popup_color_image' }, onInputFocusIn);
	$('#popup_color_select').on('focusout', { image: '#popup_color_image' }, onInputFocusOut);
	$('#popup_custom_color_input').on('keydown', onInputEnter);
	$('#popup_custom_color_input').on('focusin', { image: '#popup_color_image' }, onInputFocusIn);
	$('#popup_custom_color_input').on('focusout', { image: '#popup_color_image' }, onInputFocusOut);

	// amount
	$('#popup_amount_input')[0].min = product.amount_min;
	$('#popup_amount_input')[0].placeholder = `Enter amount (min ${product.amount_min})`;
	$('#popup_amount_input').on('keydown', onInputEnter);
	$('#popup_amount_input').on('focusin', { image: '#popup_amount_image' }, onInputFocusIn);
	$('#popup_amount_input').on('focusout', { image: '#popup_amount_image' }, onInputFocusOut);

	// button	
	if (type == 'product') {
		$('#popup_button_div').on('click', { type: 'cartAdd' }, sendPopup);
		$('#popup_button_text')[0].innerText = 'ADD TO CART';
	} else if (type == 'item') {
		$('#popup_button_div').on('click', { type: 'cartSave' }, sendPopup);
		$('#popup_button_text')[0].innerText = 'SAVE';
	}

	// existing values
	if (type == 'product') {
		resetTotalPrice();
	} else if (type == 'item') {
		// material
		$('#popup_material_select')[0].value = item.material.name;

		// color
		$('#popup_color_select')[0].value = item.color.name;
		if (item.color.name == 'custom') {
			// custom color
			$('#popup_custom_color_input')[0].value = item.custom_color;
			activateElement('#popup_custom_color_input');
		}

		// amount
		$('#popup_amount_input')[0].value = item.amount;

		updateTotalPrice();
	}
}

function createModelViewer() {
	let x = document.createElement('model-viewer');
	x.setAttribute('auto-rotate', '');
	x.setAttribute('camera-controls', '');
	x.setAttribute('data-js-focus-visible', '');
	x.setAttribute('interaction-prompt', 'none');
	x.setAttribute('min-camera-orbit', 'auto 0deg 520m');
	x.setAttribute('max-camera-orbit', 'auto 180deg auto');
	x.setAttribute('camera-orbit', '0deg 65deg 520m');
	x.setAttribute('src', product.model_url);
	x.setAttribute('id', 'popup_model_viewer');
	return x;
}

function resetTotalPrice() {
	// clear price
	$('#popup_total_price_1_text')[0].innerText = '-';
	$('#popup_total_price_2_text')[0].style.display = 'none';
	$('#popup_total_price_2_text')[0].innerText = '-';

	disableButton('#popup_button_div');
}

function updateTotalPrice() {
	// calculate total price
	let amountString = $('#popup_amount_input')[0].value;
	let amountValue = Number(amountString);

	let materialValue = $('#popup_material_select')[0].value;
	let material = product.materials.find(x => x.name == materialValue);

	let totalPrice = amountValue * material.price;

	$('#popup_total_price_1_text')[0].innerText = `${formattedValue(amountValue)} * ${material.price} \u20ac`;
	$('#popup_total_price_2_text')[0].innerText = `${formattedValue(totalPrice)} \u20ac`;
	$('#popup_total_price_2_text')[0].style.display = 'block';

	enableButton('#popup_button_div');
}

function allowSubmit() {
	// amount not set
	let amountString = $('#popup_amount_input')[0].value;
	if (amountString == '') {
		return false;
	}

	let materialValue = $('#popup_material_select')[0].value;
	let colorValue = $('#popup_color_select')[0].value;
	let amountValue = Number(amountString);

	// material set, color set, amount set and larger than min
	if (materialValue != '0' &&
		colorValue != '0' &&
		amountValue >= product.amount_min) {
		return true;
	} else {
		return false;
	}
}

function onMaterialChange() {
	if (allowSubmit() == true) {
		updateTotalPrice();
	} else {
		resetTotalPrice();
	}
}

function onColorChange() {
	let colorValue = $('#popup_color_select')[0].value;
	if (colorValue == 'custom') {
		activateElement('#popup_custom_color_input');
	} else {
		deactivateElement('#popup_custom_color_input');
	}

	if (allowSubmit() == true) {
		updateTotalPrice();
	} else {
		resetTotalPrice();
	}
}

function onAmountChange() {
	// if amount value is lower than min value, clear amount value
	let amountString = $('#popup_amount_input')[0].value;
	if (amountString != '') {
		let amountValue = Number(amountString);
		if (amountValue < product.amount_min) {
			$('#popup_amount_input')[0].value = '';
		}
	}

	if (allowSubmit() == true) {
		updateTotalPrice();
	} else {
		resetTotalPrice();
	}
}

function sendPopup(event) {
	// disable events
	disableEvents('#popup_button_div');

	// get values
	let materialValue = $('#popup_material_select')[0].value;
	let material = product.materials.find(x => x.name == materialValue);
	let colorValue = $('#popup_color_select')[0].value;
	let color = product.colors.find(x => x.name == colorValue);
	let customColorValue = $('#popup_custom_color_input')[0].value;
	let amountString = $('#popup_amount_input')[0].value;
	let amountValue = Number(amountString);
	let totalPrice = amountValue * material.price;

	let url, id, success_text;
	if (event.data.type == 'cartAdd') {
		url = DATASET_PRODUCT.cartAddUrl;
		id = product.id;
		success_text = 'ADDED!';
	} else if (event.data.type == 'cartSave') {
		url = DATASET_PRODUCT.cartSaveUrl;
		id = item.id;
		success_text = 'SAVED!';
	}

	fetch(url, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: JSON.stringify({
			'id': id,
			'model': product.model,
			'material': material,
			'color': color,
			'custom_color': customColorValue,
			'amount': amountValue,
			'total_price': totalPrice
		})
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			$('#popup_button_text')[0].innerText = success_text;

			setTimeout(function() {
				closePopup();
			}, 400);

			location.reload();
		} else {
			// error
			if (!$('#popup_button_div').hasClass('error')) {
				$('#popup_button_div').addClass('error');
			}
			$('#popup_button_text')[0].innerText = 'Something went wrong, please try again!';
		}
	});
}

function closePopup() {
	$('#popup').modal('hide');
}

$('#popup').on('hidden.bs.modal', function() {
	// reset values
	product, item = [];

	// name 
	$('#popup_name_text')[0].innerText = '';

	// model viewer
	$('#popup_left_div').empty();

	// materials
	$('#popup_material_select')[0].value = '0';
	$('#popup_material_select').find('option').not(':first').remove();
	$('#popup_material_select').off('keydown');
	$('#popup_material_select').off('focusin');
	$('#popup_material_select').off('focusout');

	// colors
	$('#popup_color_select')[0].value = '0';
	$('#popup_color_select').find('option').not(':first').remove();
	$('#popup_color_select').off('keydown');
	$('#popup_color_select').off('focusin');
	$('#popup_color_select').off('focusout');

	// custom color
	$('#popup_custom_color_input')[0].value = '#33C4A9';
	if ($('#popup_custom_color_input').hasClass('active')) {
		$('#popup_custom_color_input').removeClass('active');
	}
	$('#popup_custom_color_input').off('keydown');
	$('#popup_custom_color_input').off('focusin');
	$('#popup_custom_color_input').off('focusout');

	// amount
	$('#popup_amount_input')[0].value = '';
	$('#popup_amount_input')[0].placeholder = '';
	$('#popup_amount_input').off('keydown');
	$('#popup_amount_input').off('focusin');
	$('#popup_amount_input').off('focusout');

	// total price
	$('#popup_total_price_1_text')[0].innerText = '-';
	$('#popup_total_price_2_text')[0].style.display = 'none';
	$('#popup_total_price_2_text')[0].innerText = '-';

	// button
	$('#popup_button_text')[0].innerText = '';
	deactivateError('#popup_button_div');
	disableButton('#popup_button_div');
	$('#popup_button_div').off('click');
});