/* ============================================================
   WhatsApp Appointment OS — app.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── 1. Toast auto-dismiss ──────────────────────────────────
  document.querySelectorAll('.toast-auto').forEach(el => {
    setTimeout(() => {
      el.classList.add('toast-hide');
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ── 2. Password show/hide toggle ──────────────────────────
  document.querySelectorAll('[data-pw-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.pwToggle);
      if (!target) return;
      const isText = target.type === 'text';
      target.type = isText ? 'password' : 'text';
      btn.querySelector('i').className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
    });
  });

  // ── 3. Delete confirmation ─────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) e.preventDefault();
    });
  });

  // ── 4. Edit Staff modal prefill ───────────────────────────
  const editStaffModal = document.getElementById('editStaffModal');
  if (editStaffModal) {
    editStaffModal.addEventListener('show.bs.modal', event => {
      const btn = event.relatedTarget;
      editStaffModal.querySelector('#edit-staff-name').value     = btn.dataset.name     || '';
      editStaffModal.querySelector('#edit-staff-phone').value    = btn.dataset.phone    || '';
      editStaffModal.querySelector('#edit-staff-email').value    = btn.dataset.email    || '';
      editStaffModal.querySelector('#edit-staff-position').value = btn.dataset.position || '';
      const form = editStaffModal.querySelector('form');
      form.action = `/staff/edit/${btn.dataset.pk}/`;
    });
  }


  // ── 5. Appointment table search filter ────────────────────
  const searchInput = document.getElementById('appointmentSearch');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase();
      document.querySelectorAll('#appointmentTable tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── 6. Staff card search filter ───────────────────────────
  const staffSearch = document.getElementById('staffSearch');
  if (staffSearch) {
    staffSearch.addEventListener('input', () => {
      const q = staffSearch.value.toLowerCase();
      document.querySelectorAll('.staff-card-wrap').forEach(card => {
        card.style.display = card.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── 7. Datetime-local: prevent past appointments ──────────
  const dtInput = document.getElementById('appointment_date');
  if (dtInput) {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    dtInput.min = now.toISOString().slice(0, 16);
  }

  // ── 8. Entrance animations via IntersectionObserver ───────
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.stat-card, .card').forEach(el => {
    el.classList.add('animate-pending');
    observer.observe(el);
  });

  // ── 9. Navbar active link highlight ───────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/') {
      link.classList.add('active');
    }
  });
});
