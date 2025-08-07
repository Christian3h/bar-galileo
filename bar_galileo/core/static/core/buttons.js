// Hace que todos los botones muestren un mensaje al hacer clic

// Para botones principales
document.querySelectorAll('.btn-green').forEach(btn => {
  btn.addEventListener('click', function() {
    alert('¡Botón funcionando!');
  });
});

// Para botones de carrusel (prev/next)
document.querySelectorAll('.carousel-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    alert('¡Botón de carrusel funcionando!');
  });
});
