$(document).ready(function() {
	/*
	 * Change form fields based on activity type
	 */
	var $typeSelector = $("#id_activity_type");
	var $subForms = $(".sub-form")

	function updateCurrent(current) {
		$(".sub-forms").children().remove()

		$subForms.each(function() {
			if ($(this).data("name") == current) {
				$(this).appendTo(".sub-forms");
			}
		})
	}

	updateCurrent($typeSelector.val());

	$typeSelector.change(function() {
		updateCurrent($(this).val());
	});

	/*
	 * Show/hide internal description based on visibility
	 */
	function updateInternalDescription(visibility) {
		console.log("Trigger");
		var $internalDescription = $('#id_description_internal').parent().parent()
		var className = "description-hidden";

		if (visibility == "PUB") {
			console.log("Public")
			$internalDescription.removeClass(className);
		} else {
			console.log("Internal")
			$internalDescription.addClass(className);
		}
	}

	var $visibilitySelector = $('#id_visibility');

	updateInternalDescription($visibilitySelector.val());

	$('#id_visibility').change(function() {
		updateInternalDescription($(this).val());
	});
});
