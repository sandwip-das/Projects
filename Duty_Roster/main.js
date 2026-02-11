
// DOM Elements
const appContent = document.getElementById('app-content');
// Desktop Elements
const yearDisplay = document.getElementById('current-year-display');
const prevBtn = document.getElementById('prev-year');
const nextBtn = document.getElementById('next-year');
const tabInt = document.getElementById('tab-international');
const tabDom = document.getElementById('tab-domestic');

// Mobile Elements
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const mobileYearDisplay = document.getElementById('mobile-year-display');
const mobilePrevBtn = document.getElementById('mobile-prev-year');
const mobileNextBtn = document.getElementById('mobile-next-year');
const mobileTabInt = document.getElementById('mobile-tab-international');
const mobileTabDom = document.getElementById('mobile-tab-domestic');
const themeToggle = document.getElementById('theme-toggle');
const iconSun = document.getElementById('icon-sun');
const iconMoon = document.getElementById('icon-moon');

const mobileThemeToggle = document.getElementById('mobile-theme-toggle');
const mobileThemeText = document.getElementById('mobile-theme-text');
const mobileIconSun = document.getElementById('mobile-icon-sun');
const mobileIconMoon = document.getElementById('mobile-icon-moon');

// State
let currentYear = new Date().getFullYear();
let currentTab = 'international';
let isDarkMode = false;
const monthsShort = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

// --- Roster Logic ---
function getInternationalRoster(year) {
    const initialOffsets = { 'A': 0, 'B': 2, 'C': 4, 'D': 6 };
    const rows = [];
    for (let r = 0; r < 32; r++) {
        const rowData = {
            index: r,
            M: '', E: '', N: '', O: '',
            months: {},
        };
        const cycleState = r % 8;
        for (const [sName, startOff] of Object.entries(initialOffsets)) {
            const sState = (startOff + cycleState) % 8;
            if ([0, 1].includes(sState)) rowData.M = sName;
            else if ([2, 3].includes(sState)) rowData.E = sName;
            else if ([4, 5].includes(sState)) rowData.N = sName;
            else if ([6, 7].includes(sState)) rowData.O = sName;
        }
        rows.push(rowData);
    }
    const refDate = new Date(2025, 11, 31);
    refDate.setHours(12, 0, 0, 0);
    const startDate = new Date(year, 0, 1);
    startDate.setHours(12, 0, 0, 0);
    const endDate = new Date(year, 11, 31);
    endDate.setHours(12, 0, 0, 0);
    let current = new Date(startDate);

    while (current <= endDate) {
        const diffTime = current - refDate;
        const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
        let rowIdx = (6 + diffDays) % 32;
        if (rowIdx < 0) rowIdx += 32;
        const mIdx = current.getMonth() + 1;
        const day = current.getDate();
        const dayName = current.toLocaleDateString('en-US', { weekday: 'short' });
        const yy = current.getFullYear().toString().slice(-2);
        const dd = String(day).padStart(2, '0');
        const fmtDate = `${dd} ${dayName}-${yy}`;
        const fullDate = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        if (!rows[rowIdx].months[mIdx]) {
            rows[rowIdx].months[mIdx] = { text: fmtDate, fullDate: fullDate, day: day };
        }
        current.setDate(current.getDate() + 1);
    }
    return rows;
}

function getDomesticRoster(year) {
    const rosterRows = [];
    const refDate = new Date(2025, 11, 31);
    refDate.setHours(12, 0, 0, 0);
    for (let dayNum = 1; dayNum <= 31; dayNum++) {
        const row = { dayNum: dayNum, months: {} };
        for (let m = 1; m <= 12; m++) {
            const d = new Date(year, m - 1, dayNum);
            d.setHours(12, 0, 0, 0);
            if (d.getMonth() !== (m - 1)) { row.months[m] = null; continue; }
            const diffTime = d - refDate;
            const deltaDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
            let cycleIdx = (deltaDays - 1) % 6;
            if (cycleIdx < 0) cycleIdx += 6;
            let mShift, eShift;
            if (cycleIdx >= 0 && cycleIdx < 3) { mShift = 'A'; eShift = 'B'; }
            else { mShift = 'B'; eShift = 'A'; }
            row.months[m] = {
                date: d, dayName: d.toLocaleDateString('en-US', { weekday: 'short' }),
                fullDate: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`,
                M: mShift, E: eShift
            };
        }
        rosterRows.push(row);
    }
    return rosterRows;
}

// --- Display Utils ---
function getLocalDateStr(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

function getActiveDutyDate() {
    const now = new Date();
    if (now.getHours() < 6) {
        now.setDate(now.getDate() - 1);
    }
    return getLocalDateStr(now);
}

function getTodayStr() {
    return getLocalDateStr(new Date());
}

// --- Render ---

// --- Render ---

// Tailwind Classes
// Fluid font size scaling from 0.4rem to 0.8rem
const TABLE_CLASSES = "w-full border-collapse text-[clamp(0.35rem,1.4vw,0.75rem)]";

// Fluid Scale for Headers
const TH_CLASSES = "bg-[#1cab9d] text-white font-bold uppercase border border-[#901647] whitespace-nowrap align-middle h-auto text-[inherit] p-[clamp(0px,0.3vw,2px)] shadow-md hover:scale-105 transition-transform duration-200 cursor-default";

// Fluid Scale for Data Cells
const TD_CLASSES = "text-black border border-[#901647] text-center whitespace-nowrap h-auto w-min min-w-0 align-middle text-[1em] leading-none py-[2px] px-0";

const TODAY_CLASSES = "bg-[#22c55e] font-bold !text-black"; // Unified highlight (Green)
// Dynamic Row Classes based on Mode
const ODD_ROW_LIGHT = "bg-[#d1fae5]"; // Mint
const EVEN_ROW_LIGHT = "bg-[#f3f4f6]"; // Gray
const ODD_ROW_DARK = "bg-[#1E293B]"; // First/Odd Rows
const EVEN_ROW_DARK = "bg-[#334155]"; // Second/Even Rows
const TEXT_LIGHT = "text-black font-normal";
const TEXT_DARK = "!text-white !font-light";

function renderInternational() {
    const rows = getInternationalRoster(currentYear);
    const todayStr = getTodayStr();
    const activeDutyDate = getActiveDutyDate();
    const currentHour = new Date().getHours();

    let html = `
        <table class="${TABLE_CLASSES}">
            <thead>
                <tr>
                    ${monthsShort.slice(0, 6).map(m => `<th class="${TH_CLASSES}">${m}</th>`).join('')}
                    <th class="${TH_CLASSES}">M</th>
                    <th class="${TH_CLASSES}">E</th>
                    <th class="${TH_CLASSES}">N</th>
                    <th class="${TH_CLASSES}">O</th>
                    ${monthsShort.slice(6, 12).map(m => `<th class="${TH_CLASSES}">${m}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
    `;

    rows.forEach((row, idx) => {
        let isActiveDutyRow = false;
        Object.values(row.months).forEach(m => { if (m && m.fullDate === activeDutyDate) isActiveDutyRow = true; });

        // Theme-based Classes
        const rowBgClass = isDarkMode ? ((idx % 2 === 0) ? ODD_ROW_DARK : EVEN_ROW_DARK) : ((idx % 2 === 0) ? ODD_ROW_LIGHT : EVEN_ROW_LIGHT);
        const textClass = isDarkMode ? TEXT_DARK : TEXT_LIGHT;

        html += `<tr class="${rowBgClass}">`;

        // Col 1-6
        for (let m = 1; m <= 6; m++) {
            const data = row.months[m];
            const isToday = data && data.fullDate === todayStr;
            const extraClasses = isToday ? TODAY_CLASSES : textClass;
            html += `<td class="${TD_CLASSES} ${extraClasses}">${data ? `<span>${data.text}</span>` : ''}</td>`;
        }

        // Shifts - Determine active state
        const hM = isActiveDutyRow && currentHour >= 6 && currentHour < 14;
        const hE = isActiveDutyRow && currentHour >= 14 && currentHour < 22;
        const hN = isActiveDutyRow && (currentHour >= 22 || currentHour < 6);

        html += `
            <td class="${TD_CLASSES} ${hM ? TODAY_CLASSES : textClass}">${row.M}</td>
            <td class="${TD_CLASSES} ${hE ? TODAY_CLASSES : textClass}">${row.E}</td>
            <td class="${TD_CLASSES} ${hN ? TODAY_CLASSES : textClass}">${row.N}</td>
            <td class="${TD_CLASSES} ${textClass}">${row.O}</td>
        `;

        // Col 7-12
        for (let m = 7; m <= 12; m++) {
            const data = row.months[m];
            const isToday = data && data.fullDate === todayStr;
            const extraClasses = isToday ? TODAY_CLASSES : textClass;
            html += `<td class="${TD_CLASSES} ${extraClasses}">${data ? `<span>${data.text}</span>` : ''}</td>`;
        }
        html += `</tr>`;
    });
    html += `</tbody></table>
    
    <div class="flex justify-center gap-2 md:gap-6 mt-[5px] animate-pulse-slow p-0 flex-wrap">
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-teal-500 shadow-[0_0_5px_rgba(20,184,166,0.6)]"></div> Morning (M): 06:00-14:00
        </div>
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.6)]"></div> Evening (E): 14:00-22:00
        </div>
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_5px_rgba(168,85,247,0.6)]"></div> Night (N): 22:00-06:00
        </div>
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-slate-500"></div> Off Day (O)
        </div>
    </div>`;
    appContent.innerHTML = html;
}

function renderDomestic() {
    const rows = getDomesticRoster(currentYear);
    const todayStr = getTodayStr();

    let html = `
        <table class="${TABLE_CLASSES}">
            <thead>
                <tr>
                    ${monthsShort.map(m => `<th class="${TH_CLASSES}" colspan="3">${m}</th>`).join('')}
                </tr>
                <tr>
                    ${monthsShort.map(() => `
                        <th class="${TH_CLASSES}">Date</th>
                        <th class="${TH_CLASSES}">M</th>
                        <th class="${TH_CLASSES}">E</th>
                    `).join('')}
                </tr>
            </thead>
            <tbody>
    `;
    rows.forEach((row, idx) => {
        // Theme-based Classes
        const rowBgClass = isDarkMode ? ((idx % 2 === 0) ? ODD_ROW_DARK : EVEN_ROW_DARK) : ((idx % 2 === 0) ? ODD_ROW_LIGHT : EVEN_ROW_LIGHT);
        const textClass = isDarkMode ? TEXT_DARK : TEXT_LIGHT;

        html += `<tr class="${rowBgClass}">`;
        for (let m = 1; m <= 12; m++) {
            const data = row.months[m];
            if (data) {
                const isToday = data.fullDate === todayStr;
                const currentHour = new Date().getHours();
                const isMorning = currentHour >= 6 && currentHour < 14;
                const isEvening = currentHour >= 14 && currentHour < 22;

                const mActive = isToday && isMorning;
                const eActive = isToday && isEvening;

                const dateClasses = isToday ? TODAY_CLASSES : textClass;

                html += `
                    <td class="${TD_CLASSES} ${dateClasses}">
                        <span>${String(row.dayNum).padStart(2, '0')}</span> <span>${data.dayName}</span>
                    </td>
                    <td class="${TD_CLASSES} ${mActive ? TODAY_CLASSES : textClass}">${data.M}</td>
                    <td class="${TD_CLASSES} ${eActive ? TODAY_CLASSES : textClass}">${data.E}</td>
                `;
            } else {
                html += `<td class="${TD_CLASSES}"></td><td class="${TD_CLASSES}"></td><td class="${TD_CLASSES}"></td>`;
            }
        }
        html += `</tr>`;
    });
    html += `</tbody></table>
    
    <div class="flex justify-center gap-2 md:gap-6 mt-[5px] animate-pulse-slow p-0 flex-wrap">
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-teal-500 shadow-[0_0_5px_rgba(20,184,166,0.6)]"></div> Morning (M)
        </div>
        <div class="flex items-center gap-2 text-[0.6rem] md:text-[0.8rem] font-bold text-slate-200 bg-white/5 px-3 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors cursor-default shadow-sm">
            <div class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.6)]"></div> Evening (E)
        </div>
    </div>`;
    appContent.innerHTML = html;
}

function updateUI() {
    yearDisplay.textContent = currentYear;
    if (mobileYearDisplay) mobileYearDisplay.textContent = currentYear;
    if (currentTab === 'international') renderInternational();
    else renderDomestic();
}
function updateTabs() {
    // Shared Button Base Style reflecting "Button" look
    const baseStyle = "font-bold cursor-pointer transition-all duration-300 border border-transparent rounded-full px-[clamp(0.6rem,2vw,1.2rem)] py-[clamp(0.2rem,1vw,0.4rem)] text-[clamp(0.6rem,1.5vw,0.8rem)] flex items-center justify-center shadow-md";

    // Active State: White background, colored text, strong shadow
    const activeStyle = `${baseStyle} bg-white text-teal-700 shadow-[0_0_15px_rgba(255,255,255,0.4)] scale-105`;

    // Inactive State: Semi-transparent background, white text, hover effect
    const inactiveStyle = `${baseStyle} bg-white/10 text-white/90 hover:bg-white/20 hover:text-white hover:border-white/30`;

    // Mobile Tab Styles
    const mobileActive = "bg-teal-600 text-white shadow-lg scale-[1.02]";
    const mobileInactive = "bg-white/5 text-slate-300 hover:bg-white/10";

    if (currentTab === 'international') {
        tabInt.className = activeStyle;
        tabDom.className = inactiveStyle;

        if (mobileTabInt) {
            mobileTabInt.className = `w-full font-bold py-2 rounded-lg text-center transition-all ${mobileActive}`;
            mobileTabDom.className = `w-full font-bold py-2 rounded-lg text-center transition-all ${mobileInactive}`;
        }
    } else {
        tabInt.className = inactiveStyle;
        tabDom.className = activeStyle;

        if (mobileTabInt) {
            mobileTabInt.className = `w-full font-bold py-2 rounded-lg text-center transition-all ${mobileInactive}`;
            mobileTabDom.className = `w-full font-bold py-2 rounded-lg text-center transition-all ${mobileActive}`;
        }
    }
}
prevBtn.addEventListener('click', () => { currentYear--; updateUI(); });
nextBtn.addEventListener('click', () => { currentYear++; updateUI(); });
tabInt.addEventListener('click', () => { currentTab = 'international'; updateTabs(); updateUI(); });
tabDom.addEventListener('click', () => { currentTab = 'domestic'; updateTabs(); updateUI(); });

// Mobile Listeners
if (mobilePrevBtn) mobilePrevBtn.addEventListener('click', () => { currentYear--; updateUI(); });
if (mobileNextBtn) mobileNextBtn.addEventListener('click', () => { currentYear++; updateUI(); });
if (mobileTabInt) mobileTabInt.addEventListener('click', () => {
    currentTab = 'international';
    updateTabs();
    updateUI();
    mobileMenu.classList.add('hidden'); // Close menu on selection
});
if (mobileTabDom) mobileTabDom.addEventListener('click', () => {
    currentTab = 'domestic';
    updateTabs();
    updateUI();
    mobileMenu.classList.add('hidden'); // Close menu on selection
});
if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    updateUI();

    // Desktop Toggle Logic (Rotation & Scale)
    if (isDarkMode) {
        // Sun: Rotate out & fade
        iconSun.classList.replace('rotate-0', 'rotate-[-90deg]');
        iconSun.classList.replace('opacity-100', 'opacity-0');
        iconSun.classList.replace('scale-100', 'scale-0');

        // Moon: Rotate in & show
        iconMoon.classList.replace('rotate-90', 'rotate-0');
        iconMoon.classList.replace('opacity-0', 'opacity-100');
        iconMoon.classList.replace('scale-0', 'scale-100');
    } else {
        // Sun: Rotate in & show
        iconSun.classList.replace('rotate-[-90deg]', 'rotate-0');
        iconSun.classList.replace('opacity-0', 'opacity-100');
        iconSun.classList.replace('scale-0', 'scale-100');

        // Moon: Rotate out & fade
        iconMoon.classList.replace('rotate-0', 'rotate-90');
        iconMoon.classList.replace('opacity-100', 'opacity-0');
        iconMoon.classList.replace('scale-100', 'scale-0');
    }

    // Mobile Toggle Logic
    if (mobileIconSun && mobileIconMoon) {
        if (isDarkMode) {
            mobileThemeText.textContent = "Switch into Light Mode";
            // Sun Out
            mobileIconSun.classList.replace('rotate-0', 'rotate-[-90deg]');
            mobileIconSun.classList.replace('opacity-100', 'opacity-0');
            mobileIconSun.classList.replace('scale-100', 'scale-0');
            // Moon In
            mobileIconMoon.classList.replace('rotate-90', 'rotate-0');
            mobileIconMoon.classList.replace('opacity-0', 'opacity-100');
            mobileIconMoon.classList.replace('scale-0', 'scale-100');
        } else {
            mobileThemeText.textContent = "Switch into Dark Mode";
            // Sun In
            mobileIconSun.classList.replace('rotate-[-90deg]', 'rotate-0');
            mobileIconSun.classList.replace('opacity-0', 'opacity-100');
            mobileIconSun.classList.replace('scale-0', 'scale-100');
            // Moon Out
            mobileIconMoon.classList.replace('rotate-0', 'rotate-90');
            mobileIconMoon.classList.replace('opacity-100', 'opacity-0');
            mobileIconMoon.classList.replace('scale-100', 'scale-0');
        }
    }
}

if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
if (mobileThemeToggle) mobileThemeToggle.addEventListener('click', () => {
    toggleTheme();
    mobileMenu.classList.add('hidden');
});

// Init
document.getElementById('footer-year').textContent = new Date().getFullYear();
const mFooterYear = document.getElementById('mobile-footer-year');
if (mFooterYear) mFooterYear.textContent = new Date().getFullYear();
updateUI();
updateTabs();
