from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from functools import wraps
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / 'storage'
USERS_FILE = STORAGE_DIR / 'users.json'
APPOINTMENTS_FILE = STORAGE_DIR / 'appointments.json'

app = Flask(__name__)
app.secret_key = 'eps-digital-demo-local'

SERVICE_OPTIONS = {
    'Medicina General': {'specialty': 'Medicina General', 'doctor': 'Dra. Laura Sánchez'},
    'Cardiología': {'specialty': 'Cardiología', 'doctor': 'Dr. Andrés Ramírez'},
    'Pediatría': {'specialty': 'Pediatría', 'doctor': 'Dra. Paula Gómez'},
    'Odontología': {'specialty': 'Odontología', 'doctor': 'Dr. Miguel Torres'},
    'Laboratorio y Exámenes': {'specialty': 'Diagnóstico Clínico', 'doctor': 'Equipo de Laboratorio'},
}

SERVICES_CATALOG = [
    {'title': 'Medicina General', 'description': 'Consultas de salud integral para control preventivo y seguimiento básico.', 'availability': 'Disponible', 'implemented': True, 'icon': '🩺'},
    {'title': 'Cardiología', 'description': 'Valoración del corazón y del sistema circulatorio.', 'availability': 'Disponible', 'implemented': True, 'icon': '❤️'},
    {'title': 'Pediatría', 'description': 'Atención médica infantil para crecimiento, control y enfermedades comunes.', 'availability': 'Disponible', 'implemented': True, 'icon': '👶'},
    {'title': 'Odontología', 'description': 'Servicios de salud oral, limpieza y valoración.', 'availability': 'Disponible', 'implemented': True, 'icon': '🦷'},
    {'title': 'Urgencias*', 'description': 'Módulo visual preparado para futura integración con atención prioritaria.', 'availability': 'En construcción', 'implemented': False, 'icon': '🚑'},
    {'title': 'Laboratorio y Exámenes*', 'description': 'Flujo preparado para órdenes y resultados, pendiente de desarrollo completo.', 'availability': 'En construcción', 'implemented': False, 'icon': '🧪'},
]

FAQ_ITEMS = [
    {'question': '¿Cómo agendo una cita?', 'answer': 'Ingresa a Citas Médicas, selecciona Agendar nueva cita y completa el formulario.'},
    {'question': '¿Necesito registrarme?', 'answer': 'Sí. El registro local permite guardar tus datos y ver las citas programadas.'},
    {'question': '¿Qué significa el asterisco?', 'answer': 'Indica una opción no implementada completamente este semestre. Al seleccionarla verás el mensaje En construcción.'},
]


# ---------- Utilidades ----------
def ensure_storage() -> None:
    STORAGE_DIR.mkdir(exist_ok=True)
    for path in (USERS_FILE, APPOINTMENTS_FILE):
        if not path.exists():
            path.write_text('[]', encoding='utf-8')


def read_json(path: Path) -> list[dict]:
    ensure_storage()
    try:
        return json.loads(path.read_text(encoding='utf-8') or '[]')
    except json.JSONDecodeError:
        return []


def write_json(path: Path, data: list[dict]) -> None:
    ensure_storage()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def get_current_user() -> dict | None:
    return session.get('user')


def find_user_by_document(document_number: str) -> dict | None:
    users = read_json(USERS_FILE)
    for user in users:
        if user.get('document_number') == document_number:
            return user
    return None


def get_user_appointments(document_number: str) -> list[dict]:
    appointments = read_json(APPOINTMENTS_FILE)
    return [a for a in appointments if a.get('user_document') == document_number]


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not get_current_user():
            flash('Debes iniciar sesión para acceder a esta sección.', 'warning')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_globals():
    return {
        'current_user': get_current_user(),
        'service_options': SERVICE_OPTIONS,
        'current_year': datetime.now().year,
    }


# ---------- Rutas ----------
@app.route('/')
def home():
    user = get_current_user()
    appointments = get_user_appointments(user['document_number']) if user else []
    latest_appointment = appointments[-1] if appointments else None
    return render_template('home.html', page='home', latest_appointment=latest_appointment)


@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        document_type = request.form.get('document_type', '').strip()
        document_number = request.form.get('document_number', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms')

        if not all([name, email, phone, address, document_type, document_number, password, confirm_password]):
            flash('Completa todos los campos del registro.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            flash('La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))

        if not terms:
            flash('Debes aceptar términos y condiciones.', 'danger')
            return redirect(url_for('register'))

        if find_user_by_document(document_number):
            flash('Ya existe un usuario con ese número de documento.', 'warning')
            return redirect(url_for('register'))

        users = read_json(USERS_FILE)
        user = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'document_type': document_type,
            'document_number': document_number,
            'password_hash': generate_password_hash(password),
            'blood_type': 'O+',
            'allergies': 'Ninguna registrada',
            'chronic_conditions': 'Sin antecedentes reportados',
            'assigned_doctor': 'Dra. Laura Sánchez',
            'policy_number': f"POL-{document_number[-4:]}-{str(uuid4())[:4].upper()}",
            'affiliate_date': datetime.now().strftime('%Y-%m-%d'),
            'membership': 'Premium',
            'status': 'Activo',
        }
        users.append(user)
        write_json(USERS_FILE, users)
        session['user'] = user
        flash('Cuenta creada correctamente. Ya puedes gestionar tus citas.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', page='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        document_number = request.form.get('document_number', '').strip()
        password = request.form.get('password', '')
        user = find_user_by_document(document_number)

        if not user or not check_password_hash(user.get('password_hash', ''), password):
            flash('Documento o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))

        session['user'] = user
        flash('Sesión iniciada correctamente.', 'success')
        return redirect(url_for('home'))

    return render_template('login.html', page='login')


@app.post('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def profile():
    tab = request.args.get('tab', 'personal')
    valid_tabs = {'personal', 'medical', 'eps', 'settings'}
    if tab not in valid_tabs:
        tab = 'personal'
    return render_template('profile.html', page='profile', tab=tab)


@app.route('/citas/agendar', methods=['GET', 'POST'])
@login_required
def appointments_book():
    if request.method == 'POST':
        service = request.form.get('service', '').strip()
        doctor = request.form.get('doctor', '').strip()
        appointment_date = request.form.get('appointment_date', '').strip()
        appointment_time = request.form.get('appointment_time', '').strip()
        symptoms = request.form.get('symptoms', '').strip()

        if not all([service, doctor, appointment_date, appointment_time, symptoms]):
            flash('Completa todos los campos para agendar la cita.', 'danger')
            return redirect(url_for('appointments_book'))

        current_user = get_current_user()
        appointments = read_json(APPOINTMENTS_FILE)
        appointments.append({
            'id': f"CITA-{str(uuid4())[:8].upper()}",
            'user_document': current_user['document_number'],
            'service': service,
            'specialty': SERVICE_OPTIONS.get(service, {}).get('specialty', service),
            'doctor': doctor,
            'date': appointment_date,
            'time': appointment_time,
            'symptoms': symptoms,
            'status': 'Programada',
            'venue': 'Sede Central - Bogotá',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        write_json(APPOINTMENTS_FILE, appointments)
        flash('La cita fue agendada correctamente.', 'success')
        return redirect(url_for('appointments_view'))

    return render_template('appointments_book.html', page='appointments', subpage='book')


@app.route('/citas/ver')
@login_required
def appointments_view():
    current_user = get_current_user()
    appointments = get_user_appointments(current_user['document_number'])
    return render_template('appointments_view.html', page='appointments', subpage='view', appointments=appointments)


@app.route('/asistente')
def assistant():
    return render_template('assistant.html', page='assistant')


@app.route('/servicios')
def services():
    return render_template('services.html', page='services', services=SERVICES_CATALOG)


@app.route('/ayuda')
def help_page():
    tab = request.args.get('tab', 'guide')
    if tab not in {'guide', 'faq', 'support', 'legal'}:
        tab = 'guide'
    return render_template('help.html', page='help', tab=tab, faq_items=FAQ_ITEMS)


@app.route('/en-construccion')
def construction():
    title = request.args.get('title', 'Módulo en construcción')
    return render_template('construction.html', page='construction', title=title)


if __name__ == '__main__':
    ensure_storage()
    app.run(debug=True)
