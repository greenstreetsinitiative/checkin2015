/* main.js */

/************************************************
	Become a Retail Partner
************************************************/

/*
 * 	retailPartnerForm
 *	Object that collects/stores all data from the
 *	join retail partner form
 */
var retailPartnerForm = function() {
	this.contact_name = $("#contactname").val();
	this.contact_email = $("#contactemail").val();
	this.contact_phone = $("#contactphone").val();
	this.name = $("#businessname").val();
	this.address = $("#businessaddress").val();
	this.phone = $("#businessphone").val();
	this.website = $("#businesswebsite").val();
	this.offer = $("#businessoffer").val();
}

/*
 *	validate
 *	Attempts to validate data from the form.
 *	This is done mostly by making sure that the data is there
 *	in combination with a few regexes (for email and phone)
 *
 *	Return: True is the data appears to be good, false otherwise
 *	Other: 	Alerts user if the data seems to have some issues
 */
retailPartnerForm.prototype.validate = function(){
	var valid = true;
	var errmsg = ""

	if(!(this.contact_name && this.contact_phone && this.contact_email)){
		var valid = false;
		errmsg += "Information is missing from the contact section.\n";
	}

	if(!(this.name && this.address && this.address)) {
		var valid = false;
		errmsg += "Information is missing from the business section of the form.\n";
	}

	// Reject names that have numbers or certain special characters in them
	if(/[0-9]|[~!@#$%\^&*()_|+=?;:",.<>\{\}\[\]\\\/]+/g.test(this.contact_name)) {
		errmsg += "Please check the contact name.\n"
		valid = false
	}

	// Checks validity of contact email (not full rfc spec)
	if(!(/\S+@\S+\.\S+/.test(this.contact_email) && this.contact_email.length <= 254)) {
		errmsg += "Please check the contact email.\n";
		valid = false;
	}

	// Checks phone number
	if(!(/(?:\()?\d{3}(?:-|\s|\.|\)\s|\))?\d{3}(?:-|\.|\s)?\d{4}/g.test(this.contact_phone))) {
		errmsg += "Please check the phone number you wrote under the contact information.\n";
		valid = false;
	}

	// Can't validate company name
	// Address is validated server side due to geocoding
	// Can't validate offer
	// Can't validate url

	// Checks phone number
	if(!(/(?:\()?\d{3}(?:-|\s|\.|\)\s|\))?\d{3}(?:-|\.|\s)?\d{4}/g.test(this.phone))){
		errmsg += "Please check the phone number you wrote under the contact information.\n";
		valid = false;
	}

	if(errmsg){
		alert(errmsg);
	}
	return valid;
}

/*
 *	submit
 *	Submits form to server
 *	Should do something if submission fails,
 *	however it takes quite a while to get a
 *	response from the server
 */
retailPartnerForm.prototype.submit = function(){
	$('#jrp-submit-button').prop('disabled', true); // Disable button so people can't press submit several times while waiting

	// Deal with csrf
	var csrftoken = $.cookie('csrftoken');
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

	alert("Your application was submitted. We'll be in touch!");
	$('#jrp-submit-button').prop('disabled', false);
	$('#jrp-close').click(); //close modal

	// Submit the data
	$.post('',{'formJSON': JSON.stringify(this)}, function(data){
		if(data['success']){/* Something */}
		else {/* Something else */}
	});
}

/************************************************
	Coordinate Distance Functions
************************************************/

/*
 *	haversin
 * 		Applies the haversin on a given angle.
 *		The haversin is defined as:
 * 			harversin(x) = 1-(sin(x/2))^2
 *		This is equivalent to 1-cos(x)/2
 *		which is faster, but could possibly lead to floating point rounding from what I've read
 *
 *		Input 'theta' is an angle in degrees (use 'radian' function to convert from radian to degrees).
 */
function haversin(theta) {
	//return Math.sin(theta/2.0)*Math.sin(theta/2.0);
	return (1-Math.cos(theta))/2.0;
};

/*
 *	radian
 *		Converts angle from radians into degrees
 * 		Input: Angle in radians
 *		Output: Angle in degrees
 */
function radian(angle) {
	return angle * ( Math.PI / 180.0 );
};

/*
 *	CoordinateDistance
 *		Calculates the distance between two sets of coordinates (in kilometers) using the Haversine formula
 *		Inputs: Latitude and longitude of the two points
 *		Output: Distance between coordinates in kilometers
 *
 *	More info: http://en.wikipedia.org/wiki/Haversine_formula
 */
function coordinateDistance(latitude1, longitude1, latitude2, longitude2) {

	var h = haversin(radian(latitude2 - latitude1)) + Math.cos(radian(latitude2))*Math.cos(radian(latitude1))*haversin(radian(longitude2 - longitude1));

	//h needs to be less than 1 (possible floating point error); it's mentioned in the wikipedia article
	if(h > 1.0) {
		h = 1.0;
	}

	// distance = 2 * (earth radius) * arcsin ( sqrt ( h ) )
	// 3963.191 = earth's radius in miles
	return 2.0 * 3963.191 * Math.asin(Math.sqrt(h));
};

/************************************************
	Retail Partner Data Object
************************************************/

/*
 * 	retailPartnerData
 *		Object used to store all the data about retail partners
 *		in addition to the map, a boolean that determines if
 *		the user is on a mobile device, list of cities and cateogires.
 */
var retailPartnerData = function(data, isMobile, isTablet){
	var retailPartners = data.concat([]);

	// Create map
	if(!isMobile){
		var map = new L.map('map', {
				layers: MQ.mapLayer(),
				center: [42.3581, -71.0636],
				zoom: 11
		});
	}

	// Contains custom markers
	if(!isMobile){
		var category = {
			"Food and Drink": L.AwesomeMarkers.icon({
				icon: 'cutlery',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'green'
				}),
			"Clothing and Equipment": L.AwesomeMarkers.icon({
				icon: 'tags',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'blue'
			}),
			"Mind and Body": L.AwesomeMarkers.icon({
				icon: 'eye',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'orange'
			}),
			"Art": L.AwesomeMarkers.icon({
				icon: 'paint-brush',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'purple'
			}),
			"Bikes": L.AwesomeMarkers.icon({
				icon: 'bicycle',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'red'
			}),
			"Office": L.AwesomeMarkers.icon({
				icon: 'book',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'darkred'
			}),
			"Gifts": L.AwesomeMarkers.icon({
				icon: 'gift',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'darkgreen'
			}),
			"Unused": L.AwesomeMarkers.icon({
				icon: 'shopping-cart',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'darkpuple'
			}),
			"Other": L.AwesomeMarkers.icon({
				icon: 'certificate',
				iconColor: 'white',
				prefix: 'fa',
				markerColor: 'cadetblue'
			})
		};
	}

	// Sort sponsors alphabetically
	retailPartners.sort(function(a, b){
		if(a.name < b.name) {
			return -1;
		}
		if(a.name > b.name) {
			return 1;
		}
		return 0;
	});

	// Add a marker for each partner
	for(var i in retailPartners) {
		if(!isMobile){
			if(retailPartners[i].category == 'None'){
				retailPartners[i].category = 'Other';
			}
			retailPartners[i].popup = '<b>'+retailPartners[i].name+'</b><br>'+retailPartners[i].address+'<br>'+retailPartners[i].offer
			retailPartners[i].marker = new L.marker([retailPartners[i].latitude, retailPartners[i].longitude],
													{icon:category[retailPartners[i].category], riseOnHover:true, title:retailPartners[i].name})
			retailPartners[i].marker.addTo(map)
									.bindPopup(retailPartners[i].popup);
		}
		retailPartners[i].visible = true;
	};

	// Get cities and categories from data
	var cities = [], categories = [];
	for(var i = 0; i < retailPartners.length; i++) {
		cities[cities.length] = retailPartners[i].city;
		categories[categories.length] = retailPartners[i].category;
	}

	cities = cities.filter( function( item, index, inputArray ) { // Filters out duplicates & sorts alphabetically
		   return inputArray.indexOf(item) == index;
	}).sort();

	categories = categories.filter( function( item, index, inputArray ) { // Filters out duplicates & sorts alphabetically
		   return inputArray.indexOf(item) == index;
	}).sort();

	this.isMobile = isMobile;
	this.isTablet = isTablet;
	this.retailPartners = retailPartners;
	this.map = map;
	this.cities = cities;
	this.categories = categories;
	this.you = false; // storage of marker denoting user
	this.filters = {
		city : "All",
		category : "All",
		name : ""
	}
};

/************************************************
	Filtering Functions
************************************************/

/*
 * 	filterName
 *	Filters out the list of retail partners by a user-inputted string
 */
retailPartnerData.prototype.filterName = function() {
	// Get data from the searchbox
	var filterString = this.filters.name;

	// only do stuff if string is not empty
	if(filterString !== "") {
		// Make filterString lowercase to get around different formating
		filterString = filterString.toLowerCase();

		// temporary array to store results
		var tempArray = [];

		// Go through sponsors of this array
		for (var i in this.retailPartners){

			// Get the name of the current entry in this array
			// Make it lowercase to get around differences in formating
			// Then check to see if the user inputted string shows up
			var foundString = (this.retailPartners[i].name.toLowerCase()).indexOf(filterString);
			var foundStringSpace = (this.retailPartners[i].name.toLowerCase()).indexOf(" "+filterString);

			// Check we found the string
			// If true, add the retail partner to the temporary array
			if (!(foundString === 0 || foundStringSpace != -1)) {
				this.retailPartners[i].visible = false;
			}
		}
	}
};

// Filters by city
retailPartnerData.prototype.filterCity = function(){
	var filter = this.filters.city;

	if(filter !== "All") {
		for(var i in this.retailPartners){
			if(this.retailPartners[i].city !== filter){
				this.retailPartners[i].visible = false;
			}
		}
	}
}

// Filters by category
retailPartnerData.prototype.filterCategory = function(){
	var filter = this.filters.category;

	if(filter !== "All") {
		for(var i in this.retailPartners){
			if(this.retailPartners[i].category !== filter){
				this.retailPartners[i].visible = false;
			}
		}
	}
}

/*
 *	filter
 * 	Resets and reapplies all filters.
 *
 *	The filters are reset and all filters are applied to simplify figuring
 *	out which filters have already been applied and how to un-do them.
 *
 * 	The filter functions only change the visible property (a boolean)
 *	of the retail partners. The display function in turn only displays
 *	retail partners whose visible property is true.
 *
 */
retailPartnerData.prototype.filter = function() {
	for(var i in this.retailPartners){
		this.retailPartners[i].visible = true; // reset filters
	}

	this.filterCity();
	this.filterCategory();
	this.filterName();
}

/************************************************
	Sorting Functions
************************************************/

/*
 * 	sortAddress
 *	Sorts list of retail partners by distance to a user-inputted address
 *	The address is converted to latitude,longitude coordinates using the mapquest api
 *	After acquiring the coordinates, this function updates the distances, then displays the results
 */
retailPartnerData.prototype.sortAddress = function(){
	var address = prompt("Enter address:");
	if(address) {
		var latitude, longitude;
		var key = "Fmjtd%7Cluur2h68n9%2C7x%3Do5-9w2wdz";
		var mq_url = "http://open.mapquestapi.com/geocoding/v1/address?key="
					+ key
					+ "&inFormat=kvp&outFormat=json&location="
					+ address
					+ "&thumbMaps=false";

		var proxy = this;
		$.getJSON(mq_url, function(data) {
			if(data.results[0].locations[0].latLng.lat !== null){
				latitude = data.results[0].locations[0].latLng.lat;
				longitude = data.results[0].locations[0].latLng.lng;

				for(var i in proxy.retailPartners){
					proxy.retailPartners[i].distance = coordinateDistance(proxy.retailPartners[i].latitude, proxy.retailPartners[i].longitude, latitude, longitude);
				}

				proxy.retailPartners.sort(function(a,b){
					return a.distance - b.distance;
				});

				if(!proxy.isMobile){
					proxy.addUserMarker(latitude, longitude);
				}

				proxy.display();
			}
			else {
				$(".user-address").empty();
				alert("Sorry, but we couldn't find that address. Please try again!");
			}
		});
	}
	else {
		$(".sort").val('alphabet');
	}
}

/*
 * 	sortDistance
 *	Sorts retail partners by distance to user
 *	User location is acquired using geolocation api (html5)
 */
retailPartnerData.prototype.sortDistance = function() {
	var proxy = this;
	if('geolocation' in navigator) {
		navigator.geolocation.getCurrentPosition(function(position){
			var latitude = position.coords.latitude;
			var longitude = position.coords.longitude;

			if(!proxy.isMobile){
				proxy.addUserMarker(latitude, longitude);
			}

			for(var i in proxy.retailPartners) {
				proxy.retailPartners[i].distance = coordinateDistance(proxy.retailPartners[i].latitude, proxy.retailPartners[i].longitude, latitude, longitude);
			}

			proxy.retailPartners.sort(function(a,b){
				return a.distance - b.distance;
			});

			proxy.display();
		});
	}
	else {
		alert("Sorry, but geolocation isn't supported by your browser. We can't figure out where you are right now.");
	}
}

/*
 * 	sortAlphabet
 *	Sorts retail partners alphabetically and displays the result
 *	(default sort option)
 */
retailPartnerData.prototype.sortAlphabet = function(){
	this.retailPartners.sort(function(a, b) {
		if(a.name < b.name) {
			return -1;
		}
		if(a.name > b.name) {
			return 1;
		}
		return 0;
	});

	this.display();
}

/*
 *	Determines what type of sorting the user select
 *	and calls appropriate function to sort retail partners
 */
retailPartnerData.prototype.sort = function(sortable){
	switch( sortable ) {
		case "alphabet":
			this.sortAlphabet();
			break;
		case "distance":
			this.sortDistance();
			break;
		case "address":
			this.sortAddress();
			break;
	}
}

/************************************************
	Retail Partner Helper Functions
************************************************/

/*
 *	clearMap
 *	Removes all markers from map
 */
retailPartnerData.prototype.clearMap = function(){
	for(var i in this.retailPartners){
		//this.retailPartners[i].marker.setOpacity(0);
		this.map.removeLayer(this.retailPartners[i].marker);
	}
}

/*
 * 	addUserMarker
 *	Adds user location to map as a marker
 */
retailPartnerData.prototype.addUserMarker = function(latitude, longitude){
	if(this.you){ // Remove previous marker denoting user location
		this.map.removeLayer(this.you);
	}

	var icon = L.AwesomeMarkers.icon({
		icon: 'star',
		iconColor: 'white',
		prefix: 'fa',
		markerColor: 'red'
	});

	this.you = new L.marker([latitude, longitude], {icon:icon, riseOnHover:true, title:"You are here!"}).addTo(this.map);

	this.map.panTo(new L.LatLng(latitude, longitude)); // Centers on user coordinates
}

/*
 * 	display
 *	Displays retail partners on the page (both list and map)
 *	Also enables the popups for when you hover over the partner in the list
 */
retailPartnerData.prototype.display = function() {
	$(".retail-partners-list").empty();
	if(!this.isMobile){
			this.clearMap();
	}
	var content = "";
	for(var i in this.retailPartners) {
		if(this.retailPartners[i].visible){
			if(!this.isMobile){
				this.retailPartners[i].marker.addTo(this.map).bindPopup(this.retailPartners[i].popup);
				//this.retailPartners[i].marker.setOpacity(1); // Make marker visible
			}

			content += "<li class=\"rp-object\" id=\"id_" + i + "\">"
			if(this.retailPartners[i].website === "") { // If the retail partner has a website, add an url to the name
				content += "<p class=\"rp-name\">" + this.retailPartners[i].name + "</p>";
			}
			else {
				content += "<a  href=\""+ this.retailPartners[i].website +"\" class=\"rp-name-url\">" + this.retailPartners[i].name + "</a>";
			}
			content += "<p class=\"rp-p\">"+this.retailPartners[i].address+"</p>"+"<p class=\"rp-p\">"+this.retailPartners[i].offer+"</p>"
			if(this.retailPartners[i].distance != Math.Infinity){	// If we've calculated the distance, show it.
				content += "<p class=\"rp-p\">"+this.retailPartners[i].distance.toFixed(2)+" miles</p>";
			}
			content += "</li>";
		}
	}
	$(".retail-partners-list").append(content);

	if(!this.isMobile){
		var proxy = this;
		$('.rp-object').mouseenter(function(){
			var i = parseInt($(this).attr('id').split("_").pop());
			proxy.retailPartners[i].marker.openPopup();
		});
		$('.rp-object').mouseleave(function(){
			var i = parseInt($(this).attr('id').split("_").pop());
			proxy.retailPartners[i].marker.closePopup();
		});
	}
};

/*
 * 	loadFilters
 *	Gets all the cities and categories from the list of retail partners
 *	and adds them to the page to be used as filters
 *	The retailPartnerData object should already hold all of this data
 */
retailPartnerData.prototype.loadFilters = function(){
	if( !(this.isTablet||this.isMobile) ) {
		// Load cities
		$(".city").empty();
		var content = "<option value=\"All\">All cities</option>";
		for(var i in this.cities){
			content += "<option value=\""+this.cities[i]+"\">"+this.cities[i]+"</option>";
		}
		$(".city").append(content);

		// Load categories
		$(".category").empty();
		var content = "<option value=\"All\">All Categories</option>";
		for(var i in this.categories){
			content += "<option value=\""+this.categories[i]+"\">"+this.categories[i]+"</option>";
		}
		$(".category").append(content);
	}
	else { // Tablet or Mobile
		// Load cities
		$(".city-modal-body").empty();
		var content = "<button type=\"button\" class=\"btn btn-default m-btn city-btn\" value=\"All\">All Cities</button>";
		for(var i in this.cities) {
			content += "<br><button type=\"button\" class=\"btn btn-default m-btn city-btn\" value=\""+this.cities[i]+"\">"+this.cities[i]+"</button>";
		}
		$(".city-modal-body").append(content);

		// Load categories
		$(".category-modal-body").empty();
		var content = "<button type=\"button\" class=\"btn btn-default m-btn category-btn\" value=\"All\">All Categories</button>";
		for(var i in this.categories){
			content += "<br><button type=\"button\" class=\"btn btn-default m-btn category-btn\" value=\""+this.categories[i]+"\">"+this.categories[i]+"</button>";
		}
		$(".category-modal-body").append(content);
	}
}

/************************************************
	Main
************************************************/
$(document).ready(function(){

	$('body').on('touchstart.dropdown', '.dropdown-menu', function(e){ e.stopPropagation(); });

	var isMobile = false, isTablet = false;
	if( /webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini|Android(?=.*Mobile)/i.test(navigator.userAgent) ) {
		isMobile = true;
		$('#rightbar').css("width", "100%");
		//$('body').css("padding-top", "0px;");
 	}
 	else if(/Android|iPad|Windows(?=.*Touch)/.test(navigator.userAgent)) {
 		isTablet = true;
 	}

	var data = new retailPartnerData(rpData, isMobile, isTablet); // rpData is defined in a separate script, contains all retail partner data
	data.loadFilters();
	data.display();

	// Regular city filter
	$('.city').change(function(){
		data.filters.city = $(this).val();
		data.filter();
		data.display();
	});

	// Mobile city sort
	$('.city-btn').click(function(){
		data.filters.city = $(this).val();
		$('#mobile-city-modal').modal('hide');
		data.filter();
		data.display();
	});

	// Regular category filter
	$('.category').change(function(){
		data.filters.category = $(this).val();
		data.filter();
		data.display();
	});

	// Mobile category
	$('.category-btn').click(function(){
		data.filters.category = $(this).val();
		data.filter();
		$('#mobile-category-modal').modal('hide');
		data.display();
	});

	// All name filters
	$("#searchbox").keyup(function(){
		data.filters.name = $("#searchbox").val();
		data.filter();
		data.display();
	});

	// Regular sort
	$('#sort').change(function() {
		data.filter();
		data.sort( $(".sort").val() ); // sort displays the results since it's async due to geocoding/geolocation
	});

	// Mobile sort
	$('.sort-button').click(function(){
		data.filter();
		$('#mobile-sort-modal').modal('hide');
		data.sort( $(this).val() );
	});

	// Application to join retail partners
	$("#jrp-submit-button").click(function(){
		var form = new retailPartnerForm();
		if(form.validate()){
			form.submit();
		}
	});
});
