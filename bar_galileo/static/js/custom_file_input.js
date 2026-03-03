document.addEventListener('DOMContentLoaded', function () {
  // Seleccionar todos los inputs de tipo file
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach(input => {
    // Crear un contenedor para el input personalizado
    const wrapper = document.createElement('div');
    wrapper.classList.add('custom-file-input');
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.border = '2px dashed var(--color-primary)';
    wrapper.style.borderRadius = '8px';
    wrapper.style.padding = '10px';
    wrapper.style.backgroundColor = 'transparent';
    wrapper.style.color = 'var(--color-secondary)';
    wrapper.style.cursor = 'pointer';
    wrapper.style.textAlign = 'center';

    // Crear un label para el botón
    const label = document.createElement('label');
    label.textContent = 'Seleccionar archivo';
    label.style.display = 'block';
    label.style.color = 'var(--color-secondary)';
    label.style.marginBottom = '5px';
    wrapper.appendChild(label);

    // Crear un span para mostrar el nombre del archivo
    const fileName = document.createElement('span');
    fileName.classList.add('file-name');
    fileName.textContent = 'Ningún archivo seleccionado';
    fileName.style.display = 'block';
    fileName.style.marginTop = '5px';
    fileName.style.color = 'var(--color-secondary)';
    fileName.style.fontSize = '0.9rem';
    wrapper.appendChild(fileName);

    // Insertar el input dentro del contenedor
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    // Aplicar estilos al input para hacerlo invisible
    input.style.position = 'absolute';
    input.style.left = '0';
    input.style.top = '0';
    input.style.width = '100%';
    input.style.height = '100%';
    input.style.opacity = '0';
    input.style.cursor = 'pointer';

    // Actualizar el nombre del archivo seleccionado
    input.addEventListener('change', function () {
      if (this.files.length > 0) {
        fileName.textContent = this.files[0].name;
      } else {
        fileName.textContent = 'Ningún archivo seleccionado';
      }
    });
  });
});