
var dateInput = {
  init: function () {
    var date_input = document.getElementById("id_req_date");
    var date_button = document.getElementById("id_SetDate");

    date_input.onchange = function () {
      date_button.click();

    }
  }
}

var processChoices = {
  init: function () {
    var selectedUser = document.getElementById("id_selectedUser");

    selectedUser.onchange = function () {
      //alert( selectedUser.find("option:selected").text());
      document.getElementById("id_SetUser").click();
    };

    var navSave = document.getElementById("id_NavSave");
    var allSave = document.getElementById("id_AllSave");

    // if javascript is working enable the navigation bar save button and hide the form button
    navSave.style.display = "initial";
    allSave.style.display = "none";

    // if the navigation button is clicked fire the form button
    navSave.onclick = function (event) {
      event.preventDefault();
      //alert( allSave );
      allSave.click();
    };

  }
}
