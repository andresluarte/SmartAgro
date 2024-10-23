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
document.addEventListener('click', function(event) {
    var sidenav = document.getElementById('mySidenav');
    var menuButton = document.getElementById('menuButton');

    // Si el clic no es en el sidenav o en el botón, cerramos el sidenav
    if (!sidenav.contains(event.target) && !menuButton.contains(event.target)) {
        sidenav.style.width = "0";
    }
});
