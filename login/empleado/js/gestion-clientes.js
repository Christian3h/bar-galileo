import { verificarSesion } from "./validarSesion.js";
verificarSesion();

const formulario = document.getElementById("formularioNuevoCliente");
const inputBuscarCliente = document.getElementById("buscarCliente");
import { mostrarMensaje } from "../js/mensaje.js";

let clienteEditando = null; // Guardar cliente en edición

mostrarClientesTabla();

// Función para generar un ID único (UUID v4)
function generarID() {
    return crypto.randomUUID();
}

// Evento para agregar o editar cliente
formulario.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(formulario);
    let data = Object.fromEntries(formData.entries());

    if (clienteEditando) {
        actualizarCliente(data);
    } else {
        guardarCliente(data);
    }

    mostrarClientesTabla();
    limpiarFormulario();
});

// Función para guardar un nuevo cliente
function guardarCliente(data) {
    const { NMesa } = data;
    let clientes = JSON.parse(localStorage.getItem("clientes")) || [];

    // Verificar si la mesa ya está ocupada
    if (clientes.some(cliente => cliente.NMesa === NMesa)) {
        mostrarMensaje("Mesa ya ocupada", "error");
        return;
    }

    // Agregar ID único al cliente
    data.id = generarID();
    clientes.push(data);
    localStorage.setItem("clientes", JSON.stringify(clientes));

    mostrarMensaje("Cliente guardado", "acierto");
}

// Función para actualizar un cliente existente
function actualizarCliente(data) {
    let clientes = JSON.parse(localStorage.getItem("clientes")) || [];

    // Verificar si la mesa está ocupada por otro cliente
    if (clientes.some(cliente => cliente.NMesa === data.NMesa && cliente.id !== clienteEditando.id)) {
        mostrarMensaje("Mesa ya ocupada", "error");
        return;
    }

    // Actualizar datos del cliente
    clientes = clientes.map(cliente =>
        cliente.id === clienteEditando.id ? { ...data, id: cliente.id } : cliente
    );

    localStorage.setItem("clientes", JSON.stringify(clientes));
    mostrarMensaje("Cliente actualizado", "acierto");
    clienteEditando = null;
}

// Función para mostrar clientes en la tabla (con filtro opcional)
function mostrarClientesTabla(filtro = "") {
    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    const tablaClientes = document.getElementById("lista-clientes");
    tablaClientes.innerHTML = ""; // Limpiar la tabla antes de llenarla

    const clientesFiltrados = clientes.filter(cliente => 
        cliente.nombre.toLowerCase().includes(filtro) || 
        cliente.telefono.includes(filtro)
    );

    clientesFiltrados.forEach(cliente => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${cliente.nombre}</td>
            <td>${cliente.telefono}</td>
            <td>${cliente.fecha}</td>
            <td>${cliente.NMesa}</td>
            <td>
                <button onclick="editarCliente('${cliente.id}')">✏️</button>
                <button onclick="eliminarCliente('${cliente.id}')">❌</button>
            </td>
        `;
        tablaClientes.appendChild(row);
    });
}

// Función para eliminar un cliente
window.eliminarCliente = function (id) {
    let clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    clientes = clientes.filter(cliente => cliente.id !== id);
    localStorage.setItem("clientes", JSON.stringify(clientes));
    mostrarClientesTabla();
    mostrarMensaje("Cliente eliminado", "error");
}

// Función para editar un cliente
window.editarCliente = function (id) {
    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    clienteEditando = clientes.find(cliente => cliente.id === id);

    if (clienteEditando) {
        document.getElementById("NMesa").value = clienteEditando.NMesa;
        document.getElementById("nombre").value = clienteEditando.nombre;
        document.getElementById("telefono").value = clienteEditando.telefono;
        document.getElementById("fecha").value = clienteEditando.fecha;

        document.getElementById("textoFormulario").innerText = "Editar Cliente";
        formulario.querySelector("button").innerText = "Actualizar Cliente";
    }
};

// Función para limpiar el formulario
function limpiarFormulario() {
    formulario.reset();
    clienteEditando = null;
    document.getElementById("textoFormulario").innerText = "Agregar nuevo cliente";
    formulario.querySelector("button").innerText = "Guardar datos";
}

// Evento para la búsqueda en tiempo real
inputBuscarCliente.addEventListener("input", function () {
    const filtro = inputBuscarCliente.value.trim().toLowerCase();
    mostrarClientesTabla(filtro);
});

// Botón para limpiar lista completa
const btnLimpiarLista = document.getElementById("btn-limpiar");
btnLimpiarLista.addEventListener("click", function () {
    localStorage.removeItem("clientes");
    mostrarClientesTabla();
    mostrarMensaje("Lista de clientes eliminada", "error");
});
