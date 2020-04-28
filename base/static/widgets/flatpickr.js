$(document).ready(function() {
    config = {
	altInput: true,
	time_24hr: true,
	locale: "no",
    }

    $(".flatpickr.date").flatpickr({
	...config,
	dateFormat: "Y-m-d H:i",
    });

    $(".flatpickr.datetime").flatpickr({
	...config,
	enableTime: true,
	altFormat: "F j, Y H:i",
	dateFormat: "Y-m-d H:i",
    });

    $(".flatpickr.time").flatpickr({
	...config,
	altFormat: "H:i",
	dateFormat: "Y-m-d H:i",
	enableTime: true,
	noCalendar: true,
    });
});
