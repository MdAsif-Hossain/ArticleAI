/* =============================================
   ArticleAI — Frontend Logic
   ============================================= */

const API_URL = window.location.origin + '/api';
// Fallback if serving index.html directly from file system:
// const API_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM refs ──
    const form           = document.getElementById('analyze-form');
    const submitBtn      = document.getElementById('submit-btn');
    const newBtn         = document.getElementById('new-btn');
    const inputSection   = document.getElementById('input-section');
    const statusSection  = document.getElementById('status-section');
    const resultsSection = document.getElementById('results-section');
    const summaryEl      = document.getElementById('summary-content');
    const insightsEl     = document.getElementById('insights-content');

    let stepTimer = null;   // progress simulation interval
    let pollTimer = null;   // status polling interval

    // ── Submit Form ──
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const url   = document.getElementById('url').value.trim();

        if (!email || !url) {
            showToast('Please fill in all fields.', 'error');
            return;
        }

        try {
            setBtnLoading(true);

            const res = await fetch(`${API_URL}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, article_url: url }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Server returned an error.');
            }

            const data = await res.json();

            // Transition UI
            inputSection.classList.add('hidden');
            statusSection.classList.remove('hidden');

            // Start visual step simulation + polling
            simulateSteps();
            startPolling(data.session_id);

        } catch (err) {
            showToast(err.message, 'error');
            setBtnLoading(false);
        }
    });

    // ── "Analyze Another" button ──
    newBtn.addEventListener('click', resetUI);

    // ────────────────────────────────────────────
    // Polling
    // ────────────────────────────────────────────
    function startPolling(sessionId) {
        pollTimer = setInterval(async () => {
            try {
                const res  = await fetch(`${API_URL}/status/${sessionId}`);
                const data = await res.json();

                if (data.status === 'completed') {
                    clearTimers();
                    markAllStepsComplete();
                    setTimeout(() => showResults(data.summary, data.insights), 900);
                } else if (data.status === 'error') {
                    clearTimers();
                    showToast(data.error || 'Processing failed.', 'error');
                    resetUI();
                }
            } catch (e) {
                console.error('Poll error:', e);
            }
        }, 2500);
    }

    // ────────────────────────────────────────────
    // Visual step simulation
    // ────────────────────────────────────────────
    function simulateSteps() {
        const ids = ['step-scrape', 'step-ai', 'step-save', 'step-email'];
        let idx = 0;

        // Activate first step immediately
        activate(ids[idx]);
        idx++;

        stepTimer = setInterval(() => {
            // Complete previous
            complete(ids[idx - 1]);

            if (idx < ids.length) {
                activate(ids[idx]);
                idx++;
            } else {
                clearInterval(stepTimer);
                stepTimer = null;
            }
        }, 3500);
    }

    function activate(id) {
        const el = document.getElementById(id);
        if (el) { el.classList.add('active'); el.classList.remove('completed'); }
    }

    function complete(id) {
        const el = document.getElementById(id);
        if (el) { el.classList.remove('active'); el.classList.add('completed'); }
    }

    function markAllStepsComplete() {
        document.querySelectorAll('.step').forEach(s => {
            s.classList.remove('active');
            s.classList.add('completed');
        });
    }

    // ────────────────────────────────────────────
    // Results rendering
    // ────────────────────────────────────────────
    function showResults(summary, insights) {
        statusSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Summary
        summaryEl.innerHTML = `<p>${escapeHtml(summary || 'No summary available.')}</p>`;

        // Insights
        if (Array.isArray(insights) && insights.length) {
            insightsEl.innerHTML = insights
                .map(i => `<li>${escapeHtml(i)}</li>`)
                .join('');
        } else {
            insightsEl.innerHTML = `<li>${escapeHtml(String(insights || 'No insights extracted.'))}</li>`;
        }

        showToast('Analysis complete!', 'success');
    }

    // ────────────────────────────────────────────
    // UI helpers
    // ────────────────────────────────────────────
    function setBtnLoading(on) {
        submitBtn.disabled = on;
        submitBtn.innerHTML = on
            ? '<span>Starting workflow…</span><i class="ph ph-circle-notch ph-spin"></i>'
            : '<span>Analyze Article</span><i class="ph ph-arrow-right"></i>';
    }

    function resetUI() {
        clearTimers();
        setBtnLoading(false);
        inputSection.classList.remove('hidden');
        statusSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        // Reset step classes
        document.querySelectorAll('.step').forEach(s => {
            s.classList.remove('active', 'completed');
        });
    }

    function clearTimers() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        if (stepTimer) { clearInterval(stepTimer); stepTimer = null; }
    }

    // ── Toast ──
    let toastTimeout = null;
    function showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const msg   = document.getElementById('toast-msg');

        if (toastTimeout) clearTimeout(toastTimeout);

        toast.className = `toast visible ${type}`;
        msg.textContent = message;

        toastTimeout = setTimeout(() => {
            toast.className = 'toast';
        }, 4500);
    }

    // ── XSS helper ──
    function escapeHtml(str) {
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }
});
