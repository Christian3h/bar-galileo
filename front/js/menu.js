const menu = document.getElementById('menu-movil');
const header = document.querySelector('header');
const nav = document.querySelector('.barra-navegacion');
const navList = document.querySelector('.barra-navegacion ul');
const button = document.querySelector('header button');
const buttonCerrar = document.getElementById('cerrar-menu');
const enlaces = document.querySelectorAll('.barra-navegacion ul li a'); // Selecciona todos los enlaces

// Función para abrir el menú
menu.addEventListener('click', () => {
    header.style.cssText = "flex-direction: column; height: 100svh;";
    nav.style.cssText = "display: flex; height: 80dvh; width: 100%; align-items: center; justify-content: center; text-align: center;";
    navList.style.cssText = "display: flex; flex-direction: column; gap: 40px;";
    button.style.display = "none";
    buttonCerrar.style.display = "block"; 
    menu.style.display = "none"; 
});

// Función para cerrar el menú
function cerrarMenu() {
    header.style.cssText = "";
    nav.style.cssText = "";
    navList.style.cssText = "";
    button.style.display = "";
    buttonCerrar.style.display = "none"; 
    menu.style.display = "flex"; 
}

// Cierra el menú al hacer clic en el botón de cerrar
buttonCerrar.addEventListener('click', cerrarMenu);

// Cierra el menú al hacer clic en cualquier enlace dentro de la barra de navegación
enlaces.forEach(enlace => {
    enlace.addEventListener('click', cerrarMenu);
});


window.addEventListener("scroll", function() {
    const header = document.querySelector("header");

    if (window.scrollY > 50) {
        header.classList.add("scrolled"); // Agrega la clase cuando se baja
    } else {
        header.classList.remove("scrolled"); // La quita cuando vuelve arriba
    }
});
