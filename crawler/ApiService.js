function isInteger(num) {
  return (num ^ 0) === num;
}

function initApiService(restUrl){
  apiservice={};
  apiservice.AjaxJson = new ApiService(restUrl);
}
function ApiService(url){

    this.serviceURL = (url == null) ? "/jsp/rest.jsp" : url;
  
  }

ApiService.prototype.executeQuery = function(jsonData, isNormalHtml){
  var self = apiservice.AjaxJson;
  var objJson = new Object();
  objJson.params = JSON.stringify(jsonData);
  var rt = $.ajax({
    url: self.serviceURL,
    type: 'POST',
    async: false,
    dataType:'json',
    data: objJson,
    error: function(data){
      console.log("error",data);
    }
  }).responseJSON;

  return isNormalHtml ? rt : ((rt && !isInteger(rt) && rt.length > 0) ? JSON.parse(escapeHTML(JSON.stringify(rt))) : rt);
}
function escapeHTML(string){
  var pre = document.createElement('pre');
  var text = document.createTextNode(string);
  pre.appendChild(text);
  return pre.innerHTML.replace(/&amp;/g,'&');
}

ApiService.prototype.executeQueryAsync = function(jsonData, callbackFunction, callbackOnError) {
	var self = apiservice.AjaxJson;
	var objJson = new Object();
	objJson.params = JSON.stringify(jsonData);
	$.ajax({
		url: self.serviceURL,
		type: 'POST',
		async: true,
		dataType: 'json',
		data: objJson,
		error: function(error) {
      console.log("error", error);
      callbackOnError(error);
		},
		success: function(data) {
			callbackFunction(data); 
		}
	});
}

ApiService.prototype.executeQueryAsync2 = function(jsonData, callbackFunction){
	var self = apiservice.AjaxJson;
	var objJson = new Object();
	objJson.params = JSON.stringify(jsonData);
	var rt = $.ajax({
		url: self.serviceURL,
		type: 'POST',
		async: true,
		dataType: 'json',
		data: objJson,
		error: function(data){
			console.log("error", data);
		},
		success: function(data) {
			callbackFunction(data); 
		}
	}).responseJSON;
	return true ? rt : ((rt && !Number.isInteger(rt) && rt.length > 0) ? JSON.parse(escapeHTML(JSON.stringify(rt))) : rt);
}
