function toggleNav() {
    var sidenav = document.getElementById("mySidenav");
    if (sidenav.style.width === "0px" || sidenav.style.width === "") {
        sidenav.style.width = "250px"; // Abrir
    } else {
        sidenav.style.width = "0"; // Cerrar
    }
}

// Cerrar el sidenav si se hace clic fuera de él
document.addEventListener('click', function(event) {
    var sidenav = document.getElementById('mySidenav');
    var menuButton = document.getElementById('menuButton');
    if (!sidenav.contains(event.target) && !menuButton.contains(event.target)) {
        sidenav.style.width = "0"; // Cerrar
    }
});
