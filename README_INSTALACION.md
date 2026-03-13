# EPS Digital - instalación local con Python

## 1) Requisitos
- Python 3.10 o superior
- VS Code, PyCharm o terminal

## 2) Abrir el proyecto
Descomprime la carpeta del proyecto y ubícate dentro de `eps-digital-flask`.

## 3) Crear entorno virtual
### En Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### En macOS o Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4) Instalar dependencias
```bash
pip install -r requirements.txt
```

## 5) Ejecutar el servidor local
```bash
python app.py
```

Luego abre en el navegador:
```text
http://127.0.0.1:5000
```

## 6) Qué trae implementado
- Inicio
- Registro
- Inicio de sesión
- Mi Perfil
- Citas Médicas > Agendar nueva cita
- Citas Médicas > Ver citas programadas
- Asistente Virtual con respuesta simulada
- Servicios con buscador
- Ayuda
- Opciones con asterisco que muestran `En construcción`
- Navegación con teclado usando Tab y Shift+Tab
- Atajo Alt + H para volver al inicio

## 7) Dónde se guardan los datos
Los datos se guardan en:
- `storage/users.json`
- `storage/appointments.json`

Eso significa que no necesitas MySQL, XAMPP ni PHP para la demostración local.

## 8) Usuario de prueba
No viene un usuario precargado. La idea es que primero uses la pantalla de registro y luego entres con ese mismo documento y contraseña.

## 9) Si el puerto 5000 está ocupado
Puedes cambiar la última línea de `app.py` por algo como:
```python
app.run(debug=True, port=8000)
```

Y luego abres:
```text
http://127.0.0.1:8000
```

## 10) Opción 2: ejecutar con Flask
También puedes usar:
```bash
flask --app app run
```

## 11) Recomendación para la entrega
Si el profesor solo necesita ver el sistema funcionando, esta versión es suficiente para correr en local y enseñar la navegación completa del prototipo.
