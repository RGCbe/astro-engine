// TAMIL ASTROLOGY STRUCTURED DATASETS
// Based on Classical Texts: Jataka Alankaram & KP Systems

// 1. NAKSHATRA PADA TO LETTER MAPPING (For Namakarana / Baby Naming)
// Each Nakshatra has 4 Padas (Quarters). The sounds match the specific quarter.
const NAKSHATRA_LETTERS = {
    "Ashwini": ["Chu", "Che", "Cho", "La"],
    "Bharani": ["Li", "Lu", "Le", "Lo"],
    "Krittika": ["A", "I", "U", "E"],
    "Rohini": ["O", "Va", "Vi", "Vu"],
    "Mrigashira": ["Ve", "Vo", "Ka", "Ki"],
    "Ardra": ["Ku", "Gha", "Ng", "Chha"],
    "Punarvasu": ["Ke", "Ko", "Ha", "Hi"],
    "Pushya": ["Hu", "He", "Ho", "Da"],
    "Ashlesha": ["Di", "Du", "De", "Do"],
    "Magha": ["Ma", "Mi", "Mu", "Me"],
    "Purva Phalguni": ["Mo", "Ta", "Ti", "Tu"],
    "Uttara Phalguni": ["Te", "To", "Pa", "Pi"],
    "Hasta": ["Pu", "Sha", "Na", "Tha"],
    "Chitra": ["Pe", "Po", "Ra", "Ri"],
    "Swati": ["Ru", "Re", "Ro", "Ta"],
    "Vishakha": ["Ti", "Tu", "Te", "To"],
    "Anuradha": ["Na", "Ni", "Nu", "Ne"],
    "Jyeshtha": ["No", "Ya", "Yi", "Yu"],
    "Mula": ["Ye", "Yo", "Bha", "Bhi"],
    "Purva Ashadha": ["Bhu", "Dha", "Bha", "Dha"],
    "Uttara Ashadha": ["Bhe", "Bho", "Ja", "Ji"],
    "Shravana": ["Ju", "Je", "Jo", "Gha"],
    "Dhanishta": ["Ga", "Gi", "Gu", "Ge"],
    "Shatabhisha": ["Go", "Sa", "Si", "Su"],
    "Purva Bhadrapada": ["Se", "So", "Da", "Di"],
    "Uttara Bhadrapada": ["Du", "Tha", "Jha", "Da"],
    "Revati": ["De", "Do", "Cha", "Chi"]
};

// 2. 10 PORUTHAM (MARRIAGE MATCHING RULES)
// The 10 core Tamil compatibility metrics based on Girl & Boy's Nakshatra
const DASHA_PORUTHAM_RULES = {
    "Dina": { target: "Health and Longevity", logic: "Count from Girl's Star to Boy's Star. 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26 are highly auspicious (Uthamam)." },
    "Gana": { target: "Temperament Match", types: {"Deva": "Divine", "Manushya": "Human", "Rakshasa": "Demonic"}, logic: "Deva + Deva = Best. Rakshasa + Rakshasa = Good. Deva + Rakshasa = Avoid." },
    "Mahendra": { target: "Progeny & Wealth", logic: "Count from Girl to Boy. 4, 7, 10, 13, 16, 19, 22, 25 are indicators of strong progeny." },
    "Stree Deergha": { target: "Prosperity of Female", logic: "Boy's star should ideally be > 13 stars away from the Girl's star." },
    "Yoni": { target: "Sexual Compatibility", logic: "Based on animal associations of Nakshatras (e.g., Ashwini = Horse, Bharani = Elephant). Enemies (Cat/Mouse, Lion/Elephant) are rejected." },
    "Rasi": { target: "Lineage & Future generation", logic: "Boy's Rasi should be > 6 houses away from Girl's Rasi ideally." },
    "Rasiyathipathi": { target: "Friendship among Lords", logic: "The Planetary lords of their Rasis must be natural friends (e.g., Sun & Jupiter) and not enemies (e.g., Sun & Saturn)." },
    "Vasiya": { target: "Mutual Attraction", logic: "Specific predetermined Rasi pairs (e.g., Mesham w/ Simmam/Viruchigam) exert magnetic attraction." },
    "Rajju": { target: "Husband's Longevity (Most Critical)", types: ["Sira", "Kanda", "Nabhi", "Kati", "Pada"], logic: "Girl and Boy MUST NOT have Nakshatras belonging to the same Rajju part. If they do, it is a fatal Rajju Dosha." },
    "Vedhai": { target: "Affliction Check", logic: "Certain stars inherently afflict each other (e.g., Ashwini vs Jyeshtha). They must not match afflicted pairs." }
};

// 3. KP SUB-LORD STRUCTURE (Krishnamurti Paddhati)
// Generating the first few entries of the 249 sub-lords mapping (Planet -> Star Lord -> Sub Lord)
const KP_SUB_LORDS_SAMPLE = [
    { span: [0.00, 0.46], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Ketu" },
    { span: [0.46, 3.00], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Venus" },
    { span: [3.00, 3.40], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Sun" },
    { span: [3.40, 4.46], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Moon" },
    { span: [4.46, 5.33], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Mars" },
    { span: [5.33, 7.33], rasi: "Aries", sign_lord: "Mars", star_lord: "Ketu", sub_lord: "Rahu" },
    //... This goes mathematically up to 249 divisions (360 degrees divided proportionally by Vimshottari Dasa years)
];

// 4. VIMSHOTTARI DASHA TIMINGS (120 Year Cycle)
const VIMSHOTTARI_DASHA = {
    "Ketu": { years: 7, ruling_stars: ["Ashwini", "Magha", "Mula"] },
    "Venus": { years: 20, ruling_stars: ["Bharani", "Purva Phalguni", "Purva Ashadha"] },
    "Sun": { years: 6, ruling_stars: ["Krittika", "Uttara Phalguni", "Uttara Ashadha"] },
    "Moon": { years: 10, ruling_stars: ["Rohini", "Hasta", "Shravana"] },
    "Mars": { years: 7, ruling_stars: ["Mrigashira", "Chitra", "Dhanishta"] },
    "Rahu": { years: 18, ruling_stars: ["Ardra", "Swati", "Shatabhisha"] },
    "Jupiter": { years: 16, ruling_stars: ["Punarvasu", "Vishakha", "Purva Bhadrapada"] },
    "Saturn": { years: 19, ruling_stars: ["Pushya", "Anuradha", "Uttara Bhadrapada"] },
    "Mercury": { years: 17, ruling_stars: ["Ashlesha", "Jyeshtha", "Revati"] }
};
