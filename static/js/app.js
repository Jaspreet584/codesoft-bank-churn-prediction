/**
 * Bank Churn Prediction Dashboard – Frontend Logic
 * Handles tab navigation, form inputs, API calls, history, and animations.
 */

/* ── Constants ─────────────────────────────────────────────────────────── */
const API_BASE = '';

// Feature importance data from the model (approximate from notebook training)
const FEATURE_IMPORTANCES = [
  { name: 'Age',               value: 0.285 },
  { name: 'Balance',           value: 0.198 },
  { name: 'NumOfProducts',     value: 0.152 },
  { name: 'IsActiveMember',    value: 0.113 },
  { name: 'CreditScore',       value: 0.092 },
  { name: 'Geography',         value: 0.072 },
  { name: 'EstimatedSalary',   value: 0.044 },
  { name: 'Gender',            value: 0.022 },
  { name: 'Tenure',            value: 0.013 },
  { name: 'HasCrCard',         value: 0.009 },
];

// Sample customers for quick-fill
const SAMPLES = {
  safe: {
    credit_score: 720,
    geography: 'France',
    gender: 'Male',
    age: 35,
    tenure: 7,
    balance: 0,
    num_of_products: 2,
    has_cr_card: 1,
    is_active_member: 1,
    estimated_salary: 95000,
  },
  risk: {
    credit_score: 600,
    geography: 'Germany',
    gender: 'Female',
    age: 47,
    tenure: 3,
    balance: 145000,
    num_of_products: 1,
    has_cr_card: 0,
    is_active_member: 0,
    estimated_salary: 120000,
  },
  critical: {
    credit_score: 450,
    geography: 'Germany',
    gender: 'Female',
    age: 60,
    tenure: 1,
    balance: 180000,
    num_of_products: 1,
    has_cr_card: 0,
    is_active_member: 0,
    estimated_salary: 60000,
  },
};

/* ── Session history (stored in memory) ─────────────────────────────────── */
let predictionHistory = JSON.parse(sessionStorage.getItem('churn_history') || '[]');

/* ── Tab navigation ─────────────────────────────────────────────────────── */
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
  });
});

/* ── Range slider live update ───────────────────────────────────────────── */
function initSlider(inputId, valId, formatter) {
  const input = document.getElementById(inputId);
  const display = document.getElementById(valId);

  const update = () => {
    display.textContent = formatter ? formatter(input.value) : input.value;
    // Update the CSS custom property for fill
    const pct = ((input.value - input.min) / (input.max - input.min)) * 100;
    input.style.setProperty('--val', `${pct}%`);
  };

  input.addEventListener('input', update);
  update(); // init
}

initSlider('input-age', 'val-age');
initSlider('input-credit-score', 'val-credit-score');
initSlider('input-tenure', 'val-tenure', v => `${v} yr${v == 1 ? '' : 's'}`);
initSlider('input-products', 'val-products');

/* ── Toggle labels ──────────────────────────────────────────────────────── */
function initToggle(checkId, labelId, onText, offText) {
  const check = document.getElementById(checkId);
  const label = document.getElementById(labelId);
  const update = () => { label.textContent = check.checked ? onText : offText; };
  check.addEventListener('change', update);
  update();
}

initToggle('input-credit-card',    'label-credit-card',    'Has Credit Card',   'No Credit Card');
initToggle('input-active-member',  'label-active-member',  'Active Member',     'Inactive Member');

/* ── Sample customer fill ───────────────────────────────────────────────── */
function fillForm(sample) {
  document.getElementById('input-credit-score').value = sample.credit_score;
  document.getElementById('input-age').value          = sample.age;
  document.getElementById('input-tenure').value       = sample.tenure;
  document.getElementById('input-products').value     = sample.num_of_products;
  document.getElementById('input-balance').value      = sample.balance;
  document.getElementById('input-salary').value       = sample.estimated_salary;
  document.getElementById('input-geography').value    = sample.geography;
  document.getElementById('input-gender').value       = sample.gender;
  document.getElementById('input-credit-card').checked    = sample.has_cr_card === 1;
  document.getElementById('input-active-member').checked  = sample.is_active_member === 1;

  // Re-trigger all slider displays and toggles
  ['input-age', 'input-credit-score', 'input-tenure', 'input-products'].forEach(id => {
    document.getElementById(id).dispatchEvent(new Event('input'));
  });
  document.getElementById('input-credit-card').dispatchEvent(new Event('change'));
  document.getElementById('input-active-member').dispatchEvent(new Event('change'));

  showToast('info', `✦ Filled with sample: ${sample.geography} customer`);
}

document.getElementById('sample-safe').addEventListener('click',     () => fillForm(SAMPLES.safe));
document.getElementById('sample-risk').addEventListener('click',     () => fillForm(SAMPLES.risk));
document.getElementById('sample-critical').addEventListener('click', () => fillForm(SAMPLES.critical));

/* ── Read form values ───────────────────────────────────────────────────── */
function getFormPayload() {
  return {
    credit_score:     parseInt(document.getElementById('input-credit-score').value, 10),
    geography:        document.getElementById('input-geography').value,
    gender:           document.getElementById('input-gender').value,
    age:              parseInt(document.getElementById('input-age').value, 10),
    tenure:           parseInt(document.getElementById('input-tenure').value, 10),
    balance:          parseFloat(document.getElementById('input-balance').value) || 0,
    num_of_products:  parseInt(document.getElementById('input-products').value, 10),
    has_cr_card:      document.getElementById('input-credit-card').checked ? 1 : 0,
    is_active_member: document.getElementById('input-active-member').checked ? 1 : 0,
    estimated_salary: parseFloat(document.getElementById('input-salary').value) || 0,
  };
}

/* ── Predict ────────────────────────────────────────────────────────────── */
const predictBtn = document.getElementById('predict-btn');
const predictSpinner = document.getElementById('predict-spinner');
const predictBtnText = document.getElementById('predict-btn-text');

predictBtn.addEventListener('click', async () => {
  const payload = getFormPayload();

  // Button loading state
  predictBtn.disabled = true;
  predictSpinner.classList.add('visible');
  predictBtnText.textContent = 'Analysing…';

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderResult(data, payload);
    addToHistory(data, payload);
    updateSessionStats();
    showToast('success', `✦ Prediction complete — ${data.label} (${(data.churn_probability * 100).toFixed(1)}% churn risk)`);

  } catch (err) {
    showToast('error', `❌ Prediction failed: ${err.message}`);
    console.error(err);
  } finally {
    predictBtn.disabled = false;
    predictSpinner.classList.remove('visible');
    predictBtnText.textContent = '🔮 Predict Churn Risk';
  }
});

/* ── Render prediction result ───────────────────────────────────────────── */
function renderResult(data, payload) {
  const isChurn = data.prediction === 1;

  const panel       = document.getElementById('result-panel');
  const header      = document.getElementById('result-header');
  const iconEl      = document.getElementById('result-icon');
  const verdictEl   = document.getElementById('result-verdict');
  const subEl       = document.getElementById('result-sub');
  const gaugeFill   = document.getElementById('gauge-fill');
  const gaugePct    = document.getElementById('gauge-pct-label');
  const riskBadge   = document.getElementById('risk-badge');

  const churnPct = (data.churn_probability * 100).toFixed(1);

  // Header styling
  header.className = `result-header ${isChurn ? 'churn-header' : 'retain-header'}`;
  panel.className  = `result-panel ${isChurn ? 'churn-result' : 'retain-result'}`;

  iconEl.className      = `result-icon-big ${isChurn ? 'churn-icon' : 'retain-icon'}`;
  iconEl.textContent    = isChurn ? '⚠️' : '✅';
  verdictEl.className   = `result-verdict ${isChurn ? 'churn-text' : 'retain-text'}`;
  verdictEl.textContent = isChurn ? '⚠ Likely to Churn' : '✓ Customer Retained';
  subEl.textContent     = isChurn
    ? `This customer has a ${churnPct}% probability of leaving the bank.`
    : `This customer is likely to stay. Churn risk is only ${churnPct}%.`;

  // Gauge
  gaugeFill.className = `gauge-fill ${isChurn ? 'churn-fill' : 'retain-fill'}`;
  setTimeout(() => { gaugeFill.style.width = `${churnPct}%`; }, 50);
  gaugePct.textContent = `${churnPct}%`;

  // Risk badge
  const riskClass = {
    'Low':      'risk-low',
    'Medium':   'risk-medium',
    'High':     'risk-high',
    'Critical': 'risk-critical',
  }[data.risk_level] || 'risk-low';

  const riskEmoji = { Low: '🟢', Medium: '🟡', High: '🔴', Critical: '🚨' }[data.risk_level] || '—';
  riskBadge.className = `risk-badge ${riskClass}`;
  riskBadge.textContent = `${riskEmoji} ${data.risk_level} Risk`;

  // Meta values
  document.getElementById('meta-churn-prob').textContent  = `${(data.churn_probability * 100).toFixed(2)}%`;
  document.getElementById('meta-retain-prob').textContent = `${(data.retain_probability * 100).toFixed(2)}%`;
  document.getElementById('meta-time').textContent        = `${data.processing_time_ms} ms`;
  document.getElementById('meta-timestamp').textContent   = new Date().toLocaleTimeString();

  // Show result, hide placeholder
  document.getElementById('result-panel-wrap').style.display = 'block';
  document.getElementById('result-placeholder').style.display = 'none';
}

/* ── Prediction history ─────────────────────────────────────────────────── */
function addToHistory(data, payload) {
  const entry = {
    id:           predictionHistory.length + 1,
    geography:    payload.geography,
    age:          payload.age,
    credit_score: payload.credit_score,
    balance:      payload.balance,
    label:        data.label,
    churn_prob:   data.churn_probability,
    risk_level:   data.risk_level,
    timestamp:    new Date().toLocaleTimeString(),
  };

  predictionHistory.unshift(entry); // newest first
  sessionStorage.setItem('churn_history', JSON.stringify(predictionHistory));
  renderHistory();
}

function renderHistory() {
  const tbody   = document.getElementById('history-table-body');
  const empty   = document.getElementById('history-empty');
  const wrapper = document.getElementById('history-wrapper');

  if (predictionHistory.length === 0) {
    empty.style.display   = 'block';
    wrapper.style.display = 'none';
    return;
  }

  empty.style.display   = 'none';
  wrapper.style.display = 'block';

  tbody.innerHTML = predictionHistory.map(e => {
    const isChurn = e.label === 'Churned';
    const pillClass = isChurn ? 'pill-churn' : 'pill-retain';
    const riskColor = { Low: 'var(--accent-green)', Medium: 'var(--accent-amber)', High: 'var(--accent-red)', Critical: '#be123c' }[e.risk_level] || 'var(--text-muted)';
    return `<tr>
      <td style="color:var(--text-muted);font-family:'JetBrains Mono',monospace">${e.id}</td>
      <td>${e.geography}</td>
      <td>${e.age}</td>
      <td style="font-family:'JetBrains Mono',monospace">${e.credit_score}</td>
      <td style="font-family:'JetBrains Mono',monospace">€${e.balance.toLocaleString()}</td>
      <td><span class="pill ${pillClass}">${isChurn ? '⚠' : '✓'} ${e.label}</span></td>
      <td style="font-family:'JetBrains Mono',monospace;font-weight:700">${(e.churn_prob * 100).toFixed(1)}%</td>
      <td style="color:${riskColor};font-weight:700;font-size:0.82rem">${e.risk_level}</td>
      <td style="color:var(--text-muted);font-size:0.82rem">${e.timestamp}</td>
    </tr>`;
  }).join('');
}

document.getElementById('history-clear').addEventListener('click', () => {
  predictionHistory = [];
  sessionStorage.removeItem('churn_history');
  renderHistory();
  showToast('info', '🗑️ History cleared');
});

// Initial render on page load
renderHistory();

/* ── Session stats from API ─────────────────────────────────────────────── */
async function updateSessionStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('stat-total').textContent    = data.total_predictions;
    document.getElementById('stat-churn').textContent    = data.churn_count;
    document.getElementById('stat-retained').textContent = data.retained_count;
    document.getElementById('stat-churn-pct').textContent    = `${data.churn_rate_pct}% rate`;
    const retainRate = data.total_predictions > 0
      ? (100 - data.churn_rate_pct).toFixed(2)
      : 0;
    document.getElementById('stat-retained-pct').textContent = `${retainRate}% rate`;
  } catch (_) { /* silent */ }
}

/* ── Health check ───────────────────────────────────────────────────────── */
async function checkHealth() {
  const dot  = document.getElementById('status-dot');
  const text = document.getElementById('status-text');
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    const ok = data.model_loaded && data.status === 'healthy';
    dot.className  = `status-dot${ok ? '' : ' offline'}`;
    text.textContent = ok ? 'API Online' : 'Model Degraded';
  } catch {
    dot.className  = 'status-dot offline';
    text.textContent = 'API Offline';
  }
}

/* ── Feature importance bars ────────────────────────────────────────────── */
function renderFeatureImportances() {
  const container = document.getElementById('feat-bar-list');
  const maxVal = Math.max(...FEATURE_IMPORTANCES.map(f => f.value));

  container.innerHTML = FEATURE_IMPORTANCES
    .sort((a, b) => b.value - a.value)
    .map(f => {
      const pct = ((f.value / maxVal) * 100).toFixed(1);
      const displayPct = (f.value * 100).toFixed(1);
      return `
      <div class="feat-bar-row">
        <span class="feat-name">${f.name}</span>
        <div class="feat-bar-track">
          <div class="feat-bar-fill" data-pct="${pct}"></div>
        </div>
        <span class="feat-pct">${displayPct}%</span>
      </div>`;
    }).join('');

  // Animate fills
  setTimeout(() => {
    container.querySelectorAll('.feat-bar-fill').forEach(el => {
      el.style.width = `${el.dataset.pct}%`;
    });
  }, 100);
}

// Animate feature bars when model tab is opened
document.getElementById('nav-model').addEventListener('click', () => {
  renderFeatureImportances();
});

/* ── Toast notifications ────────────────────────────────────────────────── */
function showToast(type, message) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toastIn 0.3s ease reverse forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ── Boot ───────────────────────────────────────────────────────────────── */
checkHealth();
updateSessionStats();

// Also re-check health every 30s
setInterval(checkHealth, 30_000);
