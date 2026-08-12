# Pablo

## Pruebas

Instale las dependencias de desarrollo y ejecute la suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Despliegue

Después de actualizar el código en el servidor, reinicie el proceso Python que
ejecuta la aplicación para que cargue la nueva versión. No es necesario cambiar
`deploy.bat` para desplegar una rama de corrección.
