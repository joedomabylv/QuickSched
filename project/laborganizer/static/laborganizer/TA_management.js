//filter for TA management
function filterTA() {
   // Declare variables
   var input, id, button, buttonName, found, indexOfFound;
   input = document.getElementById("tafilter").value.toUpperCase();
   id = document.getElementById("accordionTA");
   talist = document.getElementsByClassName("accordion-item");
   //loop each row in table
   for (i = 0; i < talist.length; i++) {
     button = talist[i].getElementsByTagName("button")[0];
     buttonName = button.getElementsByTagName("div")[0];
     found = false;
     //loop each col in row
     indexOfFound = buttonName.textContent.toUpperCase().indexOf(input);
     if(indexOfFound != -1){
       //hightlight founded text
       //css class "highlight"
       let tempStr = buttonName.textContent.substring(indexOfFound, indexOfFound + input.length);
       buttonName.innerHTML = buttonName.textContent.replace(tempStr, "<span class='highlight'>" + tempStr + "</span>")
       found = true;
     }else{
       //refresh highlight
       buttonName.innerHTML = buttonName.textContent.replace("<span class='highlight'>", "")
       buttonName.innerHTML = buttonName.textContent.replace("</span>", "")
     }
     //if input founded in the row, display this row
     if (found) {
       talist[i].style.display = "";
     } else {
       talist[i].style.display = "none";
     }
   }
 } 