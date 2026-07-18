document.addEventListener('DOMContentLoaded', () => {
    initStars();
    initModal();
});

function initStars() {
    const starContainer = document.getElementById('star-container');
    const starCount = 150;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // Randomize size, position, and animation duration
        const size = Math.random() * 3 + 1;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const duration = Math.random() * 3 + 2;
        const delay = Math.random() * 5;

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${posX}vw`;
        star.style.top = `${posY}vh`;
        star.style.animationDuration = `${duration}s`;
        star.style.animationDelay = `${delay}s`;

        starContainer.appendChild(star);
    }
}

function initModal() {
    const modal = document.getElementById('chart-modal');
    const closeBtn = document.getElementById('close-modal');
    const forms = document.querySelectorAll('.dynamic-form');
    const modalTitle = document.getElementById('dynamic-modal-title');

    function openModal(title, formId) {
        modalTitle.innerText = title;
        forms.forEach(f => f.classList.add('hidden'));
        document.getElementById(formId).classList.remove('hidden');
        modal.classList.remove('hidden');
    }

    // Bind Services
    document.getElementById('btn-jathagam').addEventListener('click', () => openModal('Jathagam Details', 'natal-form'));
    document.getElementById('btn-nadi').addEventListener('click', () => openModal('Nadi Thumbprint', 'nadi-form'));
    document.getElementById('btn-prasannam').addEventListener('click', () => openModal('Ask Prasannam', 'prasannam-form'));
    document.getElementById('btn-numerology').addEventListener('click', () => openModal('En Kanitham (Numerology)', 'numerology-form'));

    // Close logic
    closeBtn.addEventListener('click', () => { modal.classList.add('hidden'); });
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    // Handle Jathagam submit
    const natalForm = document.getElementById('natal-form');
    const submitBtn = natalForm.querySelector('.submit-btn');

    natalForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const dob = document.getElementById('dob').value;
        const time = document.getElementById('time').value;
        const lat = parseFloat(document.getElementById('lat').value);
        const lon = parseFloat(document.getElementById('lon').value);
        const focusSelect = document.getElementById('focus');
        const focus = focusSelect.value;
        const focusLabel = focusSelect.options[focusSelect.selectedIndex].text;

        if (!dob || !time) return;

        const [year, month, day] = dob.split('-').map(Number);
        
        const payload = {
            year,
            month,
            day,
            time,
            lat,
            lon,
            focus
        };

        try {
            submitBtn.textContent = 'Consulting the Stars...';
            submitBtn.disabled = true;

            const response = await fetch('http://localhost:8000/api/jathagam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Failed to compute Jathagam');
            }

            const data = await response.json();
            
            const title = `${data.janma_rasi} (${data.janma_rasi_tamil})`;
            const focusHtml = focus !== 'general' ? `<br><br><span style="color:#d4af37; font-size:1.1rem; text-transform:uppercase; letter-spacing: 2px;">Your Prashna: ${focusLabel}</span>` : "";
            
            const desc = `Your Lagna is <b>${data.lagnam}</b>. Nakshatra: <b>${data.janma_nakshatra}</b>. ${data.rasi_description}`;
            
            // Build the complete body
            let fullDesc = desc + focusHtml;
            
            // Render Dashas
            fullDesc += `<div style="margin-top: 20px; padding: 15px; border-left: 3px solid #d4af37; background: rgba(212,175,55,0.05);">
                <h3 style="color: #d4af37; margin-bottom: 10px;">Time Cycles (Phase II Dasha Engine)</h3>
                <p style="margin-bottom: 5px; color: #eee;"><b>Current Vimshottari Maha Dasha:</b> ${data.current_dasha} (${data.dasha_years} years)<br><i style="font-size: 0.9em; opacity: 0.8;">${data.dasha_meaning}</i></p>
                <p style="color: #eee;"><b>Current Yogini Dasha:</b> ${data.current_yogini_dasha} (Lord: ${data.current_yogini_lord})</p>
            </div>`;
            
            // Render Yogas
            if (data.detected_yogas && data.detected_yogas.length > 0) {
                let yogaHtml = `<div style="margin-top: 20px; padding: 15px; border: 1px solid #d4af37; border-radius: 8px; background: rgba(0,0,0,0.5);">
                    <h3 style="color: #d4af37; margin-bottom: 15px; text-align: center; border-bottom: 1px dashed rgba(212,175,55,0.3); padding-bottom: 10px;">Phase III: Detected Yogas</h3>`;
                
                data.detected_yogas.forEach(yoga => {
                    let color = yoga.valence === 'GOOD' ? '#4CAF50' : (yoga.valence === 'BAD' ? '#F44336' : '#FFEB3B');
                    let icon = yoga.valence === 'GOOD' ? '⭐' : (yoga.valence === 'BAD' ? '⚠️' : '⚡');
                    yogaHtml += `
                    <div style="margin-bottom: 15px;">
                        <h4 style="color: ${color}; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;">
                            ${icon} ${yoga.name} <span style="font-size: 0.7em; padding: 2px 6px; border: 1px solid ${color}; border-radius: 4px; opacity: 0.8;">${yoga.strength}</span>
                        </h4>
                        <p style="margin-bottom: 5px; font-size: 0.95em; color: #e0e0e0; line-height: 1.4;">${yoga.description}</p>
                        <p style="font-size: 0.85em; color: #aaa; font-style: italic;"><b>Remedy/Action:</b> ${yoga.remedy}</p>
                    </div>`;
                });
                yogaHtml += `</div>`;
                fullDesc += yogaHtml;
            }
            
            // Render Evaluator Layer results
            if (data.advanced_reading_html) {
                fullDesc += `<div style="margin-top: 30px; text-align: left; padding: 20px; background: rgba(0,0,0,0.4); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                    <h2 style="color: white; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px;">Phase IV Evaluator Synthesis</h2>
                    ${data.advanced_reading_html}
                </div>`;
            }
            
            showResults(`Vanakkam, ${name}`, title, fullDesc);
        } catch (error) {
            console.error(error);
            showResults(`Vanakkam, ${name}`, 'Error', 'The cosmos are clouded. Please try again.');
        } finally {
            submitBtn.textContent = 'Read Jathagam';
            submitBtn.disabled = false;
        }
    });

    // Handle Nadi submit (Thumbprint)
    const thumbScanner = document.getElementById('thumb-scanner');
    thumbScanner.addEventListener('click', () => {
        thumbScanner.style.background = 'rgba(212, 175, 55, 0.4)'; // Gold flash
        setTimeout(() => { thumbScanner.style.background = ''; }, 300);
    });

    document.getElementById('nadi-form').addEventListener('submit', (e) => {
        e.preventDefault();
        showResults('Ancient Leaves Found', 'Kandam 1', 'Your palm leaf indicates great spiritual awakening and incoming wealth.');
    });

    // Handle Prasannam submit
    document.getElementById('prasannam-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const question = document.getElementById('question').value;
        const answers = ["Yes, the timing is highly auspicious.", "Patience. The stars favor waiting.", "Obstacles are present, but determination will overcome them."];
        const answer = answers[Math.floor(Math.random() * answers.length)];
        showResults('Prasannam Insight', 'Answer Revealed', answer);
    });

    // Handle Numerology submit
    document.getElementById('numerology-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const dob = document.getElementById('num-dob').value;
        const name = document.getElementById('num-name').value;
        const dobNumbers = dob.replace(/-/g, '');
        let destinyNum = 0;
        for (let char of dobNumbers) {
            destinyNum += parseInt(char);
        }
        while (destinyNum > 9) {
            let sum = 0;
            for (let char of destinyNum.toString()) {
                sum += parseInt(char);
            }
            destinyNum = sum;
        }
        showResults(`Numerology for ${name}`, `Destiny Number: ${destinyNum}`, `Number ${destinyNum} commands strong planetary energy and spiritual alignment.`);
    });

    function showResults(greeting, title, desc) {
        document.getElementById('results-greeting').innerHTML = greeting;
        document.getElementById('zodiac-sign').innerHTML = title;
        document.getElementById('zodiac-desc').innerHTML = desc;
        
        modal.classList.add('hidden');
        document.getElementById('hero-section').classList.add('hidden');
        document.getElementById('results-section').classList.remove('hidden');
        
        forms.forEach(f => f.reset());
    }

    const resetBtn = document.getElementById('reset-btn');
    if(resetBtn) {
        resetBtn.addEventListener('click', () => {
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('hero-section').classList.remove('hidden');
        });
    }
}

function getRasiData(month, day) {
    // Note: True Rasi (Moon Sign) requires ephemeris data. 
    // This is an approximate mapping to Tamil Sun Signs (Madham) for demonstration.
    const signs = [
        { name: "Makaram (Capricorn)", startM: 1, startD: 15, endM: 2, endD: 12, desc: "Disciplined, Ambitious, Patient" },
        { name: "Kumbam (Aquarius)", startM: 2, startD: 13, endM: 3, endD: 14, desc: "Progressive, Humanitarian, Independent" },
        { name: "Meenam (Pisces)", startM: 3, startD: 15, endM: 4, endD: 13, desc: "Compassionate, Intuitive, Artistic" },
        { name: "Mesham (Aries)", startM: 4, startD: 14, endM: 5, endD: 14, desc: "Courageous, Energetic, Natural Leader" },
        { name: "Rishabam (Taurus)", startM: 5, startD: 15, endM: 6, endD: 14, desc: "Reliable, Patient, Grounded" },
        { name: "Mithunam (Gemini)", startM: 6, startD: 15, endM: 7, endD: 16, desc: "Versatile, Expressive, Curious" },
        { name: "Kadagam (Cancer)", startM: 7, startD: 17, endM: 8, endD: 16, desc: "Nurturing, Intuitive, Protective" },
        { name: "Simmam (Leo)", startM: 8, startD: 17, endM: 9, endD: 16, desc: "Charismatic, Confident, Generous" },
        { name: "Kanni (Virgo)", startM: 9, startD: 17, endM: 10, endD: 17, desc: "Analytical, Practical, Diligent" },
        { name: "Thulaam (Libra)", startM: 10, startD: 18, endM: 11, endD: 16, desc: "Diplomatic, Harmonious, Charming" },
        { name: "Viruchigam (Scorpio)", startM: 11, startD: 17, endM: 12, endD: 15, desc: "Passionate, Resourceful, Intense" },
        { name: "Dhanusu (Sagittarius)", startM: 12, startD: 16, endM: 1, endD: 14, desc: "Optimistic, Adventurous, Philosophical" }
    ];

    for (let sign of signs) {
        if ((month === sign.startM && day >= sign.startD) || (month === sign.endM && day <= sign.endD)) {
            return sign;
        }
    }
    // Handle wrap-around for Dhanusu/Makaram edge cases
    return (month === 1) ? signs[11] : signs[0];
}
