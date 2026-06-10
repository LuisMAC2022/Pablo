@echo off
echo [%date% %time%] Iniciando deploy... >> C:\Users\Vigilancia\Pablo\logs\deploy.log

cd /d C:\Users\Vigilancia\Pablo

echo [%date% %time%] Haciendo git pull... >> logs\deploy.log
git pull origin master >> logs\deploy.log 2>&1

echo [%date% %time%] Aplicando migraciones... >> logs\deploy.log
call .venv\Scripts\activate
alembic upgrade head >> logs\deploy.log 2>&1

echo [%date% %time%] Reiniciando servicio... >> logs\deploy.log
nssm restart PabeAppMantenimiento >> logs\deploy.log 2>&1

echo [%date% %time%] Deploy completado. >> logs\deploy.log