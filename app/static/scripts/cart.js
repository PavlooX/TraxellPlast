const DATASET_CART = document.currentScript.dataset;

function cartDelete(id, model) {
	jsonData = JSON.stringify({
		'id': id,
		'model': model
	});
	sendCart('cartDelete', jsonData);	
}

function cartDeleteAll() {
	sendCart('cartDeleteAll');
}

function cartSubmit() {
	sendCart('cartSubmit');
}

function sendCart(event, jsonData=null) {
	if (event == 'cartDelete') {
		url = DATASET_CART.cartDeleteUrl;
	} else if (event == 'cartDeleteAll') {
		url = DATASET_CART.cartDeleteAllUrl;
	} else if (event == 'cartSubmit') {
		url = DATASET_CART.cartSubmitUrl;
	}

	fetch(url, {
		method: 'POST',
		headers: {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrftoken
		},
		body: jsonData
	})

	.then(response => response.json())

	.then(data => {
		if (data.response == 'success') {
			if (event == 'cartDelete' || event == 'cartDeleteAll') {
				location.reload();
			} else if (event == 'cartSubmit') {
				openPage(DATASET_CART.ordersViewUrl);
			}
		}
	});
}