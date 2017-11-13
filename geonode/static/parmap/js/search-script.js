function searchLayerLandCover(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/layer-land-cover-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}

function searchLayerVulnerabilityAssessment(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/layer-vulnerability-assessment-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}

function searchMapsLandCover(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/maps-land-cover-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}

function searchMapsVulnerabilityAssessment(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/maps-vulnerability-assessment-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}

function searchSpectralLibrary(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/spectral-library-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}

function searchDocument(url) {
	$.ajax({
		type: "POST",
		url: url + "website/ajax/document-search.php",
		data: {},
		success: function(r) {
			$(".rightPanel").html(r);
			return false;
		},
		dataType: "html"
	});
}
