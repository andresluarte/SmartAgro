function toggleNav() {
    var sidenav = document.getElementById("mySidenav");
    var menuButton = document.getElementById("menuButton");

    // Si el sidenav tiene width 0, lo abrimos
    if (sidenav.style.width === "0px" || sidenav.style.width === "") {
        sidenav.style.width = "250px";
    } else {
        // Si no, lo cerramos
        sidenav.style.width = "0";
    }
}

// Evitamos que el clic en cualquier parte de la página abra el sidenav

