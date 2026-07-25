let currentBrand = 'Všechny';
let currentReportId = null;
let currentHtmlSnippet = '';

document.addEventListener('DOMContentLoaded', () => {
    fetchBrands();
    fetchDevices();
    fetchReports();
    loadSettings();
});

// Tab Switcher
function switchTab(tabId, el) {
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    el.classList.add('active');

    if (tabId === 'tab-history') {
        fetchReports();
    }
}

// Fetch Brands
async function fetchBrands() {
    try {
        const res = await fetch('/api/brands');
        const brands = await res.json();

        const container = document.getElementById('brands-row');
        container.innerHTML = `
            <div class="brand-pill ${currentBrand === 'Všechny' ? 'active' : ''}" onclick="selectBrand('Všechny')">
                <div class="b-name">Všechny značky</div>
                <div class="b-count">Všechny modely</div>
            </div>
        `;

        brands.forEach(b => {
            container.innerHTML += `
                <div class="brand-pill ${currentBrand === b.name ? 'active' : ''}" onclick="selectBrand('${b.name}')">
                    <div class="b-name">${b.name}</div>
                    <div class="b-count">${b.total} modelů</div>
                </div>
            `;
        });
    } catch (e) {
        console.error("Chyba při načítání značek:", e);
    }
}

function selectBrand(brandName) {
    currentBrand = brandName;
    fetchBrands();
    fetchDevices();
}

function resetFilters() {
    currentBrand = 'Všechny';
    document.getElementById('search-input').value = '';
    fetchBrands();
    fetchDevices();
}

// Fetch Devices
async function fetchDevices() {
    const search = document.getElementById('search-input').value.trim();
    let url = `/api/devices?brand=${encodeURIComponent(currentBrand)}&search=${encodeURIComponent(search)}`;

    try {
        const res = await fetch(url);
        const devices = await res.json();

        const grid = document.getElementById('devices-grid');
        grid.innerHTML = '';

        if (devices.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">Žádná zařízení neodpovídají zadaným kritériím.</div>`;
            return;
        }

        devices.forEach(d => {
            const isEol = d.is_eol;
            const statusClass = isEol ? 'status-eol' : 'status-active';
            const statusText = isEol ? 'EOL (Ukončeno)' : 'Aktivní podpora';

            grid.innerHTML += `
                <div class="device-card">
                    <div>
                        <div class="card-top">
                            <span class="brand-badge">${d.brand}</span>
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </div>
                        <div class="device-name">${d.model}</div>
                    </div>
                    <div>
                        <div class="info-row">
                            <span>Konec podpory OS:</span>
                            <span class="val">${d.os_support_end || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span>Bezpečnostní záplaty do:</span>
                            <span class="val">${d.security_support_end || 'N/A'}</span>
                        </div>
                        <div class="info-row" style="margin-top: 10px; font-size: 0.75rem;">
                            <span>Zdroj:</span>
                            <span class="val" style="color: #64748b;">${d.source}</span>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (e) {
        console.error("Chyba při načítání zařízení:", e);
    }
}

// Fetch Reports History
async function fetchReports() {
    try {
        const res = await fetch('/api/reports');
        const reports = await res.json();

        const list = document.getElementById('reports-list');
        list.innerHTML = '';

        if (reports.length === 0) {
            list.innerHTML = `<div style="padding: 20px; color: var(--text-muted);">Zatím nebyl spuštěn žádný report.</div>`;
            return;
        }

        reports.forEach((r, idx) => {
            const activeClass = idx === 0 ? 'active' : '';
            list.innerHTML += `
                <div class="report-item ${activeClass}" onclick="selectReport(${r.id}, this)">
                    <div class="time">Report #${r.id} (${r.timestamp})</div>
                    <div class="summary">${r.summary_text}</div>
                </div>
            `;
        });

        if (reports.length > 0 && currentReportId === null) {
            selectReport(reports[0].id, list.querySelector('.report-item'));
        }
    } catch (e) {
        console.error("Chyba při načítání reportů:", e);
    }
}

// Select Report Detail & Generate HTML snippet
async function selectReport(reportId, el) {
    currentReportId = reportId;
    document.querySelectorAll('.report-item').forEach(i => i.classList.remove('active'));
    if (el) el.classList.add('active');

    try {
        const res = await fetch(`/api/reports/${reportId}`);
        const data = await res.json();

        document.getElementById('report-detail-title').innerText = `Detail kontroly #${reportId}`;
        const container = document.getElementById('changes-container');
        container.innerHTML = '';

        if (data.changes.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted);">V této kontrole nebyly zjištěny žádné změny.</p>`;
            document.getElementById('html-box').style.display = 'block';
            currentHtmlSnippet = data.html_snippet;
            document.getElementById('html-snippet-code').innerText = currentHtmlSnippet;
            return;
        }

        let html = '';

        if (data.added && data.added.length > 0) {
            html += `<h4 style="color: #34d399; margin: 15px 0 10px 0;">➕ Nově přidána zařízení (${data.added.length})</h4>`;
            data.added.forEach(c => {
                html += `
                    <div style="background: #0f172a; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #10b981;">
                        <strong>${c.brand} ${c.model}</strong><br>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">${c.new_value}</span>
                    </div>
                `;
            });
        }

        if (data.changed && data.changed.length > 0) {
            html += `<h4 style="color: #60a5fa; margin: 15px 0 10px 0;">🔄 Změny v cyklech / stavu (${data.changed.length})</h4>`;
            data.changed.forEach(c => {
                html += `
                    <div style="background: #0f172a; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #3b82f6;">
                        <strong>${c.brand} ${c.model}</strong><br>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">${c.old_value} → <b>${c.new_value}</b></span>
                    </div>
                `;
            });
        }

        if (data.removed && data.removed.length > 0) {
            html += `<h4 style="color: #f87171; margin: 15px 0 10px 0;">❌ Odebraná zařízení / Konce podpory (EOL) (${data.removed.length})</h4>`;
            data.removed.forEach(c => {
                html += `
                    <div style="background: #0f172a; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444;">
                        <strong>${c.brand} ${c.model}</strong><br>
                        <span style="font-size: 0.85rem; color: var(--text-muted);">${c.old_value} (Podpora ukončena / Odebráno)</span>
                    </div>
                `;
            });
        }

        container.innerHTML = html;
        currentHtmlSnippet = data.html_snippet;
        document.getElementById('html-snippet-code').innerText = currentHtmlSnippet;
        document.getElementById('html-box').style.display = 'block';

    } catch (e) {
        console.error("Chyba při načítání detailu reportu:", e);
    }
}

// Copy HTML Snippet to Clipboard
function copyHtmlSnippet() {
    if (!currentHtmlSnippet) return;
    navigator.clipboard.writeText(currentHtmlSnippet).then(() => {
        alert("HTML report (UL/LI) byl zkopírován do schránky!");
    }).catch(err => {
        alert("Chyba při kopírování: " + err);
    });
}

// Trigger Manual Check
async function runCheckNow() {
    const btn = document.getElementById('btn-check-now');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳ Probíhá kontrola...</span>';

    try {
        const res = await fetch('/api/check', { method: 'POST' });
        const data = await res.json();
        alert(data.summary);
        fetchBrands();
        fetchDevices();
        fetchReports();
    } catch (e) {
        alert("Chyba při provádění kontroly: " + e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>⚡ Spustit kontrolu nyní</span>';
    }
}

// Gmail Preset Helper
function applyGmailPresets() {
    document.getElementById('smtp_host').value = 'smtp.gmail.com';
    document.getElementById('smtp_port').value = '587';
    alert("Přednastavení pro Gmail aplikováno! Nyní zadejte Váš e-mail a Heslo aplikace (App Password).");
}

// Load Settings
async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const settings = await res.json();

        for (const [k, v] of Object.entries(settings)) {
            const el = document.getElementById(k);
            if (el) {
                if (el.type === 'checkbox') {
                    el.checked = v === '1';
                } else {
                    el.value = v;
                }
            }
        }
    } catch (e) {
        console.error("Chyba při načítání nastavení:", e);
    }
}

// Save Settings
async function saveSettings(e) {
    e.preventDefault();
    const data = {
        smtp_host: document.getElementById('smtp_host').value.trim(),
        smtp_port: document.getElementById('smtp_port').value.trim(),
        smtp_user: document.getElementById('smtp_user').value.trim(),
        smtp_password: document.getElementById('smtp_password').value,
        recipient_email: document.getElementById('recipient_email').value.trim(),
        auto_send_email: document.getElementById('auto_send_email').checked ? '1' : '0',
        smtp_use_tls: '1'
    };

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            alert("Nastavení bylo úspěšně uloženo!");
        }
    } catch (err) {
        alert("Chyba při ukládání nastavení: " + err);
    }
}

// Test Email
async function testEmail() {
    try {
        const res = await fetch('/api/test-email', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert("Testovací e-mail byl úspěšně odoslán!");
        } else {
            alert("Odeslání e-mailu selhalo: " + data.message);
        }
    } catch (e) {
        alert("Chyba: " + e);
    }
}
