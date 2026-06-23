const botonImprimir = document.getElementById("imprimir-solicitud");

if (botonImprimir) {
  botonImprimir.addEventListener("click", () => {
    const urlPdf = botonImprimir.dataset.urlPdf;

    if (!urlPdf) {
      const mensaje = document.getElementById("mensaje-pdf");

      if (mensaje) {
        mensaje.textContent = "No se encontró la URL del PDF para imprimir.";
      }

      return;
    }

    window.open(urlPdf, "_blank", "noopener");
  });
}
