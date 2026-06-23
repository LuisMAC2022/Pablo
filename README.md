# Pablo

## Requisitos del servidor

La generación del PDF de la solicitud convierte la plantilla XLSX llena con LibreOffice en modo headless. El servidor debe tener disponible el ejecutable `libreoffice` en el `PATH`; si no existe, la ruta PDF responderá con un error claro de conversión.
