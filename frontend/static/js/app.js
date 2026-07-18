document.addEventListener('DOMContentLoaded', () => {
    const birthForm = document.getElementById('birth-form');
    const inputSection = document.getElementById('input-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const progressFill = document.querySelector('.progress-fill');
    const langSelect = document.getElementById('lang-select');
    const downloadBtn = document.getElementById('download-pdf-btn');
    
    const API_BASE = window.location.origin || 'http://127.0.0.1:8000';

    const apiKeyInput = document.getElementById('api-key');
    if (apiKeyInput) {
        const savedKey = sessionStorage.getItem('atro_api_key');
        if (savedKey) apiKeyInput.value = savedKey;
        apiKeyInput.addEventListener('change', () => {
            const v = apiKeyInput.value.trim();
            if (v) sessionStorage.setItem('atro_api_key', v);
            else sessionStorage.removeItem('atro_api_key');
        });
    }

    function getApiKey() {
        const el = document.getElementById('api-key');
        return (el && el.value.trim()) || sessionStorage.getItem('atro_api_key') || '';
    }

    function withApiKey(payload) {
        const key = getApiKey();
        if (key) payload.api_key = key;
        return payload;
    }

    const UI_TRANSLATIONS = {
        "en": {
            "title": "Calculate Your Destiny",
            "subtitle": "Enter your birth details for a high-fidelity multi-book analysis.",
            "dob": "Birth Date",
            "tob": "Birth Time",
            "lat": "Latitude",
            "lon": "Longitude",
            "focus": "Focus Area",
            "focus_general": "General Life",
            "focus_career": "Career & Success",
            "focus_relationship": "Marriage & Love",
            "focus_health": "Health & Vitality",
            "init_btn": "Initialize Engine",
            "executive_summary": "Executive Summary",
            "panchangam": "Panchangam",
            "lbl_tithi": "Tithi",
            "lbl_vara": "Vara",
            "lbl_paksha": "Paksha",
            "current_dasha": "Current Dasha",
            "badge_ai": "AI SYNTHESIS",
            "yogas": "Detected Yogas",
            "rules": "Planetary Interpretations",
            "timeline": "120-Year Council of Masters Timeline",
            "download_btn": "📥 Download PDF Report",
            "new_chart_btn": "New Chart"
        },
        "ta": {
            "title": "உங்கள் விதியை கணக்கிடுங்கள்",
            "subtitle": "உங்கள் பிறந்த விவரங்களை உள்ளிட்டு ஆழ்ந்த பகுப்பாய்வைப் பெறுங்கள்.",
            "dob": "பிறந்த தேதி",
            "tob": "பிறந்த நேரம்",
            "lat": "அட்ச ரேகை (Latitude)",
            "lon": "தீர்க்க ரேகை (Longitude)",
            "focus": "கவனிக்க வேண்டிய துறை",
            "focus_general": "பொது வாழ்க்கை",
            "focus_career": "தொழில் மற்றும் வெற்றி",
            "focus_relationship": "திருமணம் மற்றும் காதல்",
            "focus_health": "ஆரோக்கியம் மற்றும் வீரியம்",
            "init_btn": "ஜாதகத்தை கணிக்குக",
            "executive_summary": "நிர்வாக சுருக்கம்",
            "panchangam": "பஞ்சாங்கம்",
            "lbl_tithi": "திதி",
            "lbl_vara": "வாரம்",
            "lbl_paksha": "பக்ஷம்",
            "current_dasha": "தற்போதைய தசை",
            "badge_ai": "செயற்கை நுண்ணறிவு தொகுப்பு",
            "yogas": "கண்டறியப்பட்ட யோகங்கள்",
            "rules": "கிரக நிலைகளின் பலன்கள்",
            "timeline": "120 வருட காலவரிசை",
            "download_btn": "📥 PDF அறிக்கை பதிவிறக்கம்",
            "new_chart_btn": "புதிய ஜாதகம்"
        },
        "hi": {
            "title": "अपने भाग्य की गणना करें",
            "subtitle": "गहन विश्लेषण के लिए अपने जन्म का विवरण दर्ज करें।",
            "dob": "जन्म तिथि",
            "tob": "जन्म समय",
            "lat": "अक्षांश (Latitude)",
            "lon": "रेखांश (Longitude)",
            "focus": "मुख्य क्षेत्र",
            "focus_general": "सामान्य जीवन",
            "focus_career": "करियर और सफलता",
            "focus_relationship": "विवाह और प्रेम",
            "focus_health": "स्वास्थ्य और जीवन शक्ति",
            "init_btn": "कुंडली प्रारंभ करें",
            "executive_summary": "कार्यकारी सारांश",
            "panchangam": "पंचांग",
            "lbl_tithi": "तिथि",
            "lbl_vara": "वार",
            "lbl_paksha": "पक्ष",
            "current_dasha": "वर्तमान दशा",
            "badge_ai": "एआई संश्लेषण",
            "yogas": "कुंडली में उपस्थित योग",
            "rules": "ग्रहों का फल",
            "timeline": "120-वर्षीय जीवन कालक्रम",
            "download_btn": "📥 PDF रिपोर्ट डाउनलोड करें",
            "new_chart_btn": "नई कुंडली"
        }
    };

    function applyUITranslations(lang) {
        const trans = UI_TRANSLATIONS[lang] || UI_TRANSLATIONS["en"];
        document.querySelectorAll('[data-ui]').forEach(el => {
            const key = el.getAttribute('data-ui');
            if (trans[key]) {
                if (key === 'title') {
                    const highlight = lang === 'ta' ? 'விதியை' : (lang === 'hi' ? 'भाग्य' : 'Destiny');
                    el.innerHTML = trans[key].replace(highlight, `<span class="gold-gradient">${highlight}</span>`);
                } else {
                    el.textContent = trans[key];
                }
            }
        });
    }

    // Handle language change
    langSelect.addEventListener('change', (e) => {
        applyUITranslations(e.target.value);
    });

    birthForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const lang = langSelect.value;
        const formData = withApiKey({
            year: parseInt(document.getElementById('dob').value.split('-')[0]),
            month: parseInt(document.getElementById('dob').value.split('-')[1]),
            day: parseInt(document.getElementById('dob').value.split('-')[2]),
            time: document.getElementById('tob').value,
            lat: parseFloat(document.getElementById('lat').value),
            lon: parseFloat(document.getElementById('lon').value),
            focus: document.getElementById('focus').value,
            lang: lang
        });

        // Transition to loading
        inputSection.classList.remove('active');
        loadingSection.classList.add('active');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 95) progress = 95;
            progressFill.style.width = `${progress}%`;
        }, 400);

        try {
            const response = await fetch(`${API_BASE}/api/book-battle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Engine Timeout or Error');
            
            const data = await response.json();
            clearInterval(interval);
            progressFill.style.width = '100%';
            
            setTimeout(() => {
                renderDashboard(data.full_data);
                renderTimeline(data.battle_results);
                if (data.truth?.disclaimer || data.full_data?.truth?.disclaimer) {
                    const note = document.getElementById('truth-notice');
                    if (note) note.textContent = data.truth?.disclaimer || data.full_data.truth.disclaimer;
                }
                loadingSection.classList.remove('active');
                resultSection.classList.add('active');
            }, 500);

        } catch (error) {
            alert('Error: ' + error.message);
            loadingSection.classList.remove('active');
            inputSection.classList.add('active');
            clearInterval(interval);
        }
    });

    function renderDashboard(data) {
        const lang = langSelect.value;
        
        // Identity & Panchangam
        document.getElementById('lagna-initial').textContent = data.lagnam.charAt(0);
        
        const lagnamSuffix = lang === 'ta' ? ' லக்னம்' : (lang === 'hi' ? ' लग्न' : ' Ascendant');
        document.getElementById('lagna-name').textContent = `${data.lagnam}${lagnamSuffix}`;
        
        const nakSuffix = lang === 'ta' ? ' நட்சத்திரம்' : (lang === 'hi' ? ' नक्षत्र' : ' Nakshatra');
        document.getElementById('nakshatra-name').textContent = `${data.janma_nakshatra}${nakSuffix}`;
        
        document.getElementById('tithi-val').textContent = data.panchangam.tithi;
        document.getElementById('vara-val').textContent = data.panchangam.vara;
        
        const isShukla = data.panchangam.tithi.includes('Shukla') || 
                        data.panchangam.tithi.includes('சுக்ல') || 
                        data.panchangam.tithi.includes('शुक्ल');
        document.getElementById('paksha-val').textContent = isShukla ? 
            (lang === 'ta' ? 'வளர்பிறை (சுக்லபக்ஷம்)' : (lang === 'hi' ? 'शुक्ल पक्ष' : 'Shukla')) : 
            (lang === 'ta' ? 'தேய்பிறை (கிருஷ்ணபக்ஷம்)' : (lang === 'hi' ? 'कृष्ण पक्ष' : 'Krishna'));

        // Dasha
        document.getElementById('curr-maha').textContent = data.current_dasha;
        document.getElementById('curr-antar').textContent = data.current_antardasha;
        document.getElementById('dasha-end-val').textContent = data.current_antardasha_end || data.dasha_end;

        // Synthesis
        document.getElementById('synthesis-text').textContent = data.synthesis.short_summary;
        document.getElementById('advice-text').textContent = data.synthesis.action_advice;

        // Yogas
        const yogaContainer = document.getElementById('yoga-container');
        yogaContainer.innerHTML = '';
        data.detected_yogas.forEach(yoga => {
            const card = document.createElement('div');
            card.className = 'yoga-card';
            card.innerHTML = `
                <h4>${yoga.name}</h4>
                <p>${yoga.description.substring(0, 80)}...</p>
                <small class="gold">${yoga.strength}% ${lang === 'ta' ? 'வலிமை' : (lang === 'hi' ? 'प्रबलता' : 'Strength')}</small>
            `;
            card.onclick = () => showModal(yoga.name, yoga.description + (yoga.remedy ? '<br><br><b>Remedy:</b> ' + yoga.remedy : ''));
            yogaContainer.appendChild(card);
        });

        // Rule Feed
        const ruleFeed = document.getElementById('rules-feed');
        ruleFeed.innerHTML = '';
        
        // Display rules by planet in house
        data.house_predictions.forEach(reading => {
            if (reading.status === 'locked') {
                const block = document.createElement('div');
                block.className = 'rule-block locked';
                block.innerHTML = `<h3>${lang === 'ta' ? 'வீடு' : (lang === 'hi' ? 'भाव' : 'House')} ${reading.house}</h3><p class="rule-text" style="color:#888;">${reading.message || 'Locked — upgrade to Pro.'}</p>`;
                ruleFeed.appendChild(block);
                return;
            }
            const block = document.createElement('div');
            block.className = 'rule-block';
            
            let rulesHtml = '';
            if (reading.corpus_rules && reading.corpus_rules.length > 0) {
                reading.corpus_rules.slice(0, 3).forEach(r => {
                    rulesHtml += `
                        <div class="rule-item">
                            <p class="rule-text">${r.text}</p>
                            <p class="rule-source">— ${r.source}</p>
                        </div>
                    `;
                });
            } else {
                rulesHtml = `<p class="rule-text" style="color: #666; font-style: italic;">${lang === 'ta' ? 'தனித்துவமான விதிகள் எதுவும் கிடைக்கவில்லை.' : (lang === 'hi' ? 'कोई विशिष्ट नियम नहीं मिले।' : 'No specific classical rules found.')}</p>`;
            }

            let conjunction = reading.conjunction_with && reading.conjunction_with.length > 0 
                ? ` (${lang === 'ta' ? 'இணைவு' : (lang === 'hi' ? 'युति' : 'Conjunct')}: ${reading.conjunction_with.join(', ')})`
                : '';

            const houseLabel = lang === 'ta' ? 'வீடு' : (lang === 'hi' ? 'भाव' : 'House');
            block.innerHTML = `
                <h3>${reading.planet} - ${houseLabel} ${reading.house}: ${reading.rasi}${conjunction}</h3>
                ${rulesHtml}
            `;
            ruleFeed.appendChild(block);
        });
    }

    // Modal logic
    const modal = document.getElementById('corpus-modal');
    const closeModal = document.querySelector('.close-modal');

    function showModal(title, body) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = body;
        modal.style.display = 'block';
    }

    closeModal.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

    // "New Chart" button
    document.getElementById('new-reading-btn').addEventListener('click', () => {
        resultSection.classList.remove('active');
        inputSection.classList.add('active');
    });

    // "Download PDF" button click handler
    downloadBtn.addEventListener('click', async () => {
        const dob = document.getElementById('dob').value;
        const tob = document.getElementById('tob').value;
        const lat = parseFloat(document.getElementById('lat').value);
        const lon = parseFloat(document.getElementById('lon').value);
        const focus = document.getElementById('focus').value;
        const lang = langSelect.value;

        if (!dob || !tob) {
            alert(lang === 'ta' ? 'தயவுசெய்து பிறந்த விவரங்களை முதலில் உள்ளிடவும்.' : (lang === 'hi' ? 'कृपया पहले जन्म विवरण दर्ज करें।' : 'Please enter birth details first.'));
            return;
        }

        const payload = withApiKey({
            year: parseInt(dob.split('-')[0]),
            month: parseInt(dob.split('-')[1]),
            day: parseInt(dob.split('-')[2]),
            time: tob,
            lat: lat,
            lon: lon,
            focus: focus,
            lang: lang
        });

        try {
            downloadBtn.disabled = true;
            const origHTML = downloadBtn.innerHTML;
            downloadBtn.innerHTML = `<span>⏳ ${lang === 'ta' ? 'பதிவிறக்கம் செய்யப்படுகிறது...' : (lang === 'hi' ? 'डाउनलोड हो रहा है...' : 'Generating PDF...')}</span>`;

            const response = await fetch(`${API_BASE}/api/download-pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('PDF Generation Failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `AtroVeda_Report_${lang.toUpperCase()}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            downloadBtn.innerHTML = origHTML;
            downloadBtn.disabled = false;
        } catch (error) {
            alert('Error downloading PDF: ' + error.message);
            downloadBtn.innerHTML = `<span>📥 ${lang === 'ta' ? 'PDF அறிக்கை பதிவிறக்கம்' : (lang === 'hi' ? 'PDF रिपोर्ट डाउनलोड करें' : 'Download PDF Report')}</span>`;
            downloadBtn.disabled = false;
        }
    });

    function renderTimeline(battleResults) {
        const timelineFeed = document.getElementById('timeline-feed');
        timelineFeed.innerHTML = '';
        
        for (const [subject, report] of Object.entries(battleResults)) {
            if (!subject.includes('Dasha Timing') && !subject.includes('Antardasha Timing') && !subject.includes('Maha Dasha')) continue;
            
            const node = document.createElement('div');
            node.className = 'timeline-node';
            
            let statusClass = 'mixed';
            if (report.consensus.status.includes('Auspicious')) statusClass = 'auspicious';
            else if (report.consensus.status.includes('Inauspicious')) statusClass = 'inauspicious';

            let rulesHtml = '';
            report.top_rules.forEach(r => {
                rulesHtml += `
                    <div class="rule-item">
                        <p class="rule-text">${r.text}</p>
                        <p class="rule-source">— ${r.books.join(', ')}</p>
                    </div>
                `;
            });

            node.innerHTML = `
                <h4>${subject}</h4>
                <div class="timeline-consensus ${statusClass}">
                    ${report.consensus.status} (${report.consensus.consensus_percent}%)
                </div>
                <div class="timeline-rules">
                    ${rulesHtml || '<p class="rule-text" style="color:#666;">No explicit corpus rule matching.</p>'}
                </div>
            `;
            timelineFeed.appendChild(node);
        }
    }
});
