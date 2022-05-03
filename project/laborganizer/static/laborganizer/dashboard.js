var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="dropdown"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});
var popoverTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="popover"]')
);
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl);
});
//filter
function filterFuntion() {
  // Declare variables
  var input, table, rows, cols, found, colStr;
  input = document.getElementById("tablefilter").value.toUpperCase();
  table = document.getElementById("labTable");
  rows = table.getElementsByTagName("tr");
  //loop each row in table
  for (i = 0; i < rows.length; i++) {
    cols = rows[i].getElementsByTagName("td");
    found = false;
    //loop each col in row
    for (j = 0; j < cols.length - 1; j++) {
      if(j == 8){
        let temp = cols[j].getElementsByTagName("select")[0];
        colStr = temp.options[temp.selectedIndex];
      }else{
        colStr = cols[j];
      }
      indexOfFound = colStr.textContent.toUpperCase().indexOf(input);
      if(indexOfFound != -1){
        //hightlight founded text
        //css class "highlight"
        let tempStr = colStr.textContent.substring(indexOfFound, indexOfFound + input.length);
        colStr.innerHTML = colStr.textContent.replace(tempStr, "<span class='highlight'>" + tempStr + "</span>")
        found = true;
      }else{
        //refresh highlight
        colStr.innerHTML = colStr.textContent.replace("<span class='highlight'>", "")
        colStr.innerHTML = colStr.textContent.replace("</span>", "")
      }
    }
    //if input founded in the row, display this row
    if (found) {
      rows[i].style.display = "";
    } else {
      rows[i].style.display = "none";
    }
  }
}

//sorf function
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("labTable");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 0; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      if(n == -1){
        x = rows[i].getElementsByTagName("th")[0];
        y = rows[i + 1].getElementsByTagName("th")[0];
      }else{
        x = rows[i].getElementsByTagName("td")[n];
        y = rows[i + 1].getElementsByTagName("td")[n];
      }
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if( n == -1 || n == 9){
        sortX = parseInt(x.innerHTML);
        sortY = parseInt(y.innerHTML);
      }else if( n == 8){
        sortX = x.getElementsByTagName("option")[0].text;
        sortY = y.getElementsByTagName("option")[0].text;
      }else{
        sortX = x.innerHTML.toLowerCase();
        sortY = y.innerHTML.toLowerCase();
      }
      if (dir == "asc") {
        if (sortX > sortY) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (sortX < sortY) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been maed, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

window.onload = refreshAssignedLabs()

//Refresh assinged number of labs
function refreshAssignedLabs(){
  var table = document.getElementById("labTable");
  var rows = table.rows;
  for (i = 0; i < rows.length; i++) {
    let count = 0;
    let TA = rows[i].getElementsByTagName("td")[8].getElementsByTagName("option")[0].text;
    for(j = 0; j < rows.length; j++){
      let TA2 = rows[j].getElementsByTagName("td")[8].getElementsByTagName("option")[0].text;
      if(TA == TA2){
        count++;
      }
    }
    rows[i].getElementsByTagName("td")[9].innerHTML = count;
  }
}