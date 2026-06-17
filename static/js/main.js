/* =============================================================
   BOOKSTORE — main.js
   All interactive UI: theme, cart AJAX, wishlist, autocomplete,
   toasts, qty-steppers, gallery, skeleton loader removal.
   ============================================================= */

/* ── 0. THEME — runs immediately (before DOMContentLoaded) ────── */
(function () {
  const saved = localStorage.getItem('bs-theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', saved);
})();

/* ── 1. DOM READY ───────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  /* ─── Theme Toggle ─────────────────────────────────────────── */
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon   = document.getElementById('themeIcon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('bs-theme', theme);
    if (themeIcon) {
      themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  // Set icon to match current theme on load
  applyTheme(localStorage.getItem('bs-theme') || 'light');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-bs-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  /* ─── Mobile menu toggle ────────────────────────────────────── */
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const mobileMenu   = document.getElementById('mobileMenu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', function () {
      mobileMenu.classList.toggle('open');
      const icon = this.querySelector('i');
      if (icon) icon.className = mobileMenu.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
    });
  }

  /* ─── Cart count badge init ─────────────────────────────────── */
  syncCartBadge();

  /* ─── Add-to-cart AJAX ──────────────────────────────────────── */
  document.querySelectorAll('.add-to-cart-ajax').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"], .btn-overlay-cart');
      if (btn) {
        btn.disabled = true;
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        setTimeout(() => { btn.disabled = false; btn.innerHTML = orig; }, 1500);
      }
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCSRF() },
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showToast(data.message || 'Added to cart!', 'success');
            updateCartBadge(data.total_items);
          } else {
            showToast(data.message || 'Error adding to cart', 'error');
          }
        })
        .catch(() => {
          // Graceful fallback: full page submit
          form.submit();
        });
    });
  });

  /* ─── Wishlist AJAX ─────────────────────────────────────────── */
  document.querySelectorAll('.wishlist-form-ajax').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = form.querySelector('button');
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCSRF() },
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showToast(data.message || (data.added ? 'Added to wishlist!' : 'Removed from wishlist'), data.added ? 'success' : 'info');
            if (btn) {
              btn.classList.toggle('active', !!data.added);
              const icon = btn.querySelector('i');
              if (icon) icon.style.color = data.added ? 'var(--danger)' : '';
            }
          }
        })
        .catch(() => form.submit());
    });
  });

  /* ─── Cart page: qty change + remove (AJAX) ─────────────────── */
  // Qty +/- buttons
  document.querySelectorAll('.cart-qty-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const itemId  = this.dataset.item;
      const action  = this.dataset.action; // 'inc' | 'dec'
      const input   = document.querySelector(`.cart-qty-input[data-item="${itemId}"]`);
      if (!input) return;
      let val = parseInt(input.value) || 1;
      val = action === 'inc' ? val + 1 : Math.max(1, val - 1);
      input.value = val;
      updateCartItem(itemId, val);
    });
  });

  document.querySelectorAll('.cart-qty-input').forEach(function (input) {
    input.addEventListener('change', function () {
      const val = Math.max(1, parseInt(this.value) || 1);
      this.value = val;
      updateCartItem(this.dataset.item, val);
    });
  });

  // Remove item buttons
  document.querySelectorAll('.cart-remove-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const itemId = this.dataset.item;
      const row    = document.getElementById('cart-row-' + itemId);
      if (row) { row.style.opacity = '0.4'; row.style.pointerEvents = 'none'; }
      fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCSRF() },
      })
        .then(r => r.json())
        .then(data => {
          if (row) row.remove();
          if (data.total_items !== undefined) updateCartBadge(data.total_items);
          refreshCartSummary(data.subtotal || null);
          showToast('Mahsulot savatdan o\'chirildi', 'info');
        })
        .catch(() => window.location.reload());
    });
  });

  /* ─── Coupon code apply ─────────────────────────────────────── */
  const couponForm = document.getElementById('couponForm');
  if (couponForm) {
    couponForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const code = document.getElementById('couponInput').value.trim();
      if (!code) return;
      fetch('/payments/apply-coupon/', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            showToast(data.message || `Kupon qo'llanildi!`, 'success');
            const discount = parseFloat(data.discount) || 0;
            const subtotalEl = document.getElementById('cartSubtotal');
            const totalEl = document.getElementById('cartTotal');
            const discountRow = document.getElementById('discountRow');
            const discountEl = document.getElementById('cartDiscount');
            if (subtotalEl && totalEl && discount > 0) {
              const subtotal = parseFloat(subtotalEl.textContent.replace(/[^\d.]/g, '')) || 0;
              const newTotal = Math.max(0, subtotal - discount);
              if (discountRow) discountRow.style.display = '';
              if (discountEl) discountEl.textContent = `-${discount.toLocaleString()} so'm`;
              totalEl.textContent = `${newTotal.toLocaleString()} so'm`;
            }
            refreshCartSummary();
          } else {
            showToast(data.message || 'Kupon kodi noto\'g\'ri yoki muddati o\'tgan', 'error');
          }
        })
        .catch(() => showToast('Kupon qo\'llanilmadi, qayta urinib ko\'ring', 'error'));
    });
  }

  /* ─── Remove coupon ─────────────────────────────────────────── */
  const removeCouponBtn = document.getElementById('removeCouponBtn');
  if (removeCouponBtn) {
    removeCouponBtn.addEventListener('click', function () {
      fetch('/cart/remove-coupon/', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCSRF() },
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) location.reload();
        });
    });
  }

  /* ─── Search Autocomplete ───────────────────────────────────── */
  const searchInput = document.getElementById('mainSearchInput');
  const acDropdown  = document.getElementById('searchAutocomplete');

  if (searchInput && acDropdown) {
    let acTimer = null;

    searchInput.addEventListener('input', function () {
      clearTimeout(acTimer);
      const q = this.value.trim();
      if (q.length < 2) { hideAutocomplete(); return; }
      acTimer = setTimeout(() => fetchAutocomplete(q), 280);
    });

    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') hideAutocomplete();
      if (e.key === 'ArrowDown') {
        const first = acDropdown.querySelector('.autocomplete-item');
        if (first) first.focus();
        e.preventDefault();
      }
    });

    // Arrow-key navigation within dropdown
    acDropdown.addEventListener('keydown', function (e) {
      const items = [...acDropdown.querySelectorAll('.autocomplete-item')];
      const idx   = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' && idx < items.length - 1) { items[idx + 1].focus(); e.preventDefault(); }
      if (e.key === 'ArrowUp') {
        if (idx > 0) items[idx - 1].focus();
        else searchInput.focus();
        e.preventDefault();
      }
      if (e.key === 'Escape') { hideAutocomplete(); searchInput.focus(); }
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !acDropdown.contains(e.target)) hideAutocomplete();
    });
  }

  function fetchAutocomplete(q) {
    if (!acDropdown) return;
    acDropdown.innerHTML = '<div class="autocomplete-loading"><i class="fas fa-spinner fa-spin me-2"></i>Searching…</div>';
    acDropdown.classList.add('active');

    fetch(`/autocomplete/?q=${encodeURIComponent(q)}&format=json`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then(r => r.json())
      .then(data => {
        if (!data.results || data.results.length === 0) {
          acDropdown.innerHTML = `<div class="autocomplete-empty">No results for "<strong>${escHtml(q)}</strong>"</div>`;
          return;
        }
        acDropdown.innerHTML = data.results.map(item => `
          <a class="autocomplete-item" href="${item.url}" tabindex="0">
            ${item.cover
              ? `<img src="${item.cover}" alt="${escHtml(item.title)}" loading="lazy">`
              : `<div class="autocomplete-item-placeholder"><i class="fas fa-book"></i></div>`}
            <div class="autocomplete-item-info">
              <div class="autocomplete-item-title">${escHtml(item.title)}</div>
              <div class="autocomplete-item-meta">${escHtml(item.author)} · <strong>$${item.price}</strong></div>
            </div>
          </a>`).join('') +
          `<a class="autocomplete-item" href="/search/?q=${encodeURIComponent(q)}" style="justify-content:center;font-size:.8rem;color:var(--primary);font-weight:600;border-top:1px solid var(--border-light)">
            <i class="fas fa-search me-2"></i>See all results for "${escHtml(q)}"
          </a>`;
      })
      .catch(() => hideAutocomplete());
  }

  function hideAutocomplete() {
    if (acDropdown) { acDropdown.classList.remove('active'); acDropdown.innerHTML = ''; }
  }

  /* ─── Detail page: image gallery ───────────────────────────── */
  const mainImg = document.getElementById('mainBookImage');
  document.querySelectorAll('.gallery-thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      if (mainImg) {
        mainImg.src = this.dataset.src || this.querySelector('img')?.src || '';
        mainImg.style.animation = 'none';
        mainImg.offsetHeight; // reflow
        mainImg.style.animation = 'pageFadeIn .2s ease';
      }
      document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  /* ─── Detail page: qty stepper ─────────────────────────────── */
  const qtyInput   = document.getElementById('detailQty');
  const qtyMinus   = document.getElementById('qtyMinus');
  const qtyPlus    = document.getElementById('qtyPlus');
  const qtyMax     = qtyInput ? parseInt(qtyInput.dataset.max || '9999') : 9999;

  if (qtyMinus) qtyMinus.addEventListener('click', () => stepQty(-1));
  if (qtyPlus)  qtyPlus.addEventListener('click',  () => stepQty(+1));

  function stepQty(delta) {
    if (!qtyInput) return;
    const v = Math.max(1, Math.min(qtyMax, (parseInt(qtyInput.value) || 1) + delta));
    qtyInput.value = v;
  }

  /* ─── Star rating input (review form) ──────────────────────── */
  document.querySelectorAll('.star-rating-input .star-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const val     = parseInt(this.dataset.value);
      const input   = document.getElementById('ratingValue');
      if (input) input.value = val;
      const allBtns = [...this.closest('.star-rating-input').querySelectorAll('.star-btn')];
      allBtns.forEach((b, i) => {
        b.classList.toggle('active', i < val);
        b.innerHTML = `<i class="${i < val ? 'fas' : 'far'} fa-star"></i>`;
      });
    });
  });

  /* ─── Filter section collapse/expand ───────────────────────── */
  window.toggleSection = function (id) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('collapsed');
  };

  /* ─── Sort select preserves other query params ──────────────── */
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      const url = new URL(window.location.href);
      url.searchParams.set('ordering', this.value);
      url.searchParams.delete('page');
      window.location.href = url.toString();
    });
  }

  /* ─── Grid / List view toggle ───────────────────────────────── */
  const btnGrid  = document.getElementById('btnGrid');
  const btnList  = document.getElementById('btnList');
  const gridView = document.getElementById('gridView');
  const listView = document.getElementById('listView');

  function setView(v) {
    if (!gridView || !listView) return;
    const isGrid = v === 'grid';
    gridView.style.display = isGrid ? '' : 'none';
    listView.style.display = isGrid ? 'none' : '';
    btnGrid?.classList.toggle('active', isGrid);
    btnList?.classList.toggle('active', !isGrid);
    localStorage.setItem('bookView', v);
  }

  if (btnGrid) btnGrid.addEventListener('click', () => setView('grid'));
  if (btnList) btnList.addEventListener('click', () => setView('list'));
  if (gridView && listView) setView(localStorage.getItem('bookView') || 'grid');

  /* ─── Skeleton loader — hide after page loaded ──────────────── */
  document.querySelectorAll('.skeleton-card').forEach(function (el) {
    el.style.display = 'none';
  });

  /* ─── Animate elements on scroll ───────────────────────────── */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('page-fade-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.book-card, .stat-card, .book-list-item').forEach(el => io.observe(el));
  }

}); // end DOMContentLoaded

/* ── 2. HELPERS ─────────────────────────────────────────────────── */

function getCSRF() {
  return window.CSRF_TOKEN || getCookieVal('csrftoken') || '';
}

function getCookieVal(name) {
  for (const c of document.cookie.split(';')) {
    const [k, v] = c.trim().split('=');
    if (k === name) return decodeURIComponent(v || '');
  }
  return '';
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ── 3. TOAST NOTIFICATIONS ─────────────────────────────────────── */
function showToast(message, type) {
  type = type || 'info';
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = {
    success: 'fa-check-circle',
    error:   'fa-times-circle',
    warning: 'fa-exclamation-triangle',
    info:    'fa-info-circle',
  };

  const el = document.createElement('div');
  el.className = `toast-notification ${type}`;
  el.setAttribute('role', 'alert');
  el.setAttribute('aria-live', 'polite');
  el.innerHTML = `
    <i class="fas ${icons[type] || icons.info} toast-icon"></i>
    <div class="toast-body">
      <div class="toast-message">${escHtml(message)}</div>
    </div>
    <button class="toast-close" aria-label="Close"><i class="fas fa-times"></i></button>
    <div class="toast-progress"></div>`;

  container.appendChild(el);

  // Close button
  el.querySelector('.toast-close').addEventListener('click', () => dismissToast(el));

  // Auto-dismiss after 4 s
  const timer = setTimeout(() => dismissToast(el), 4000);
  el.dataset.timer = timer;
}

function dismissToast(el) {
  clearTimeout(el.dataset.timer);
  el.classList.add('leaving');
  el.addEventListener('animationend', () => el.remove(), { once: true });
}

/* ── 4. CART BADGE ───────────────────────────────────────────────── */
function updateCartBadge(count) {
  const badges = document.querySelectorAll('#cartCount');
  badges.forEach(b => {
    b.textContent = count;
    b.classList.toggle('hidden', count <= 0);
  });
}

function syncCartBadge() {
  // Read server-rendered value injected by context processor
  const badge = document.querySelector('#cartCount');
  if (badge) {
    const n = parseInt(badge.textContent) || 0;
    badge.classList.toggle('hidden', n <= 0);
  }
}

/* ── 5. CART ITEM AJAX UPDATE ────────────────────────────────────── */
function updateCartItem(itemId, qty) {
  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': getCSRF(),
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${qty}`,
  })
    .then(r => r.json())
    .then(data => {
      if (data.total_items !== undefined) updateCartBadge(data.total_items);
      if (data.subtotal) refreshCartSummary(data.subtotal);
    })
    .catch(() => {});
}

function refreshCartSummary(subtotal) {
  const subtotalEl = document.getElementById('cartSubtotal');
  const totalEl    = document.getElementById('cartTotal');

  // If subtotal not passed, recalculate from item prices on the page
  if (!subtotal) {
    let sum = 0;
    document.querySelectorAll('[id^="cart-row-"]').forEach(function (row) {
      const priceEl = row.querySelector('.cart-qty-input');
      const unitPriceEl = row.querySelector('[data-unit-price]');
      if (unitPriceEl && priceEl) {
        sum += parseFloat(unitPriceEl.dataset.unitPrice || 0) * (parseInt(priceEl.value) || 1);
      }
    });
    if (sum > 0) subtotal = sum;
    else if (subtotalEl) {
      subtotal = parseFloat(subtotalEl.textContent.replace(/[^\d.]/g, '')) || 0;
    }
  }

  if (subtotal !== undefined && subtotal !== null) {
    const sub = parseFloat(subtotal);
    const shipping = sub >= 35000 ? 0 : 5000;
    const discountEl = document.getElementById('cartDiscount');
    const discount = discountEl
      ? parseFloat(discountEl.textContent.replace(/[^\d.]/g, '')) || 0
      : 0;
    const total = Math.max(0, sub + shipping - discount);
    if (subtotalEl) subtotalEl.textContent = `${sub.toLocaleString('uz-UZ')} so'm`;
    if (totalEl)    totalEl.textContent    = `${total.toLocaleString('uz-UZ')} so'm`;

    // Update shipping display
    const shippingEls = document.querySelectorAll('.cart-summary-row span[id]');
    document.querySelectorAll('.cart-summary-row').forEach(function (row) {
      const label = row.querySelector('span:first-child');
      const val   = row.querySelector('span:last-child');
      if (label && val && label.textContent.trim().startsWith('Yetkazib')) {
        if (shipping === 0) {
          val.textContent = 'Bepul';
          val.style.color = 'var(--c-success)';
        } else {
          val.textContent = '5 000 so\'m';
          val.style.color = '';
        }
      }
    });
  }

  // Check if cart is empty
  const rows = document.querySelectorAll('[id^="cart-row-"]');
  if (rows.length === 0) {
    const cartWrapper = document.getElementById('cartContent');
    if (cartWrapper) {
      cartWrapper.innerHTML = `
        <div class="text-center py-5" style="padding:60px 0 !important">
          <div style="font-size:5rem;opacity:.2;margin-bottom:20px">🛒</div>
          <h3 style="font-weight:700;color:var(--t-secondary);margin-bottom:8px">Savatingiz bo'sh</h3>
          <p style="color:var(--t-muted);margin-bottom:24px">Minglab ajoyib kitoblarni kashf eting va savatga qo'shing.</p>
          <a href="/" class="btn-add-cart" style="background:var(--c-primary);color:#fff">
            <i class="fas fa-book-open me-2"></i>Kitoblarga qarang
          </a>
        </div>`;
    }
  }
}

/* ── 6. LEGACY changeQty (used in older detail template) ────────── */
function changeQty(delta) {
  const input = document.getElementById('qty') || document.getElementById('detailQty');
  if (!input) return;
  const max = parseInt(input.dataset.max || input.max || '9999');
  input.value = Math.max(1, Math.min(max, (parseInt(input.value) || 1) + delta));
}
