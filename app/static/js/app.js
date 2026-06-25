/* ═══════════════════════════════════════════════════════════
   FINTRACK  –  app.js
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Chart.js global defaults ──────────────────────────── */
  if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.color       = '#94A3B8';
  }

  /* ── 1. SIDEBAR COLLAPSE ───────────────────────────────── */
  const shell   = document.getElementById('ftShell');
  const toggle  = document.getElementById('ftToggle');
  const sidebar = document.getElementById('ftSidebar');

  if (shell && toggle) {
    const KEY = 'ft_sidebar_collapsed';
    if (localStorage.getItem(KEY) === '1') shell.classList.add('ft-collapsed');

    toggle.addEventListener('click', () => {
      shell.classList.toggle('ft-collapsed');
      localStorage.setItem(KEY, shell.classList.contains('ft-collapsed') ? '1' : '0');
    });
  }

  /* ── 2. MOBILE SIDEBAR OVERLAY ─────────────────────────── */
  if (window.innerWidth <= 768 && sidebar) {
    const overlay = document.createElement('div');
    overlay.style.cssText =
      'position:fixed;inset:0;background:rgba(0,0,0,0.65);z-index:199;' +
      'display:none;backdrop-filter:blur(3px)';
    document.body.appendChild(overlay);

    const menuBtn = document.createElement('button');
    menuBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
           viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6"  x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>`;
    menuBtn.style.cssText =
      'position:fixed;top:12px;left:14px;z-index:201;' +
      'background:rgba(22,31,46,0.95);border:1px solid rgba(255,255,255,0.1);' +
      'color:#94A3B8;border-radius:9px;width:36px;height:36px;' +
      'display:flex;align-items:center;justify-content:center;' +
      'cursor:pointer;backdrop-filter:blur(12px);';
    document.body.appendChild(menuBtn);

    const openSidebar  = () => { sidebar.classList.add('ft-mobile-open');    overlay.style.display = 'block'; };
    const closeSidebar = () => { sidebar.classList.remove('ft-mobile-open'); overlay.style.display = 'none'; };
    menuBtn.addEventListener('click', openSidebar);
    overlay.addEventListener('click', closeSidebar);
  }

  /* ── 3. ANIMATED COUNTERS ──────────────────────────────── */
  function animateCounter(el) {
    const raw    = el.dataset.target || el.textContent.trim();
    const num    = parseFloat(raw.replace(/[^0-9.]/g, ''));
    const prefix = raw.match(/^[^\d]*/)?.[0] || '';
    if (!num || isNaN(num)) return;
    const dur = 1400;
    let start = null;
    const step = ts => {
      if (!start) start = ts;
      const p    = Math.min((ts - start) / dur, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent =
        prefix + (ease * num).toLocaleString('en-IN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* Animate hero amounts */
  ['heroNetWorth', 'heroInvested', 'heroSavings'].forEach(id => {
    const el = document.getElementById(id);
    if (el) animateCounter(el);
  });

  /* Animate KPI values */
  document.querySelectorAll('.ft-kpi-val[data-target]').forEach(animateCounter);

  /* ── 4. SPARKLINES (KPI cards) ─────────────────────────── */
  const sparks = [
    { id: 'sp0', color: '#10B981', data: [42,58,50,72,65,84,76,92] },
    { id: 'sp1', color: '#F43F5E', data: [60,48,65,54,72,58,68,55] },
    { id: 'sp2', color: '#0EA5E9', data: [30,42,36,58,52,68,62,80] },
    { id: 'sp3', color: '#F59E0B', data: [22,38,30,48,58,52,68,76] },
  ];


  sparks.forEach(({ id, color, data }) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.map(() => ''),
        datasets: [{
          data,
          borderColor: color,
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          backgroundColor: ctx => {
            const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 44);
            g.addColorStop(0, color + '44');
            g.addColorStop(1, color + '00');
            return g;
          },
          tension: 0.45,
        }],
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: { x: { display: false }, y: { display: false } },
        animation: { duration: 1000, easing: 'easeInOutQuart' },
      },
    });
  });

  /* ── 5. HERO SPARKLINE ─────────────────────────────────── */
  const heroCanvas = document.getElementById('heroSparkChart');
  if (heroCanvas) {
    const heroColor = '#10B981';
    const labels = window._ft?.chartLabels || ['Jan','Feb','Mar','Apr','May','Jun'];
    const incomeValues = window._ft?.incomeValues || [0,0,0,0,0,0];
    const expenseTrend = window._ft?.expenseTrend || [0,0,0,0,0,0];
    const heroData = incomeValues.map((v, i) => Math.max((v || 0) - (expenseTrend[i] || 0), 0));
    new Chart(heroCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data: heroData.some(Boolean) ? heroData : [0,0,0,0,0,0],
          borderColor: heroColor,
          borderWidth: 2.5,
          pointRadius: 0,
          fill: true,
          backgroundColor: ctx => {
            const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 80);
            g.addColorStop(0, heroColor + '50');
            g.addColorStop(1, heroColor + '00');
            return g;
          },
          tension: 0.45,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: { x: { display: false }, y: { display: false } },
        animation: { duration: 1200, easing: 'easeInOutQuart' },
      },
    });
  }

  /* ── 6. TREND CHART (Income vs Expenses + Savings line) ── */
  const trendCanvas = document.getElementById('trendChart');
  if (trendCanvas && typeof window._ft !== 'undefined') {
    const { incomeValues, expenseTrend, chartLabels } = window._ft;
    const MONTHS = chartLabels || ['Jan','Feb','Mar','Apr','May','Jun'];

    const savingsData = (incomeValues || [0,0,0,0,0,0]).map(
      (v, i) => Math.max((v || 0) - ((expenseTrend || [])[i] || 0), 0)
    );

    const barGrad = (ctx, color) => {
      const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 280);
      g.addColorStop(0, color + 'dd');
      g.addColorStop(1, color + '22');
      return g;
    };

    const trendChart = new Chart(trendCanvas, {
      type: 'bar',
      data: {
        labels: MONTHS,
        datasets: [
          {
            label: 'Income',
            type: 'bar',
            data: incomeValues || [0,0,0,0,0,0],
            backgroundColor: ctx => barGrad(ctx, '#10B981'),
            borderRadius: 8,
            borderSkipped: false,
            borderWidth: 0,
            order: 2,
          },
          {
            label: 'Expenses',
            type: 'bar',
            data: expenseTrend || [0,0,0,0,0,0],
            backgroundColor: ctx => barGrad(ctx, '#F43F5E'),
            borderRadius: 8,
            borderSkipped: false,
            borderWidth: 0,
            order: 2,
          },
          {
            label: 'Savings',
            type: 'line',
            data: savingsData,
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59,130,246,0.08)',
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#3B82F6',
            pointBorderColor: '#0f172a',
            pointBorderWidth: 2,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.4,
            order: 1,
            yAxisID: 'y',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0D1E2D',
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            padding: 12,
            titleColor: '#94A3B8',
            bodyColor: '#E2E8F0',
            bodySpacing: 6,
            callbacks: {
              label: ctx => {
                const v = ctx.parsed.y;
                return ` ${ctx.dataset.label}: ₹${v >= 1000 ? (v/1000).toFixed(1)+'k' : v.toFixed(0)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { font: { size: 11 }, color: '#64748B' },
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: {
              font: { size: 11 },
              color: '#64748B',
              callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v),
            },
          },
        },
        animation: { duration: 1200, easing: 'easeInOutQuart' },
      },
    });

    /* Period tabs */
    document.querySelectorAll('.ft-tab[data-chart-period]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.ft-tab').forEach(b => b.classList.remove('ft-tab-active'));
        btn.classList.add('ft-tab-active');
        const n = { '6m': 6, '3m': 3, '1m': 1 }[btn.dataset.chartPeriod] || 6;
        const inc = (incomeValues  || []).slice(-n);
        const exp = (expenseTrend  || []).slice(-n);
        trendChart.data.labels           = MONTHS.slice(-n);
        trendChart.data.datasets[0].data = inc;
        trendChart.data.datasets[1].data = exp;
        trendChart.data.datasets[2].data = inc.map((v, i) => Math.max(v - (exp[i] || 0), 0));
        trendChart.update();
      });
    });
  }

  /* ── 7. DOUGHNUT CHART ─────────────────────────────────── */
  const donutCanvas = document.getElementById('donutChart');
  if (donutCanvas && typeof window._ft !== 'undefined') {
    const { expenseLabels, expenseValues, totalExpRaw } = window._ft;
    const PALETTE = [
      '#10B981','#F43F5E','#0EA5E9','#F59E0B',
      '#34D399','#A78BFA','#FB923C','#6EE7B7','#38BDF8',
    ];

    /* Update center total */
    const centerVal = document.getElementById('donutTotalVal');
    if (centerVal) centerVal.textContent = totalExpRaw || '—';

    const donut = new Chart(donutCanvas, {
      type: 'doughnut',
      data: {
        labels: expenseLabels || [],
        datasets: [{
          data: expenseValues || [],
          backgroundColor: PALETTE,
          borderWidth: 0,
          hoverOffset: 10,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0D1E2D',
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            padding: 12,
            callbacks: {
              label: ctx => {
                const value = ctx.parsed;
                return ` ${ctx.label}: ₹${value >= 1000 ? (value/1000).toFixed(1)+'k' : value.toFixed(0)}`;
              },
            },
          },
        },
        animation: { animateRotate: true, duration: 1200, easing: 'easeInOutQuart' },
      },
    });

    /* Render custom legend */
    const legendEl = document.getElementById('donutLegend');
    if (legendEl && expenseLabels && expenseValues) {
      const total = expenseValues.reduce((a, b) => a + b, 0);
      legendEl.innerHTML = expenseLabels.map((label, i) => {
        if (!expenseValues[i]) return '';
        const pct = total ? ((expenseValues[i] / total) * 100).toFixed(1) : 0;
        return `
          <div class="ft-donut-legend-item">
            <div class="ft-dl-left">
              <span class="ft-dl-dot" style="background:${PALETTE[i] || '#6366F1'}"></span>
              ${label}
            </div>
            <span class="ft-dl-val">${pct}%</span>
          </div>`;
      }).join('');
    }
  }

  /* ── 8. AI FINANCIAL INSIGHTS ──────────────────────────── */
  const INSIGHTS = [
    {
      icon: 'trending-down',
      iconBg: 'rgba(244,63,94,0.12)',
      iconColor: '#fb7185',
      type: 'Spending Alert',
      typeColor: '#f87171',
      body: 'Your dining expenses are 32% higher than last month. Consider setting a stricter Food budget.',
      action: 'Set Budget',
      href: '/budgets',
    },
    {
      icon: 'piggy-bank',
      iconBg: 'rgba(16,185,129,0.12)',
      iconColor: '#10B981',
      type: 'Savings Tip',
      typeColor: '#22C55E',
      body: 'You could save ₹4,200 more this month by reducing Entertainment by 20%.',
      action: 'View Expenses',
      href: '/expenses',
    },
    {
      icon: 'bar-chart-2',
      iconBg: 'rgba(14,165,233,0.12)',
      iconColor: '#38bdf8',
      type: 'Investment',
      typeColor: '#818CF8',
      body: 'Your portfolio grew 9.3% this quarter. Consider diversifying into Index Funds for stability.',
      action: 'View Portfolio',
      href: '/investments',
    },
    {
      icon: 'alert-triangle',
      iconBg: 'rgba(245,158,11,0.12)',
      iconColor: '#F59E0B',

      type: 'Budget Alert',
      typeColor: '#F59E0B',
      body: 'Travel budget is at 82% with 14 days remaining this month.',
      action: 'Manage Budget',
      href: '/budgets',
    },
  ];

  function renderInsights() {
    const grid = document.getElementById('insightsGrid');
    if (!grid) return;
    grid.innerHTML = INSIGHTS.map(ins => `
      <div class="ft-insight-item">
        <div class="ft-insight-icon-row">
          <div class="ft-insight-icon" style="background:${ins.iconBg};color:${ins.iconColor}">
            <i data-lucide="${ins.icon}" class="w-4 h-4"></i>
          </div>
          <span class="ft-insight-type" style="color:${ins.typeColor}">${ins.type}</span>
        </div>
        <p class="ft-insight-body">${ins.body}</p>
        <a href="${ins.href}" class="ft-insight-action">
          ${ins.action} <i data-lucide="arrow-right" class="w-3 h-3"></i>
        </a>
      </div>`).join('');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  renderInsights();

  const refreshBtn = document.getElementById('refreshInsights');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshBtn.style.opacity = '0.5';
      setTimeout(() => {
        renderInsights();
        refreshBtn.style.opacity = '1';
      }, 600);
    });
  }

  /* ── 9. TRANSACTION FILTER TABS ────────────────────────── */
  document.querySelectorAll('.ft-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.ft-txn-filters')
         .querySelectorAll('.ft-filter-btn')
         .forEach(b => b.classList.remove('ft-filter-active'));
      btn.classList.add('ft-filter-active');
    });
  });

/* The Expenses page form submit and row-delete handlers live in the
   page-specific inline script in expenses.html. They are intentionally
   not duplicated here because binding them in both places caused
   duplicate add and delete requests. */

   });