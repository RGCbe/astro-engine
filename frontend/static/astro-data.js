// This file acts as our "Digital Astrology Book" containing information scraped and translated from traditional Vedic & Tamil astrology texts.

const ASTRO_DATABASE = {
    rasis: {
        "Mesham": { english: "Aries", ruler: "Mars (Chevvai)", element: "Fire", description: "Aggressive, independent, and fiercely protective. Born leaders with boundless energy." },
        "Rishabam": { english: "Taurus", ruler: "Venus (Sukran)", element: "Earth", description: "Steadfast, artistic, and deeply connected to material and aesthetic pleasures." },
        "Mithunam": { english: "Gemini", ruler: "Mercury (Budhan)", element: "Air", description: "Charming communicators with dual natures. Highly adaptable and intellectual." },
        "Kadagam": { english: "Cancer", ruler: "Moon (Chandran)", element: "Water", description: "Highly emotional, intuitive, and deeply attached to family and home." },
        "Simmam": { english: "Leo", ruler: "Sun (Suriyan)", element: "Fire", description: "Regal, confident, and generous. They command attention naturally." },
        "Kanni": { english: "Virgo", ruler: "Mercury (Budhan)", element: "Earth", description: "Analytical, pure-hearted, and incredibly detail-oriented problem solvers." },
        "Thulaam": { english: "Libra", ruler: "Venus (Sukran)", element: "Air", description: "Diplomatic seekers of justice. They balance scales and thrive in partnerships." },
        "Viruchigam": { english: "Scorpio", ruler: "Mars (Chevvai)", element: "Water", description: "Intense, secretive, and powerful. They undergo massive life transformations." },
        "Dhanusu": { english: "Sagittarius", ruler: "Jupiter (Guru)", element: "Fire", description: "Philosophical travelers seeking higher truth, spirituality, and luck." },
        "Makaram": { english: "Capricorn", ruler: "Saturn (Sani)", element: "Earth", description: "Disciplined, karmic workers who slowly but surely reach the pinnacle of success." },
        "Kumbam": { english: "Aquarius", ruler: "Saturn (Sani)", element: "Air", description: "Eccentric, humanitarian, and highly logical. They think decades ahead of others." },
        "Meenam": { english: "Pisces", ruler: "Jupiter (Guru)", element: "Water", description: "Mystics of the zodiac. deeply compassionate, artistic, and spiritually evolved." }
    },

    nakshatras: [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ],

    grahas: {
        "Suriyan": { english: "Sun", rules: "Soul, Ego, Father, Authority" },
        "Chandran": { english: "Moon", rules: "Mind, Emotions, Mother, Peace" },
        "Chevvai": { english: "Mars", rules: "Courage, Siblings, Real Estate, Energy" },
        "Budhan": { english: "Mercury", rules: "Intellect, Business, Communication, Education" },
        "Guru": { english: "Jupiter", rules: "Wealth, Wisdom, Children, Fortune" },
        "Sukran": { english: "Venus", rules: "Romance, Luxuries, Arts, Vehicle" },
        "Sani": { english: "Saturn", rules: "Karma, Longevity, Discipline, Labor" },
        "Rahu": { english: "North Node", rules: "Desire, Illusion, Foreign Lands, Technology" },
        "Ketu": { english: "South Node", rules: "Detachment, Spirituality, Moksha, Intuition" }
    },

    bhavas: {
        "1st House": "Self, Physical Body, Personality",
        "2nd House": "Wealth, Family, Speech",
        "3rd House": "Courage, Younger Siblings, Short Journeys",
        "4th House": "Mother, Vehicles, Happiness, Property",
        "5th House": "Intellect, Romance, Children, Speculation",
        "6th House": "Debts, Diseases, Enemies, Service",
        "7th House": "Marriage, Partnerships, Business dealings",
        "8th House": "Longevity, Occult, Sudden Gains/Losses",
        "9th House": "Dharma, Father, Fortune, Higher Education",
        "10th House": "Karma, Career, Fame, Social Standing",
        "11th House": "Gains, Income, Elder Siblings, Networks",
        "12th House": "Losses, Spirituality, Foreign Settlement, Moksha"
    }
};
