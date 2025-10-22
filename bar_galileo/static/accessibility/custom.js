document.addEventListener("DOMContentLoaded", function() {
    const buttonLabels = {
        "Readable Font": "Fuente Legible",
        "Highlight Links": "Resaltar Enlaces",
        "Highlight Title": "Resaltar Título",
        "Monochrome": "Monocromo",
        "Low Saturation": "Baja Saturación",
        "High Saturation": "Alta Saturación",
        "High Contrast": "Alto Contraste",
        "Light Contrast": "Bajo Contraste",
        "Dark Contrast": "Contraste Oscuro",
        "Big Cursor": "Cursor Grande",
        "Stop Animations": "Detener Animaciones",
        "Reading Guide": "Guía de Lectura",
        "Read Page": "Leer Página",
        "Read Full Page": "Leer toda la página",
        "Dark Mode": "Modo Oscuro"
    };

    document.querySelectorAll('.asw-btn').forEach(button => {
        const icon = button.querySelector('.material-icons');
        if (!icon) return;
        const textNode = icon.nextSibling;
        if (!textNode || !textNode.nodeValue) return;
        const key = textNode.nodeValue.trim();
        if (buttonLabels[key]) {
            textNode.nodeValue = buttonLabels[key];
            // update aria-label/title as well
            button.setAttribute('aria-label', buttonLabels[key]);
            button.setAttribute('title', buttonLabels[key]);
        }
    });
});

