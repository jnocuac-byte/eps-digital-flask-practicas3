document.addEventListener('DOMContentLoaded', () => {
  setupDropdowns();
  setupAppointmentSummary();
  setupAssistantChat();
  setupServiceSearch();
  setupKeyboardShortcut();
});

function setupDropdowns() {
  const dropdowns = document.querySelectorAll('.nav-dropdown');
  dropdowns.forEach((dropdown) => {
    const button = dropdown.querySelector('.nav-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    if (!button || !menu) return;

    button.addEventListener('click', () => toggleDropdown(button, menu));
    button.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleDropdown(button, menu);
      }
      if (event.key === 'Escape') {
        closeDropdown(button, menu);
      }
    });
  });

  document.addEventListener('click', (event) => {
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(event.target)) {
        const button = dropdown.querySelector('.nav-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        closeDropdown(button, menu);
      }
    });
  });
}

function toggleDropdown(button, menu) {
  const isOpen = menu.classList.contains('show');
  document.querySelectorAll('.dropdown-menu').forEach((item) => item.classList.remove('show'));
  document.querySelectorAll('.nav-toggle').forEach((item) => item.setAttribute('aria-expanded', 'false'));
  if (!isOpen) {
    menu.classList.add('show');
    button.setAttribute('aria-expanded', 'true');
  }
}

function closeDropdown(button, menu) {
  if (!button || !menu) return;
  menu.classList.remove('show');
  button.setAttribute('aria-expanded', 'false');
}

function setupAppointmentSummary() {
  const service = document.getElementById('service');
  const doctor = document.getElementById('doctor');
  const symptoms = document.getElementById('symptoms');
  const serviceSummary = document.getElementById('summary-service');
  const specialtySummary = document.getElementById('summary-specialty');
  const doctorSummary = document.getElementById('summary-doctor');
  const symptomsSummary = document.getElementById('summary-symptoms');

  if (!service || !serviceSummary) return;

  const render = () => {
    const selected = window.serviceOptions?.[service.value];
    serviceSummary.textContent = service.value || '-';
    specialtySummary.textContent = selected?.specialty || '-';
    if (selected && doctor && !doctor.value) {
      doctor.value = selected.doctor;
    }
    doctorSummary.textContent = doctor?.value || selected?.doctor || '-';
    symptomsSummary.textContent = symptoms?.value || '-';
  };

  [service, doctor, symptoms].forEach((field) => field && field.addEventListener('input', render));
  render();
}

function setupAssistantChat() {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const body = document.getElementById('chat-body');
  if (!form || !input || !body) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    appendMessage(body, text, 'user');
    appendMessage(body, getBotReply(text), 'bot');
    input.value = '';
  });
}

function appendMessage(container, text, role) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function getBotReply(text) {
  const lower = text.toLowerCase();
  if (lower.includes('cardio')) {
    return 'Te recomiendo seleccionar Cardiología en el formulario de citas y revisar disponibilidad con el Dr. Andrés Ramírez.';
  }
  if (lower.includes('agendar') || lower.includes('cita')) {
    return 'Puedes hacerlo desde Citas Médicas > Agendar nueva cita. Allí eliges servicio, fecha, hora y síntomas.';
  }
  if (lower.includes('servicio')) {
    return 'Actualmente el demo muestra Medicina General, Cardiología, Pediatría y Odontología como servicios principales.';
  }
  return 'Gracias por tu mensaje. Este asistente es una simulación local para el prototipo académico y puede orientarte en funciones básicas.';
}

function setupServiceSearch() {
  const input = document.getElementById('service-search');
  const cards = document.querySelectorAll('.service-card');
  if (!input || !cards.length) return;

  input.addEventListener('input', () => {
    const term = input.value.toLowerCase().trim();
    cards.forEach((card) => {
      const text = card.dataset.service || '';
      card.style.display = text.includes(term) ? 'block' : 'none';
    });
  });
}

function setupKeyboardShortcut() {
  document.addEventListener('keydown', (event) => {
    if (event.altKey && event.key.toLowerCase() === 'h') {
      window.location.href = '/';
    }
  });
}
