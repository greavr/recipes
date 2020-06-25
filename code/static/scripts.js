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

function drawgrid(data, title) {
   // create a tag (word) cloud chart
    var chart = anychart.tagCloud(data);
    // set a chart title
    chart.title(title)
    // set an array of angles at which the words will be laid out
    chart.angles([0])
    // enable a color range
    chart.colorRange(true);
    // set the color range length
    chart.colorRange().length('80%');
  // display the word cloud chart
    chart.container("container");
    chart.draw();
};