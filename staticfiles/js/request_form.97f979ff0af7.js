function addrow() {
  // should get length !
  var num = document.getElementById("additional_enrollments").childElementCount;
  var node = document.createElement("DIV");
  node.setAttribute("id", "addEnroll-" + num);
  node.setAttribute("class", "row vertical-center");
  //node.appendChild(y);
  var id = "'additional_enrollments','addEnroll-" + num + "'";
  var name_user = "'additional_enrollments[" + num + "][user]'";
  var name_role = "'additional_enrollments[" + num + "][role]'";
  node.insertAdjacentHTML(
    "beforeend",
    "<label style='width: 45%;'> User (pennkey) <input name=" +
      name_user +
      " value='' class='form-control' type='text'> </label> <label> Role  <select id='choose' name=" +
      name_role +
      " > <option disabled selected>Please select</option> <option value='TA'>TA</option> <option value='DES'>Designer</option> <option value='LIB'>Librarian</option> </select> </label><a onClick=removeElement(" +
      id +
      "); style='padding-left:5px;'> Delete <i class='fas fa-times'></i></a>"
  );
  document.getElementById("additional_enrollments").appendChild(node);
}

function removeElement(parentDiv, childDiv) {
  if (childDiv == parentDiv) {
    alert("The parent div cannot be removed.");
  } else if (document.getElementById(childDiv)) {
    var child = document.getElementById(childDiv);
    var parent = document.getElementById(parentDiv);
    parent.removeChild(child);
  } else {
    alert("Child div has already been removed or does not exist.");
    return false;
  }
}
