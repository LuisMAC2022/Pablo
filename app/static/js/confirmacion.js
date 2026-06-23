const botonImprimir = document.getElementById("imprimir-solicitud");

if (botonImprimir) {
  botonImprimir.addEventListener("click", () => {
    window.print();
  });
}
