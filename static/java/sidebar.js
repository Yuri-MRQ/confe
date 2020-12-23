function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.getElementById("main").style.width = "84%";
    document.getElementById("form-box").style.margin = "0px 450px 0px";
  }
  
  function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
    document.getElementById("main").style.width = "100%";
    document.getElementById("form-box").style.margin = "0px 570px 0px";
  }