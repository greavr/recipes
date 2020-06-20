var NumCounter = 1;
var Counter = 1;


function toogleAccoridan(div){
  div.classList.toggle("active");
  var panel = div.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
}

function addInput(){
    Counter++;
    $('#IngredientsTable').append("<tr id='UnNumrow"+Counter+"'><td><input type='text' name='Ingredients[]'></td><td><button type='button' name='remove' onClick='deleteRow(this)'>X</button></td></tr>");
}

function addNumberedInput(){
    NumCounter++;
    $('#DirectionsTable').append("<tr id='Numrow"+NumCounter+"'><td><b>Step "+NumCounter+":</b> <textarea name='Directions[]'></textarea></td><td><button type='button' name='remove' onClick='deleteRow(this)');'>X</button></td></tr>");
}

function deleteRow(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
  }