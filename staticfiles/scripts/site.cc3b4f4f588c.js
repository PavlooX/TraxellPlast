function openPage(url) {
	document.location.href = url;
}

function newPage(url) {
	window.open(url, '_blank');
}

function formattedValue(value) {
	// if value has decimal part return number with 2 decimals (.00), else return whole number
	if (Number.isInteger(value)) {
		return value.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})
	} else {
		return value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})
	}
}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
const csrftoken = getCookie('csrftoken');

//hide all tabs first
$('.tab-content').hide();
//show the first tab content
$('#tab-orders').show();

$('#select_tab').change(function() {
	dropdown = $('#select_tab').val();
	//first hide all tabs again when a new option is selected
	$('.tab-content').hide();
	//then show the tab content of whatever option value was selected
	$('#' + "tab-" + dropdown).show();
});


// navbar

// listen to screen width changes
window.matchMedia('(max-width: 1199px)').addEventListener('change', function(e) {
	if (e.matches) {
		hideNavbarCollapse();
	} else {
		showNavbarCollapse();
	}
});

function showNavbarCollapse() {
	// show collapse
	if (!$('#navbar_pages_div').hasClass('show')) {
		$('#navbar_pages_div').addClass('show');
	}

	// set close image without animation
	$('#navbar_menu_div').addClass('no-transition');
	activateElement('#navbar_menu_div');
	$('#navbar_menu_div')[0].offsetHeight;
	$('#navbar_menu_div').removeClass('no-transition');
}

function hideNavbarCollapse() {
	// hide collapse
	if ($('#navbar_pages_div').hasClass('show')) {
		$('#navbar_pages_div').removeClass('show');
	}

	// set menu image without animation
	$('#navbar_menu_div').addClass('no-transition');
	deactivateElement('#navbar_menu_div');
	$('#navbar_menu_div')[0].offsetHeight;
	$('#navbar_menu_div').removeClass('no-transition');
}

function toggleNavbarMenu() {
	// animate collapse & menu images
	if (!$('#navbar_menu_div').hasClass('active')) {
		$('#navbar_menu_div').addClass('active');
		$('#navbar_pages_div').collapse('show');
	} else {
		$('#navbar_menu_div').removeClass('active');
		$('#navbar_pages_div').collapse('hide');
	}
}

// toggle collapse
function toggleContent(id) {
	arrow = '#arrow_image_' + id;
	content = '#content_' + id;

	if (!$(arrow).hasClass('active')) {
		$(arrow).addClass('active');
		$(content).collapse('show');
	} else {
		$(arrow).removeClass('active');
		$(content).collapse('hide');
	}
}

// enable button
function enableButton(el) {
	$(el)[0].style.pointerEvents = 'all';
	if ($(el).hasClass('disabled')) {
		$(el).removeClass('disabled');
	}
}

// disable button
function disableButton(el) {
	$(el)[0].style.pointerEvents = 'none';
	if (!$(el).hasClass('disabled')) {
		$(el).addClass('disabled');
	}
}

// activate element
function activateElement(el) {
	if (!$(el).hasClass('active')) {
		$(el).addClass('active');
	}
}

// deactivate element
function deactivateElement(el) {
	if ($(el).hasClass('active')) {
		$(el).removeClass('active');
	}
}

// activate error
function activateError(el) {
	if (!$(el).hasClass('error')) {
		$(el).addClass('error');
	}
}

// deactivate error
function deactivateError(el) {
	if ($(el).hasClass('error')) {
		$(el).removeClass('error');
	}
}

// disable events
function disableEvents(el) {
	$(el)[0].style.pointerEvents = 'none';
}

// on input enter - disable submit & unfocus
function onInputEnter(e) {
	if (e.keyCode == 13) {
		e.preventDefault();
		$(e.currentTarget).blur();
		return false;
	}
}

// on input focus in - zoom in image
function onInputFocusIn(e) {
	if (!$(e.data.image).hasClass('focused')) {
		$(e.data.image).addClass('focused');
	}
}

// on input focus out - zoom out image
function onInputFocusOut(e) {
	if ($(e.data.image).hasClass('focused')) {
		$(e.data.image).removeClass('focused');
	}
}