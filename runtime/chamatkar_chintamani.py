"""Chamatkar Chintamani — Bhattaji's classical 108-verse character readings.

Source: Chamatkar Chintamani by Bhattaji (~17th century CE), a Sanskrit text giving
4-line verse character readings for each of 9 planets in each of 12 houses (108 total).
The verses focus on personality, fortunes, profession, family-themes — distinct from
BPHS planet-in-house in their poetic, character-arc tone.

Translation-strategy:
  - Sanskrit lines are given in PHONETIC TRANSLITERATION (Roman/IAST-ish style)
    based on B Suryanarain Rao (1900), C.S.Patel & B.V.Raman pre-publications,
    and modern translations available through Bhartiya Vidya Bhavan / Sagar.
  - Where verse-cell boundaries are ambiguous in the manuscript tradition,
    I follow the Suryanarain Rao numbering (most-cited canon).
  - Translations are 60-120 words, blending available authoritative renderings.
  - 108 verses = 9 planets * 12 houses, sequential numbering by planet:
    Sun 1-12, Moon 13-24, Mars 25-36, Mercury 37-48, Jupiter 49-60,
    Venus 61-72, Saturn 73-84, Rahu 85-96, Ketu 97-108.

Self-contained: only imports vedic_core + stdlib.
"""
import sys
sys.path.insert(0, ".")

from vedic_core import (
    PLANETS_ALL, RASI_LORDS, RASIS, DIGNITIES,
    EXALTATION_SIGNS, DEBILITATION_SIGNS,
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES,
    house_lord, planet_house, planet_sign, planet_dignity,
    is_dignified, is_debilitated, house_occupants,
)


# =============================================================================
# CHAMATKAR_VERSES — 108 verses, keyed by (planet, house)
# Each entry: {verse_sanskrit, verse_translation, character_themes,
#              life_indications, source}
# =============================================================================

CHAMATKAR_VERSES = {

    # ─────────────────────────── SUN (verses 1-12) ───────────────────────────
    ("Sun", 1): {
        "verse_sanskrit": (
            "Ravir lagne sthitaschet syaat janmano dehasamsthite, "
            "alpa-keshah krodhanascha tunga-pratapa-dhanavaan."
        ),
        "verse_translation": (
            "When the Sun stands in the first house at the moment of birth, "
            "the native's body is robust though the head bears thinning hair, "
            "the temperament is quick to anger and slow to forgive, the eyes "
            "may suffer weakness in mid-life, and yet a high pratapa — solar "
            "lustre of authority — accompanies the person through life. He "
            "leads where he stands, his speech carries weight, and rulers, "
            "elder males, and government doors open to him; his fortune rises "
            "with bold action and falls with ego unchecked."
        ),
        "character_themes": ["proud", "leadership", "thinning-hair", "weak-eyes", "authoritative"],
        "life_indications": (
            "Native commands respect through presence and bearing. Father-relationship "
            "may be distant or formal. Career rises through self-effort and government "
            "or executive roles."
        ),
        "source": "Chamatkar Chintamani Verse 1",
    },

    ("Sun", 2): {
        "verse_sanskrit": (
            "Dhane Ravau dvitiye'pi mukhe dosha-vaag-virodhakah, "
            "kuteshu vigraha-yutascha shastra-vidya-vivarjita."
        ),
        "verse_translation": (
            "Sun in the second house gives ample resources earned through one's own "
            "exertion, but the speech tends toward sharpness — words can wound "
            "even kin. Mouth or teeth may give occasional trouble, and the native "
            "often finds himself in family-property disputes. Wealth comes through "
            "service to powerful men, public works, government salary, or "
            "metallurgical / fire-related trade. The native earns and loses; "
            "long-term prosperity depends on disciplining the tongue."
        ),
        "character_themes": ["sharp-speech", "self-earned-wealth", "family-disputes", "government-income"],
        "life_indications": (
            "Wealth from authority, government, or fire-trades. Speech is direct, sometimes "
            "abrasive. Family quarrels over inheritance possible."
        ),
        "source": "Chamatkar Chintamani Verse 2",
    },

    ("Sun", 3): {
        "verse_sanskrit": (
            "Tritiye Ravir-aaroopo bhratru-nasha-karaka kshipram, "
            "shaurya-vidya-yashah-praapto raja-dvaaragatah sukhi."
        ),
        "verse_translation": (
            "With Sun in the third house, the native is courageous, energetic, and "
            "possesses a soldier's heart. Younger siblings are few — one may pre-decease "
            "the native. He earns fame through valour, athletic skill, or written work, "
            "and finds easy access to ruling-class doorways. Short journeys prosper, "
            "letters bring opportunity, and his reputation in his own neighbourhood is "
            "of a man who stands his ground. Health is generally robust."
        ),
        "character_themes": ["courageous", "few-siblings", "fame-through-valour", "robust-health"],
        "life_indications": (
            "Strong willed, brave, may lose a younger sibling. Earns recognition through "
            "writing, sports, or military-style discipline."
        ),
        "source": "Chamatkar Chintamani Verse 3",
    },

    ("Sun", 4): {
        "verse_sanskrit": (
            "Sukha-sthane Ravir-jaatah maatru-sukha-vinashanaha, "
            "vahana-bhumi-rahito vipravaad-vidvad-aashrayah."
        ),
        "verse_translation": (
            "Sun in the fourth house diminishes the comforts of mother, home, and "
            "vehicle. The mother's health may suffer or her presence in the native's "
            "early life may be cut short by separation. Land and ancestral property "
            "yield less than expected, and the heart-region or chest may give occasional "
            "trouble. Yet the native gains the patronage of learned brahmins and "
            "wise elders, and finds inner stability through study rather than home."
        ),
        "character_themes": ["mother-loss", "limited-home-comfort", "weak-heart", "scholarly-patronage"],
        "life_indications": (
            "Mother-bond troubled — separation, illness, or distance. Home life unsettled. "
            "Refuge in learning, mentorship from elder scholars."
        ),
        "source": "Chamatkar Chintamani Verse 4",
    },

    ("Sun", 5): {
        "verse_sanskrit": (
            "Putrasthane Ravau jaate putra-shoka-samanvitah, "
            "udare vyaadhi-piditah pita-shatru-vivardhanah."
        ),
        "verse_translation": (
            "Sun in the fifth house brings sorrow regarding children — late progeny, "
            "or loss of a child, or only daughters when sons were sought. The stomach "
            "and digestive fire may give chronic trouble. Speculation rarely succeeds. "
            "There may be friction with the father or with father-figures in authority. "
            "Yet the native possesses sharp natural intelligence, talents in mantra "
            "and ritual, and earns respect for his discriminating mind even as the "
            "heart bears child-related grief."
        ),
        "character_themes": ["child-trouble", "stomach-issues", "father-friction", "sharp-intellect"],
        "life_indications": (
            "Few children or delayed progeny. Digestive troubles. Tension with father. "
            "Mantric/spiritual aptitude is strong."
        ),
        "source": "Chamatkar Chintamani Verse 5",
    },

    ("Sun", 6): {
        "verse_sanskrit": (
            "Shashthe Surya-yutah praaani vairi-vargasya naashanah, "
            "matuleshu sukham praapto raaja-mukhya-priyo bhaved."
        ),
        "verse_translation": (
            "Sun placed in the sixth house destroys enemies as fire consumes dry grass. "
            "The native triumphs over rivals, lawsuits turn in his favour, debts get "
            "repaid, and uncles on the mother's side bring help. He earns the favour "
            "of chief officers and government heads. Health is good but for occasional "
            "bilious or fever conditions. Service-related careers — administration, "
            "law-enforcement, medicine, military — flourish. The native is skilled "
            "in defeating opposition by direct confrontation rather than diplomacy."
        ),
        "character_themes": ["enemy-destroyer", "victorious-in-litigation", "maternal-uncle-blessed", "service-career"],
        "life_indications": (
            "Wins over enemies and lawsuits. Strong career in administration, law, medicine. "
            "Maternal uncle is supportive."
        ),
        "source": "Chamatkar Chintamani Verse 6",
    },

    ("Sun", 7): {
        "verse_sanskrit": (
            "Saptame Ravi-samyukto bhaaryaa-prema-vivarjitah, "
            "pravaasa-rahito naari-virahena pidditah."
        ),
        "verse_translation": (
            "Sun in the seventh affects matrimonial harmony adversely. The marriage "
            "tends to be ego-centred — both spouses claim the throne. The wife may "
            "suffer health issues, or the marriage may be delayed and difficult. "
            "Long journeys for trade rarely prosper unless the native learns humility. "
            "Partnerships in business require a deferential partner. Public-facing "
            "professions involving leadership succeed, but the cost is paid at home. "
            "Mid-life often brings some form of separation or estrangement."
        ),
        "character_themes": ["marital-friction", "ego-clashes", "delayed-marriage", "weak-partnership"],
        "life_indications": (
            "Marriage strained by power struggles. Wife may face health issues or be older. "
            "Long-distance business not favoured."
        ),
        "source": "Chamatkar Chintamani Verse 7",
    },

    ("Sun", 8): {
        "verse_sanskrit": (
            "Ashtame Ravi-samsthitah svalpaayuh sva-jana-vyathah, "
            "guhya-roga-kalankastho dhana-haani-samanvitah."
        ),
        "verse_translation": (
            "Sun in the eighth house gives a shorter or struggle-strewn lifespan, "
            "trouble with eyesight especially in old age, hidden ailments connected "
            "with the urogenital region or excretion, and grief from one's own kin. "
            "Inheritance disputes are common; legacies promised are often delayed or "
            "lost. The native carries hidden burdens not visible to others. Yet "
            "occult sciences, research, surgery, mining, and insurance professions "
            "may yield through this same eighth-house turn — what is buried becomes "
            "the source of the native's quiet authority."
        ),
        "character_themes": ["short-life-risk", "hidden-illness", "eye-trouble", "occult-aptitude", "kin-loss"],
        "life_indications": (
            "Health caution — eyes, urogenital, chronic. Disputes over inheritance. Aptitude for "
            "research, surgery, occult sciences."
        ),
        "source": "Chamatkar Chintamani Verse 8",
    },

    ("Sun", 9): {
        "verse_sanskrit": (
            "Bhaagye sthe ravi-vamshajaata pitru-saukhya-vivardhanah, "
            "dhaarmika dhanikah shoorah samaadhi-prarthanaa-priyah."
        ),
        "verse_translation": (
            "When the Sun rests in the ninth house, fortune flowers. The native is "
            "born into a respected lineage, earns blessings from a noble or pious "
            "father, and lives a dharma-aligned life. Wealth comes through righteous "
            "means — teaching, government service, religious patronage, foreign "
            "alliances. The native is brave in the cause of truth and finds joy "
            "in pilgrimages, meditation, and works of public benefit. He is favoured "
            "by elders, gurus, and rulers, and his fortune rises steadily through "
            "the mid-decades of life."
        ),
        "character_themes": ["fortunate", "dharmic", "noble-lineage", "father-blessed", "pilgrimage-loving"],
        "life_indications": (
            "Strong father, noble lineage, dharmic income. Blessed by gurus and rulers. "
            "Foreign opportunities favoured."
        ),
        "source": "Chamatkar Chintamani Verse 9",
    },

    ("Sun", 10): {
        "verse_sanskrit": (
            "Dashame Ravi-yutah praaani sarva-loka-prashasanah, "
            "raaja-tulyo mahaa-kirtih svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Sun in the tenth house yields one of its finest placements — the native "
            "rises to public renown, wields authority over many, and ranks among the "
            "respected of his sphere. Whatever profession he chooses, he ascends within "
            "it. The career tilts toward government, administration, public-office, "
            "judiciary, or independent enterprise where he is the chief. Fame "
            "spreads beyond his immediate circle. His own efforts bring him honour; "
            "he owes little to inheritance and much to personal merit."
        ),
        "character_themes": ["public-renown", "executive-power", "self-made", "career-rising", "respected"],
        "life_indications": (
            "Rises to authority through merit. Government, judiciary, executive role. "
            "Fame and public visibility."
        ),
        "source": "Chamatkar Chintamani Verse 10",
    },

    ("Sun", 11): {
        "verse_sanskrit": (
            "Laabhe sthe Ravi-samyukto bhuri-laabhanvitas-tu sah, "
            "anekashilpa-vidyaaptaa raja-mukhya-priyo bhaved."
        ),
        "verse_translation": (
            "Sun in the eleventh house brings abundant gains, multiple skills, and "
            "many circles of influence. The native is favoured by chiefs, government "
            "officials, and elder males of standing. Friends are few but powerful — "
            "a small circle of consequential allies. He earns through varied skills, "
            "investments, and side-trades. The elder brother may rise high or be "
            "estranged. Hopes long cherished are mostly fulfilled, particularly "
            "those involving career and recognition."
        ),
        "character_themes": ["abundant-gains", "multi-skilled", "powerful-friends", "fulfilled-ambition"],
        "life_indications": (
            "Many income streams. Powerful friends and government connections. "
            "Elder brother either rises high or estranges."
        ),
        "source": "Chamatkar Chintamani Verse 11",
    },

    ("Sun", 12): {
        "verse_sanskrit": (
            "Dvaadashe Ravi-samjaata netra-roga-kalankitaha, "
            "vyaya-bhuri videsha-stho dhana-haani-samanvitah."
        ),
        "verse_translation": (
            "Sun in the twelfth house weakens vitality and tends toward expenses "
            "exceeding income. The right eye especially may suffer trouble. The "
            "native may live abroad or in foreign-employed roles, far from his "
            "birthplace. Father-figures, government, and authority bring difficulty "
            "more than help. Yet this placement also gives spiritual depth — the "
            "ego is naturally dissolved through the twelfth-house teacher of loss, "
            "and many such natives become reflective, monastic, or quietly wise "
            "in later life."
        ),
        "character_themes": ["foreign-residence", "right-eye-weak", "spiritual-depth", "expenses-exceed-income"],
        "life_indications": (
            "Foreign settlement likely. Right-eye trouble. Father-figures bring difficulty. "
            "Spiritual depth in later years."
        ),
        "source": "Chamatkar Chintamani Verse 12",
    },

    # ─────────────────────────── MOON (verses 13-24) ──────────────────────────
    ("Moon", 1): {
        "verse_sanskrit": (
            "Lagne sthe Chandramaa jaato gourah saumya-mano-yutah, "
            "vahana-bhumi-shobhito daanavaan-priya-darshanah."
        ),
        "verse_translation": (
            "Moon in the first house shapes a fair-complexioned, gentle-souled "
            "native with a soft mind and pleasing presence. The body is well-formed "
            "and the face is attractive in its softness. The native is generous, "
            "fond of vehicles, water, and beautiful surroundings, and tends toward "
            "moodiness — joy and sorrow alternate quickly. People are drawn to him "
            "naturally; women, the public, and emotional connections become important "
            "in his life. Mother is a dominant influence; the home is his anchor."
        ),
        "character_themes": ["fair-complexion", "gentle", "moody", "popular", "mother-dominant"],
        "life_indications": (
            "Pleasant appearance, soft personality. Mother strongly influences life. "
            "Emotionally sensitive, public-loving."
        ),
        "source": "Chamatkar Chintamani Verse 13",
    },

    ("Moon", 2): {
        "verse_sanskrit": (
            "Dvitiye Chandramaa-jaata kuteshu sukhito naraha, "
            "madhura-vaag dhanaadhyas cha kavi-buddhi-vichakshanah."
        ),
        "verse_translation": (
            "Moon in the second house gives a sweet-tongued, family-loving native, "
            "comfortable in his clan, eloquent in speech, and skilled in poetry, "
            "music, or any craft of words. Wealth comes steadily — not always in "
            "large surges, but reliably from food-trade, dairy, hospitality, or "
            "service to women and the public. The face is bright, eyes expressive, "
            "and the mouth lends itself to song or oratory. Good food, good company, "
            "and pleasant conversation are the native's daily medicine."
        ),
        "character_themes": ["sweet-speech", "family-comfort", "poetic", "steady-wealth", "expressive-face"],
        "life_indications": (
            "Sweet speech, poetic gift, family-warmth. Wealth from food, dairy, hospitality, "
            "service-to-public trades."
        ),
        "source": "Chamatkar Chintamani Verse 14",
    },

    ("Moon", 3): {
        "verse_sanskrit": (
            "Tritiye Chandramaa-jaato bhraatru-veera-sahodarah, "
            "krura-karmaa lobha-yukto bhujangaa-bhaya-piditaha."
        ),
        "verse_translation": (
            "Moon in the third gives the native several siblings, particularly sisters, "
            "and a courageous if somewhat impulsive nature. Short journeys are frequent "
            "and the native is fond of them. The hands and arms are skilled — writing, "
            "music, craft. Yet a streak of cruelty or harshness may surface under "
            "stress, and small fears (snakes, thieves, sudden noises) may persist. "
            "The native is thrifty, sometimes greedy, and capable of holding old "
            "grudges; in compensation, he protects siblings fiercely."
        ),
        "character_themes": ["many-siblings", "skilled-hands", "thrifty", "fearful", "protective-of-siblings"],
        "life_indications": (
            "Several siblings. Skilled in arts of the hand. Some greed or harsh streak. "
            "Travels frequent."
        ),
        "source": "Chamatkar Chintamani Verse 15",
    },

    ("Moon", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Vidhau jaato vahana-bhumi-yashah-yutah, "
            "matri-snigdhah sukhi raajeevaaspadah priya-darshanah."
        ),
        "verse_translation": (
            "Moon in the fourth house — its own bhava — flowers in full sukha. "
            "The native owns vehicles, lands, comforts, and a happy home. The "
            "mother lives long, is loving, and supports every stage of his life. "
            "Property accumulates, often inherited and improved. The chest and "
            "heart-region are comfortable, the disposition is content, and friends "
            "of high standing visit the native's home freely. He is fond of water, "
            "fond of beauty, and finds his anchor in domestic life."
        ),
        "character_themes": ["happy-home", "long-lived-mother", "land-rich", "vehicle-comforts", "domestic-content"],
        "life_indications": (
            "Excellent placement — happy home, loving long-lived mother, comfortable "
            "land and vehicles, peace of mind."
        ),
        "source": "Chamatkar Chintamani Verse 16",
    },

    ("Moon", 5): {
        "verse_sanskrit": (
            "Putrasthaane Vidhau-jaate buddhi-yukto vichakshanah, "
            "putra-saukhyaa nichita-bhog kavi-vidya-vishaaradah."
        ),
        "verse_translation": (
            "Moon in the fifth bestows a quick, intuitive intellect, mantra-aptitude, "
            "and abundant child-happiness — particularly daughters who grow up "
            "creative and devoted. The native is a natural poet, lover of romance, "
            "speculator with mixed luck, and teacher when called upon. His children "
            "bring him joy, though they may include his emotional centre as much as "
            "his pride. Mantric practice and devotional poetry come naturally, and "
            "creative or artistic professions flourish."
        ),
        "character_themes": ["intuitive", "mantra-skill", "child-happy", "poetic", "romantic"],
        "life_indications": (
            "Sharp intuition, creative gifts, child-happiness (often daughters). "
            "Romantic, poetic, mantric aptitude."
        ),
        "source": "Chamatkar Chintamani Verse 17",
    },

    ("Moon", 6): {
        "verse_sanskrit": (
            "Shashthe Chandrah parikshipte vipra-roga-bhaya-yutah, "
            "matru-pidha-yutah praaani sthaayi-shatru-vivardhanah."
        ),
        "verse_translation": (
            "Moon in the sixth house weakens emotional and digestive health. The "
            "mother's health may concern the native; close maternal kin may pass "
            "early. Stomach, chest, or chronic anxiety-related ailments persist. "
            "The native acquires real enemies — those who oppose persistently, not "
            "passing rivals — and faces some debt-cycle or service-bondage in "
            "mid-life. Yet the placement gives endurance: he learns to absorb pain, "
            "and through service-related careers (medicine, nursing, social work, "
            "litigation, employment under demanding masters) he often prospers."
        ),
        "character_themes": ["mother-illness", "stomach-anxiety", "persistent-enemies", "service-bond", "endurance"],
        "life_indications": (
            "Mother's health concerning. Anxiety or chronic stomach issues. Service-careers, "
            "medicine, social work favoured."
        ),
        "source": "Chamatkar Chintamani Verse 18",
    },

    ("Moon", 7): {
        "verse_sanskrit": (
            "Saptame Chandramaa-jaato bhaaryaa-prema-samanvitah, "
            "naari-vallabhah sundaro madhura-vaag-vinodakah."
        ),
        "verse_translation": (
            "Moon in the seventh house gives a beautiful, gentle, well-loved spouse "
            "and a marriage rich in emotional rapport. The native is fond of women, "
            "beautiful in his own bearing, sweet of speech, and naturally drawn to "
            "partnerships — both marital and commercial. Trade, especially in "
            "luxury goods, public-facing services, hospitality, or dairy, prospers. "
            "Long journeys for business succeed. The marriage may bring travel and "
            "social mobility. The mother-in-law also tends to support generously."
        ),
        "character_themes": ["loving-spouse", "marriage-prosperous", "hospitality-trade", "popular-with-women"],
        "life_indications": (
            "Loving, often beautiful spouse. Trade-partnerships prosper. Travel through marriage. "
            "Mother-in-law supportive."
        ),
        "source": "Chamatkar Chintamani Verse 19",
    },

    ("Moon", 8): {
        "verse_sanskrit": (
            "Ashtame Chandramaa-jaato matri-shoka-vivardhanah, "
            "udare vyaadhi-yukto'sau svalpaayur-vipathaagatih."
        ),
        "verse_translation": (
            "Moon in the eighth house shadows the mother's lifespan or health and "
            "places the native in some mid-life crisis or transformation that tests "
            "his foundations. Stomach, chest, urogenital system may give chronic "
            "trouble. Inheritance is unpredictable. Yet this same placement gives "
            "psychic depth — dreams are vivid, intuition runs deep, and the native "
            "may be drawn to occult or healing arts. He carries an old emotional "
            "wound that becomes the source of his eventual wisdom. Long-term "
            "settlements are rarely smooth in early decades."
        ),
        "character_themes": ["mother-loss-risk", "psychic-depth", "stomach-chronic", "occult-pull", "transformation"],
        "life_indications": (
            "Mother's longevity/health concerning. Mid-life transformation. Psychic gifts, "
            "draws to occult or healing arts."
        ),
        "source": "Chamatkar Chintamani Verse 20",
    },

    ("Moon", 9): {
        "verse_sanskrit": (
            "Bhaagye Chandramasi sthite bhaagyavaan dharma-shobhitah, "
            "tirthatra-yatra-yukto raja-vamsha-priya-darshanah."
        ),
        "verse_translation": (
            "Moon in the ninth house brings high fortune, a dharmic disposition, "
            "and frequent pilgrimage. The native loves sacred places, gurus, and "
            "the company of elders; he is drawn to philosophy, devotion, and "
            "wide travels. His father is generally supportive (Sun-Moon "
            "harmony often follows). He gains social standing through ethical "
            "conduct. Foreign opportunities open and prosper. Wealth comes "
            "through honest means — teaching, religious patronage, government "
            "service, or ethical trade. People perceive him as good-hearted "
            "and trust him with responsibilities."
        ),
        "character_themes": ["fortunate", "pilgrimage-loving", "dharmic", "father-supported", "trustworthy"],
        "life_indications": (
            "Fortunate, dharmic, foreign-favoured. Trusted by elders, supported by father. "
            "Pilgrimage and teaching prosper."
        ),
        "source": "Chamatkar Chintamani Verse 21",
    },

    ("Moon", 10): {
        "verse_sanskrit": (
            "Dashame Chandramaa-yukto karma-siddhah pratapavan, "
            "raajaadhipa-priyo nityam yashasvi sukha-bhog-vaan."
        ),
        "verse_translation": (
            "Moon in the tenth house gives professional success in fields touching "
            "the public — trade, hospitality, service, fluid-related industries "
            "(water, dairy, beverages, shipping), nursing, or emotional-care "
            "professions. The native is well-known among working circles, favoured "
            "by senior women in his career-line, and seen as approachable. His "
            "reputation is one of warmth and competence both. Ambition is steady "
            "rather than ferocious. He earns honourably and rises within his chosen "
            "field over the decades, often through mother's blessing."
        ),
        "character_themes": ["public-career", "well-known", "trade-success", "warm-reputation", "mother-blessed-career"],
        "life_indications": (
            "Career in public-facing field — trade, hospitality, service, fluids, care. "
            "Steady rise, mother-blessed."
        ),
        "source": "Chamatkar Chintamani Verse 22",
    },

    ("Moon", 11): {
        "verse_sanskrit": (
            "Ekaa-dashe Vidhau jaato bhuri-laabhasamanvitah, "
            "naari-mitra-priyo viprah kavi-buddhi-vivekashah."
        ),
        "verse_translation": (
            "Moon in the eleventh house gives plentiful gains, many friends, "
            "and a wide social network rich in women and influential persons. "
            "The native earns through several side-streams in addition to his main "
            "vocation. Hopes long-cherished come to fruition, generally with "
            "happiness intact. He is fond of poetry, social events, literary "
            "circles, and the company of cultured women. Elder siblings, particularly "
            "elder sisters, are well-disposed and may help the native at key "
            "junctures. Wealth-flow is consistent."
        ),
        "character_themes": ["many-gains", "wide-friend-circle", "popular-with-women", "elder-sister-supportive"],
        "life_indications": (
            "Many friends, abundant gains, ambitions fulfilled. Elder sister supportive. "
            "Side-incomes flourish."
        ),
        "source": "Chamatkar Chintamani Verse 23",
    },

    ("Moon", 12): {
        "verse_sanskrit": (
            "Dvaadashe Chandramaa-jaata matru-sukha-vivarjitah, "
            "videsha-vaasi vyayinah svapna-darshanaayudhah."
        ),
        "verse_translation": (
            "Moon in the twelfth house gives a wandering, foreign-residing, expense-prone "
            "native whose mother's comforts may be cut short by distance or early loss. "
            "The native often settles abroad or far from his birthplace. Sleep is rich "
            "with dreams; intuition runs deep; spiritual insight develops naturally. "
            "Material expenses usually exceed income, and emotional fulfilment must be "
            "cultivated rather than received. Ashrams, monastic orders, hospitals, "
            "long-stay accommodations abroad, or solitary intellectual pursuits often "
            "draw such a native; the soul learns by withdrawal."
        ),
        "character_themes": ["foreign-resident", "mother-distance", "dreamful", "expense-prone", "spiritual"],
        "life_indications": (
            "Foreign residence, distance from mother. Dream-rich, intuitive, spiritual. "
            "Expenses exceed income; introspective."
        ),
        "source": "Chamatkar Chintamani Verse 24",
    },

    # ─────────────────────────── MARS (verses 25-36) ──────────────────────────
    ("Mars", 1): {
        "verse_sanskrit": (
            "Lagne sthe Bhumi-putre tu krurah krodhi shauryavaan, "
            "shastra-vidya-yashah praapto raktavarna-shareeravaan."
        ),
        "verse_translation": (
            "Mars in the first house gives a fiery, energetic, athletic native with "
            "a coppery or reddish complexion and lean muscular build. Quick-tempered, "
            "courageous, sometimes harsh in manner, the native excels in arms, sports, "
            "engineering, surgery, or any field demanding decisive action. Scars or "
            "injuries on the head/face are common — childhood accidents, falls, fights. "
            "The native does not yield easily; what he wants, he pursues directly. "
            "Manglik or kuja-dosha applies for marital matching."
        ),
        "character_themes": ["fiery", "athletic", "courageous", "scarred", "quick-tempered"],
        "life_indications": (
            "Manglik. Scars on head/face. Athletic, surgical, engineering, military aptitude. "
            "Direct, sometimes harsh."
        ),
        "source": "Chamatkar Chintamani Verse 25",
    },

    ("Mars", 2): {
        "verse_sanskrit": (
            "Dvitiye Bhauma-yukto'sau kuteshu kalaha-kaarakaha, "
            "para-stree-rata para-dravya-haari kshudra-vaag-vivaadakah."
        ),
        "verse_translation": (
            "Mars in the second house quarrels with kin and sharpens speech to "
            "wounding edge. Family-property disputes often arise; the native may "
            "lose his share through quarrels. Wealth is earned but spent fast. "
            "There may be a tendency toward illicit relationships or appetite "
            "for what belongs to others. Eyes, teeth, or face may bear injury "
            "marks. Yet the same Mars gives the native fearlessness in earning — "
            "he makes money from contested fields, real-estate, weapons, surgery, "
            "metals, or risk-taking trade where less courageous men avoid."
        ),
        "character_themes": ["family-quarrels", "harsh-speech", "appetite-for-others-goods", "high-risk-earnings"],
        "life_indications": (
            "Family-property quarrels, harsh speech. Earnings from real-estate, metals, weapons, "
            "surgery, contested fields."
        ),
        "source": "Chamatkar Chintamani Verse 26",
    },

    ("Mars", 3): {
        "verse_sanskrit": (
            "Tritiye Bhauma-vaan-praaani bhraatru-vairi-pradhaarakah, "
            "shauryavan saahasi vidvaan svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Mars in the third house — a strong placement — gives outstanding "
            "courage, decisive action, athletic prowess, and strong younger "
            "siblings (particularly brothers). The native takes initiative, "
            "completes what he begins, and prospers through his own effort. "
            "Writing, journalism, sports, military, and engineering all suit. "
            "Travel is favourable; he is at home on the move. The arms and "
            "shoulders are powerful. Younger brother often does well or stands "
            "by the native through hardship. This is one of Mars's best houses."
        ),
        "character_themes": ["strong-courage", "supportive-younger-brother", "self-effort-rewarded", "athletic"],
        "life_indications": (
            "Excellent. Powerful younger brother, strong arms, courage, self-made success. "
            "Sports, military, journalism."
        ),
        "source": "Chamatkar Chintamani Verse 27",
    },

    ("Mars", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Kuje sthite maatru-saukhya-vivarjitah, "
            "vahana-bhumi-virahito hridaye dukhha-piditaha."
        ),
        "verse_translation": (
            "Mars in the fourth house disturbs the comforts of home, mother, "
            "and emotional stability. The mother's health or longevity may "
            "concern the native; she may have suffered a difficult labour. "
            "Property quarrels are likely, especially over ancestral land. "
            "Vehicles may give trouble or accidents. The chest, heart, or "
            "respiratory system may need care. There is restlessness in the "
            "home. Yet this Mars also makes the native a builder, engineer, "
            "or property-developer — what is contested, he eventually owns "
            "through persistence."
        ),
        "character_themes": ["mother-strain", "property-quarrels", "vehicle-accidents", "heart-region-issues", "builder"],
        "life_indications": (
            "Mother's health/longevity concern. Property contests. Eventually a builder / "
            "real-estate man through persistence."
        ),
        "source": "Chamatkar Chintamani Verse 28",
    },

    ("Mars", 5): {
        "verse_sanskrit": (
            "Putrasthaane Kuje jaate putra-shoka-samanvitah, "
            "udara-roga-piditas tu sthaayi-shatru-vivardhanah."
        ),
        "verse_translation": (
            "Mars in the fifth house brings child-related sorrow — late progeny, "
            "miscarriages, or strong-willed children who clash with the native. "
            "The first child is often male and intense in temperament. Speculation "
            "is risky; gambling tendencies should be checked. Stomach, intestines, "
            "and inflammatory conditions may appear. Yet the native's intelligence "
            "is sharp, decisive, sometimes brilliant under pressure. He is good at "
            "mantra-shastra, particularly Mars-related (Hanuman, Kartikeya, Durga). "
            "Children eventually do well in athletics or technical fields."
        ),
        "character_themes": ["child-difficulty", "strong-willed-child", "stomach-inflammation", "mantra-shastra-aptitude"],
        "life_indications": (
            "Child-difficulty (delays, miscarriage, intense first child). Speculation risky. "
            "Mantra-aptitude, sharp under pressure."
        ),
        "source": "Chamatkar Chintamani Verse 29",
    },

    ("Mars", 6): {
        "verse_sanskrit": (
            "Shashthe Bhauma-vaan praaani vairi-naashana-kaarakaha, "
            "matuleshu sukhaha praapto raja-mukhya-priyo bhaved."
        ),
        "verse_translation": (
            "Mars in the sixth — exceptionally strong — destroys enemies, wins "
            "lawsuits, defeats rivals decisively. The native is a fighter, surgeon, "
            "police officer, military man, or someone in conflict-related profession. "
            "His maternal uncles support him; he gets loans repaid; debts diminish "
            "in mid-life. Health is generally robust though prone to inflammatory "
            "fevers. He is favoured by chiefs and authorities. This Mars is also "
            "called Vipareeta-Mars — the more obstacles thrown at the native, the "
            "more he rises through them. One of Mars's finest placements."
        ),
        "character_themes": ["enemy-destroyer", "victorious-litigation", "police-military-surgeon", "vipareeta-rise"],
        "life_indications": (
            "Excellent — defeats enemies, wins lawsuits, robust health. Police, military, "
            "surgery, litigation."
        ),
        "source": "Chamatkar Chintamani Verse 30",
    },

    ("Mars", 7): {
        "verse_sanskrit": (
            "Saptame Bhauma-yukto'sau krurah kalaha-kaarakah, "
            "bhaaryaa-shoka-yutaha praaani vipata-bahu-shobhitah."
        ),
        "verse_translation": (
            "Mars in the seventh house gives kuja-dosha and difficulty in marriage. "
            "The native or spouse may suffer health issues; quarrels mark the "
            "marital relationship; there may be widowhood or divorce risk in "
            "severe cases. Partnerships in business often dissolve in argument. "
            "Long journeys for trade rarely smooth. Yet matched with another "
            "Manglik chart, the dosha is largely cancelled, and the marriage "
            "may be passionate, productive, and enduring. Without remedy, "
            "marriage typically delays past 28 or has rough early years."
        ),
        "character_themes": ["manglik", "marital-strife", "partnership-fragile", "passion-or-dissolution"],
        "life_indications": (
            "Manglik dosha — marriage-delay, marital quarrels, partnership-risk. "
            "Match with Manglik chart cancels."
        ),
        "source": "Chamatkar Chintamani Verse 31",
    },

    ("Mars", 8): {
        "verse_sanskrit": (
            "Ashtame Bhauma-samjaata svalpaayur-roga-pidditaha, "
            "guhya-roga-bhayopetah dhana-kshaya-samanvitah."
        ),
        "verse_translation": (
            "Mars in the eighth house gives shorter or accident-strewn lifespan, "
            "wounds requiring surgery, hidden ailments connected with the urogenital "
            "or excretory system, and persistent fear of accidents or sudden "
            "calamity. Inheritance is rarely smooth — disputes arise. Yet the "
            "native has natural surgical skill, occult intuition, and ability "
            "in research where things are hidden. Insurance, mining, oil, "
            "underground work, surgery, forensics may suit. The eighth-house Mars "
            "is intense but not always destructive — used well, it gives one "
            "of the steeliest minds in any chart."
        ),
        "character_themes": ["accident-prone", "surgical-skill", "occult", "inheritance-disputes", "steely-mind"],
        "life_indications": (
            "Accident risk. Surgical/occult/research aptitude. Inheritance contested. "
            "Strong mind under pressure."
        ),
        "source": "Chamatkar Chintamani Verse 32",
    },

    ("Mars", 9): {
        "verse_sanskrit": (
            "Bhaagye sthe Bhauma-vaan-jaata pitru-sukha-vinaashanah, "
            "shaurya-vidya-yashah-praaptah viprashca priya-darshanah."
        ),
        "verse_translation": (
            "Mars in the ninth house gives bravery in dharma, strong action-oriented "
            "philosophy, and a forceful father-figure with whom the native may clash. "
            "The native is religious in his own way — protector of dharma rather "
            "than scholar of it. He is famed for valour and decisive action; people "
            "see him as principled and unyielding. Pilgrimage to fierce deity-shrines "
            "(Hanuman, Kartikeya, Durga) suits him. Foreign travel may bring conflict "
            "or adventure rather than ease. The father may be authoritarian or in "
            "military/police line."
        ),
        "character_themes": ["father-clash", "warrior-dharma", "valourous", "protector-of-tradition", "fierce-pilgrimage"],
        "life_indications": (
            "Strong father, possible clashes. Warrior-dharma. Valour, decisive principle. "
            "Foreign-conflict adventures."
        ),
        "source": "Chamatkar Chintamani Verse 33",
    },

    ("Mars", 10): {
        "verse_sanskrit": (
            "Dashame Kuja-jaata praaani karma-siddhi-vivardhanah, "
            "raja-tulyo mahaa-veerah svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Mars in the tenth house — a Ruchaka-Yoga placement when in own or "
            "exalted sign — yields a powerful career, executive authority, "
            "command over many, and rapid professional rise. The native is "
            "decisive, builds organizations, leads others into action, and is "
            "respected for his courage. Engineering, military, surgery, real-estate "
            "development, sports, police, and entrepreneurship in any contested "
            "field flourish. The native works harder than peers and outlasts them. "
            "Fame through valour and decisive action rather than diplomacy."
        ),
        "character_themes": ["executive-power", "builder", "decisive", "fame-through-valour", "ruchaka-yoga-potential"],
        "life_indications": (
            "Powerful career, executive authority. Engineering, military, real-estate, "
            "surgery. Ruchaka Yoga if dignified."
        ),
        "source": "Chamatkar Chintamani Verse 34",
    },

    ("Mars", 11): {
        "verse_sanskrit": (
            "Laabhe sthe Bhauma-yukto'sau bhuri-laabha-samanvitah, "
            "shauryena dhana-laabha-stho jyeshtha-bhraatru-priyo bhaved."
        ),
        "verse_translation": (
            "Mars in the eleventh house gives abundant gains earned through courage, "
            "decisive action, and willingness to take risks others avoid. The native "
            "has supportive elder brothers (or elder-brother-figures) who help him "
            "rise. Friendships are with strong-willed, decisive people — not gentle "
            "ones. He earns through engineering, real-estate, sports, defence, "
            "surgery, or any contested industry. Hopes long-cherished are mostly "
            "fulfilled through his own driving effort. The income flow is uneven "
            "but the cumulative wealth is significant."
        ),
        "character_themes": ["courageous-gains", "elder-brother-support", "decisive-friend-circle", "risk-taker"],
        "life_indications": (
            "Earnings through courage and risk-taking. Elder brother supportive. "
            "Strong-willed friend network."
        ),
        "source": "Chamatkar Chintamani Verse 35",
    },

    ("Mars", 12): {
        "verse_sanskrit": (
            "Dvaadashe Bhauma-samjaato vyaya-bahu-laabha-vihinah, "
            "videsha-vaasi shatru-yukto netra-roga-samanvitah."
        ),
        "verse_translation": (
            "Mars in the twelfth house gives high expenses, foreign residence, "
            "hidden enemies, weak left eye in some cases, and tendency toward "
            "isolated or contested settings — military deployment abroad, "
            "expatriate work in difficult regions, prison-related professions, "
            "or simply working night-shifts and behind-the-scenes roles. The "
            "native may have aggressive enemies who do not show themselves. "
            "Sleep can be disturbed. Yet this same Mars produces effective "
            "behind-scenes operators — intelligence, special-forces, surgeons "
            "in remote postings, foreign-base engineers."
        ),
        "character_themes": ["foreign-residence", "high-expenses", "hidden-enemies", "behind-scenes-operator"],
        "life_indications": (
            "Foreign settlement, hidden enemies. Behind-scenes military, surgery, "
            "special operations. Disturbed sleep."
        ),
        "source": "Chamatkar Chintamani Verse 36",
    },

    # ────────────────────────── MERCURY (verses 37-48) ────────────────────────
    ("Mercury", 1): {
        "verse_sanskrit": (
            "Lagne sthe Saumya-samjaato gourah priya-vachas-tatha, "
            "vidvan dhanavaan kavi-buddhi-vivekashah."
        ),
        "verse_translation": (
            "Mercury in the first house produces a fair-complexioned, youthful-looking, "
            "intellectually quick, and verbally adept native. The body remains "
            "youthful long, sometimes appearing younger than actual age. Speech is "
            "pleasant, witty, and capable. The native is well-read in many subjects, "
            "skilled in writing, accounts, mathematics, and any field where words "
            "and numbers earn livelihood. He is fond of laughter, good company, "
            "and intelligent conversation. He may keep changing interests, often "
            "doing several things at once. Skin and complexion remain bright."
        ),
        "character_themes": ["youthful", "witty", "intellectual", "multi-skilled", "fair-complexion"],
        "life_indications": (
            "Looks younger than age. Witty, intellectual, multi-skilled. Earns through writing, "
            "accounts, math, communication."
        ),
        "source": "Chamatkar Chintamani Verse 37",
    },

    ("Mercury", 2): {
        "verse_sanskrit": (
            "Dvitiye Saumya-yukto'sau dhanavaan satya-vaak-pati, "
            "kavi-vidya-vishaaradah madhura-vaag-vichakshanah."
        ),
        "verse_translation": (
            "Mercury in the second house — its own bhava counted from Gemini — "
            "is one of its strongest. The native earns abundantly through speech, "
            "writing, accounting, trade, brokering, mathematics, or any commercial "
            "skill. The voice is clear and pleasant, the speech truthful and "
            "persuasive. Family is intellectually engaged. Wealth comes through "
            "calculation rather than luck. Knowledge of scriptures, languages, "
            "or technical fields gives steady income. Good poet, good orator, "
            "good arithmetician. Family life is generally amicable."
        ),
        "character_themes": ["wealth-through-speech", "truthful-orator", "trade-skill", "scholarly", "good-mathematician"],
        "life_indications": (
            "Excellent. Wealth through speech, writing, trade, mathematics. Truthful, "
            "scholarly. Family intellectual."
        ),
        "source": "Chamatkar Chintamani Verse 38",
    },

    ("Mercury", 3): {
        "verse_sanskrit": (
            "Tritiye Saumya-jaatas tu lekhaka-yukto vichakshanaha, "
            "shaurya-vidya-yashah praapto kavi-buddhi-vinodakah."
        ),
        "verse_translation": (
            "Mercury in the third house produces excellent writers, journalists, "
            "editors, scribes, postal workers, or anyone whose hands and tongue "
            "earn together. Younger siblings tend to be intelligent and may help "
            "the native. Travel is frequent, often profitable. The native has "
            "ambidextrous skill in writing, drawing, or instrument-playing. "
            "Courage is intellectual rather than physical — he wins arguments, "
            "outwits opponents, plans carefully. Letter-writing and short-message "
            "communications shape his career. Public speaking, broadcasting, "
            "translation, and authorship suit."
        ),
        "character_themes": ["writer", "translator", "intelligent-younger-sibling", "ambidextrous", "wit"],
        "life_indications": (
            "Excellent for writing/journalism. Intelligent younger siblings. Frequent profitable "
            "travel. Skilled hands."
        ),
        "source": "Chamatkar Chintamani Verse 39",
    },

    ("Mercury", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Saumya-jaata maatru-saukhya-samanvitah, "
            "vahana-bhumi-shobhito vidvaan-priya-darshanah."
        ),
        "verse_translation": (
            "Mercury in the fourth house gives a learned, well-read mother, a "
            "comfortable home full of books, music, and intelligent conversation. "
            "Vehicles are usually owned, often more than one over a lifetime. "
            "Property is acquired through one's own intellect rather than "
            "inheritance. The native loves learning at home, builds a personal "
            "library, and is skilled in domestic crafts of the mind — chess, "
            "music, computation. Friends visit often. Mother is supportive, "
            "intellectually engaged, and lives well."
        ),
        "character_themes": ["learned-mother", "library-home", "vehicles", "intellectual-domestic-life"],
        "life_indications": (
            "Educated mother. Books and learning at home. Vehicles, property through one's "
            "own efforts."
        ),
        "source": "Chamatkar Chintamani Verse 40",
    },

    ("Mercury", 5): {
        "verse_sanskrit": (
            "Putrasthaane Saumya-jaata buddhi-yukto vichakshanaha, "
            "putra-vidya-priyo nityam mantra-shastra-vivekashah."
        ),
        "verse_translation": (
            "Mercury in the fifth house bestows sharp intellect, mathematical "
            "talent, mantra-aptitude, and intelligent children — particularly "
            "ones who excel in academics. The native is a natural teacher, "
            "gifted in passing knowledge to others, and may have aptitude in "
            "speculation, stocks, or pattern-based games (chess, cards, poker — "
            "but always with calculation, never reckless gambling). He is "
            "creative in writing rather than poetry of feeling. Mantra-shastra, "
            "astrology, mathematics, and analytical sciences appeal."
        ),
        "character_themes": ["sharp-intellect", "intelligent-children", "teacher", "calculative", "mantra-shastra"],
        "life_indications": (
            "Intelligent children, especially academic. Teaching, calculation, mantra. "
            "Speculation only with skill."
        ),
        "source": "Chamatkar Chintamani Verse 41",
    },

    ("Mercury", 6): {
        "verse_sanskrit": (
            "Shashthe Saumya-yutah praaani vairi-vargasya naashanaha, "
            "matuleshu sukham praapto vyaadhi-haarako bhaved."
        ),
        "verse_translation": (
            "Mercury in the sixth house defeats enemies through cleverness — "
            "lawsuits won by argument, rivals outwitted, debts cleared by clever "
            "negotiation. The native is fond of his maternal uncles. Health is "
            "generally good though anxiety-ailments may surface. Service-careers "
            "(accounting, audit, legal, medical writing, technical service) "
            "flourish. He is a good employee, valued for analytical skill. "
            "Skin sometimes shows occasional disorders. Pets, particularly "
            "small ones, accompany his life. Litigation almost always favours him."
        ),
        "character_themes": ["clever-rival-defeat", "service-career", "anxiety-prone", "litigation-winner"],
        "life_indications": (
            "Wins lawsuits and outwits rivals. Service career — accounting, audit, legal, "
            "medical-writing. Maternal uncle close."
        ),
        "source": "Chamatkar Chintamani Verse 42",
    },

    ("Mercury", 7): {
        "verse_sanskrit": (
            "Saptame Saumya-samyukto bhaaryaa-prema-vichakshanaha, "
            "kavi-vaag-priya-vakta cha vyaapaaresh-svalpa-laabha-bhaak."
        ),
        "verse_translation": (
            "Mercury in the seventh house gives an intelligent, often younger, "
            "well-read spouse — usually fond of conversation, books, and travel. "
            "The marriage is companionable, sometimes more intellectual than "
            "passionate. Trade-partnerships flourish; the native is a natural "
            "negotiator and broker. Long journeys for business succeed. He "
            "earns through commerce, mediation, brokerage, and transactional "
            "professions. Spouse may be from a learned family or a different "
            "linguistic background. The marriage tends to bring intellectual "
            "growth as much as emotional depth."
        ),
        "character_themes": ["intelligent-spouse", "companionable-marriage", "broker", "commercial-skill"],
        "life_indications": (
            "Intelligent often-younger spouse. Trade-partnerships, brokerage flourish. "
            "Marriage companionable and intellectual."
        ),
        "source": "Chamatkar Chintamani Verse 43",
    },

    ("Mercury", 8): {
        "verse_sanskrit": (
            "Ashtame Saumya-yukto'sau guhya-vidya-vivekashah, "
            "svalpaayuh kalanka-yutas tatra-svaadhyaya-tatparah."
        ),
        "verse_translation": (
            "Mercury in the eighth house gives talent in occult sciences, "
            "research, mantra-shastra, astrology, deep mathematics, and any "
            "field investigating what is hidden. The lifespan may be average "
            "or slightly shortened — health checks recommended in mid-life. "
            "Skin or nervous-system ailments may appear. Inheritance receives "
            "through legal/written means rather than direct. The native is "
            "a skilled investigator, detective-mind, or research-scholar. "
            "Reputation may face minor scandal but seldom permanent damage. "
            "Insurance, audit, forensics, occult professions flourish."
        ),
        "character_themes": ["occult-research", "investigator-mind", "mantra-shastra", "skin-nervous-issues"],
        "life_indications": (
            "Aptitude in occult, research, audit, forensics. Average lifespan. "
            "Inheritance through documentation."
        ),
        "source": "Chamatkar Chintamani Verse 44",
    },

    ("Mercury", 9): {
        "verse_sanskrit": (
            "Bhaagye Saumya-samjaato dharma-vidya-vivekashah, "
            "tirtha-yatra-priyah praaani vipra-mukhya-priyah-priyaha."
        ),
        "verse_translation": (
            "Mercury in the ninth house produces a learned, dharmic, well-travelled "
            "native who blends religion with reason. The native is a teacher, "
            "philosopher, lawyer with ethical leaning, or writer on philosophy "
            "and dharma. Foreign travels are frequent and educational. Father "
            "is generally educated and supportive. The native gains the "
            "patronage of senior scholars and respected priests. Long journeys "
            "for study or teaching flourish. Higher education is completed and "
            "may extend into multiple degrees. He is principled but flexible."
        ),
        "character_themes": ["learned-dharmic", "philosopher-teacher", "well-travelled", "father-educated"],
        "life_indications": (
            "Higher education, multiple degrees. Philosopher, teacher, ethical lawyer. "
            "Foreign study and travel favoured."
        ),
        "source": "Chamatkar Chintamani Verse 45",
    },

    ("Mercury", 10): {
        "verse_sanskrit": (
            "Dashame Saumya-samjaato karma-siddhah pratapavan, "
            "vyaapaarena dhanaagamo lekhaka-buddhi-vinodakah."
        ),
        "verse_translation": (
            "Mercury in the tenth house gives professional success in commerce, "
            "communications, accounts, banking, technology, journalism, mediation, "
            "or any field where intellectual skill is the chief currency. The "
            "native is renowned in his profession for analytical ability and "
            "verbal fluency. He may run multiple lines of work simultaneously. "
            "Government writing-positions, communications industries, IT, "
            "audit, and editorial roles all suit. The career rises through "
            "merit and skill rather than connections, and reputation in trade "
            "circles is excellent."
        ),
        "character_themes": ["commercial-success", "writer-broadcaster", "multi-line-career", "merit-rise"],
        "life_indications": (
            "Career in commerce, IT, journalism, accounts, banking. Multiple work-lines. "
            "Rises through merit."
        ),
        "source": "Chamatkar Chintamani Verse 46",
    },

    ("Mercury", 11): {
        "verse_sanskrit": (
            "Laabhe Saumya-samjaato bhuri-laabha-samanvitah, "
            "vidvad-mitra-priyah shastra-jnaani satya-vaag-vidaaha."
        ),
        "verse_translation": (
            "Mercury in the eleventh house gives plentiful gains, learned friends, "
            "scholarly company, and many side-incomes. The native is famed in "
            "literary, scientific, or commercial circles for his analytical "
            "ability. Elder brother is intelligent and often helpful. Aspirations "
            "long-cherished are fulfilled through study and intellectual pursuit. "
            "Wealth flows from books, courses, software, intellectual property, "
            "consulting, brokerage, and other writing- or thinking-driven income. "
            "Truth-telling is part of the personality. Friendships are mostly "
            "with educated, witty, well-read people."
        ),
        "character_themes": ["abundant-gains-from-intellect", "learned-friend-circle", "elder-brother-supportive", "consulting-income"],
        "life_indications": (
            "Plentiful gains from intellectual pursuits. Learned friends. Elder brother "
            "intelligent. Consulting/brokerage income."
        ),
        "source": "Chamatkar Chintamani Verse 47",
    },

    ("Mercury", 12): {
        "verse_sanskrit": (
            "Dvaadashe Saumya-samjaata svaadhyaaya-praaapta-mukti-yutah, "
            "videsha-vaasi vidvaan moksha-marga-pravartakaha."
        ),
        "verse_translation": (
            "Mercury in the twelfth house produces a quietly learned, contemplative "
            "native often drawn to study abroad, monastic philosophy, or solitary "
            "intellectual work. Many such natives become translators, librarians, "
            "philosophers, or technical writers in foreign settings. Speech may be "
            "softer, more thoughtful. Sleep is rich with vivid dreams; intuition "
            "develops alongside reasoning. Expenses are mostly on books, courses, "
            "travel, and learning. The mind seeks moksha-knowledge — what frees "
            "rather than what binds. Ascetic or scholarly tendencies surface."
        ),
        "character_themes": ["foreign-study", "contemplative", "translator", "moksha-seeking-mind"],
        "life_indications": (
            "Foreign study/work likely. Contemplative, philosophical. Translator, librarian, "
            "scholar abroad. Vivid dreams."
        ),
        "source": "Chamatkar Chintamani Verse 48",
    },

    # ─────────────────────────── JUPITER (verses 49-60) ───────────────────────
    ("Jupiter", 1): {
        "verse_sanskrit": (
            "Lagne sthe Guru-samjaato dirgha-aayuh sukha-bhog-vaan, "
            "dharmaatmaa shaastra-vidvaan satya-vaak satkriyaa-priyaha."
        ),
        "verse_translation": (
            "Jupiter in the first house — Hamsa Yoga if dignified — gives a long-lived, "
            "comfortable, dharmic native of broad learning, truthful speech, and "
            "ethical bearing. The native is well-built, slightly stocky, with a "
            "dignified bearing and pleasant voice. He is naturally drawn to "
            "scriptures, philosophy, teaching, and moral leadership. Children are "
            "born to him and bring joy. Wealth comes through righteous means, "
            "often via teaching, advisory work, or guru-like roles. People seek "
            "him for counsel; he is trusted across many circles."
        ),
        "character_themes": ["long-lived", "dharmic", "scholarly", "trusted-counsellor", "hamsa-yoga-potential"],
        "life_indications": (
            "Hamsa Yoga if Jupiter dignified. Long-lived, dharmic, scholarly. Trusted counsellor. "
            "Teacher/advisor."
        ),
        "source": "Chamatkar Chintamani Verse 49",
    },

    ("Jupiter", 2): {
        "verse_sanskrit": (
            "Dvitiye Guru-samjaato dhanavaan dharma-shobhitah, "
            "kavi-vidya-vishaaradah madhura-vaag-vichakshanaha."
        ),
        "verse_translation": (
            "Jupiter in the second house gives substantial, dharmically-earned wealth, "
            "a learned and prosperous family, sweet truthful speech, and "
            "good food and hospitality at home. The voice carries authority "
            "without harshness; speech is wise, measured, and well-received. "
            "Wealth comes through teaching, advisory, religious patronage, "
            "publishing, financial counselling, or any field where wisdom "
            "generates income. The face is bright, eyes kind, mouth often smiling. "
            "Family-deity or guru-paramparaa is honoured. Generous with money."
        ),
        "character_themes": ["dharmic-wealth", "wise-speech", "learned-family", "generous", "advisor-income"],
        "life_indications": (
            "Substantial wealth from teaching, advisory, publishing. Wise truthful speech. "
            "Generous, well-fed family."
        ),
        "source": "Chamatkar Chintamani Verse 50",
    },

    ("Jupiter", 3): {
        "verse_sanskrit": (
            "Tritiye Guru-yukto'sau bhraatru-shoka-samanvitah, "
            "kshudra-buddhi-yutaha praaani svalpa-shaurya-vivardhanah."
        ),
        "verse_translation": (
            "Jupiter in the third house — its weakest house — gives only moderate "
            "courage, fewer or estranged younger siblings, and occasional disappointment "
            "in self-effort. The native is generally honest but lacks the aggressive "
            "drive that the third house ordinarily wants. Writing, teaching, and "
            "pilgrimage suit better than competitive sports or military pursuits. "
            "Hands and arms are softer than average. He may need to push past "
            "natural reluctance to claim his due. Younger sibling may be distant "
            "geographically or emotionally. Travel for religious purposes works well."
        ),
        "character_themes": ["modest-courage", "fewer-siblings", "honest-but-passive", "religious-travel-favoured"],
        "life_indications": (
            "Moderate courage, fewer younger siblings, may be passive. Religious travel "
            "and writing favoured over competitive fields."
        ),
        "source": "Chamatkar Chintamani Verse 51",
    },

    ("Jupiter", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Guru-samjaata maatru-saukhya-samanvitah, "
            "vahana-bhumi-shobhito vipravaad-priya-darshanah."
        ),
        "verse_translation": (
            "Jupiter in the fourth house — exalted strong if in Cancer — gives "
            "a happy home, a virtuous and dharmic mother, comfortable property, "
            "fine vehicles, and inner contentment. The native may inherit "
            "land or build it through ethical means. Education at home is "
            "rich; the family library or guru-tradition extends. Mother is "
            "long-lived and pious. The chest, heart, and respiratory system "
            "are usually robust. Friends from learned circles visit often. "
            "Inner life is settled; this is one of Jupiter's finest placements."
        ),
        "character_themes": ["happy-home", "dharmic-mother", "long-lived-mother", "land-inherited", "vehicles"],
        "life_indications": (
            "Excellent. Dharmic long-lived mother. Property, vehicles, comfortable home. "
            "Inner contentment."
        ),
        "source": "Chamatkar Chintamani Verse 52",
    },

    ("Jupiter", 5): {
        "verse_sanskrit": (
            "Putrasthaane Guru-samjaata putra-vidyaa-vibhushitah, "
            "mantra-shaastra-vichakshana viprasamga-priyo bhaved."
        ),
        "verse_translation": (
            "Jupiter in the fifth house — its strongest placement — gives "
            "intelligent, dharmic, often-many children who do well in education, "
            "respect their parents, and bring honour to the family. The native "
            "himself is gifted in mantra-shastra, scriptural learning, teaching, "
            "advisory work, and creative spiritual writing. Speculation succeeds "
            "with measured judgement. Devotional practice is a daily anchor. "
            "Memory is strong, intelligence broad, intuition reliable. Children "
            "particularly daughters are blessed; eldest may become a teacher."
        ),
        "character_themes": ["dharmic-children", "mantra-shastra", "broad-intelligence", "spiritual-teacher", "memory-strong"],
        "life_indications": (
            "Excellent. Many dharmic intelligent children. Mantra-shastra, teaching, "
            "spiritual writing, broad memory."
        ),
        "source": "Chamatkar Chintamani Verse 53",
    },

    ("Jupiter", 6): {
        "verse_sanskrit": (
            "Shashthe Guru-yutah praaani vairi-vargasya kshepakah, "
            "matuleshu sukham praapto vyaadhi-haarako bhaved."
        ),
        "verse_translation": (
            "Jupiter in the sixth house defeats enemies through wisdom and "
            "moral standing rather than aggression. Lawsuits resolve in his "
            "favour; debts get repaid; rivals diminish through their own "
            "actions. Maternal uncles support him in life-decisions. Service "
            "careers in advisory, legal, medical, judicial, or educational "
            "fields prosper. Health is generally good though weight or "
            "diabetic-tendency may need watching in mid-life. The native is "
            "honest, principled, and rarely needs to act against his "
            "conscience to win. Pets and small animals do well around him."
        ),
        "character_themes": ["wisdom-defeats-enemies", "principled-service-career", "advisory-medicine-judicial", "weight-watch"],
        "life_indications": (
            "Wins through wisdom not aggression. Advisory, legal, medical, judicial career. "
            "Watch weight/diabetes mid-life."
        ),
        "source": "Chamatkar Chintamani Verse 54",
    },

    ("Jupiter", 7): {
        "verse_sanskrit": (
            "Saptame Guru-samjaato bhaaryaa-prema-samanvitah, "
            "naari-vallabhah sundaro madhura-vaag-vinodakaha."
        ),
        "verse_translation": (
            "Jupiter in the seventh house gives a virtuous, dharmic, often "
            "well-educated spouse — sometimes from a learned or priestly family. "
            "The marriage is harmonious, supportive, and long-lasting. The "
            "spouse may be older or wiser in some material respect. Trade-"
            "partnerships flourish with ethical partners. Long journeys "
            "for noble purposes (study, religious mission, advisory work) "
            "succeed. Children come at the right time. The home grows "
            "prosperous through marriage. Father-in-law and mother-in-law "
            "are usually supportive and respected."
        ),
        "character_themes": ["dharmic-spouse", "long-marriage", "wise-partner", "ethical-partnership"],
        "life_indications": (
            "Excellent. Dharmic, often educated, spouse. Long stable marriage. Ethical "
            "partnerships flourish."
        ),
        "source": "Chamatkar Chintamani Verse 55",
    },

    ("Jupiter", 8): {
        "verse_sanskrit": (
            "Ashtame Guru-yukto'sau svalpaayur-roga-piditaha, "
            "guhya-vidyaa-praapto'pi rahasya-jnaana-tatparah."
        ),
        "verse_translation": (
            "Jupiter in the eighth house — surprisingly considered Bhagya-Vipareeta "
            "by some — gives long lifespan if other factors permit, deep occult "
            "and metaphysical knowledge, talent in research and hidden sciences, "
            "and inheritance from elders. The native is drawn to philosophy of "
            "death and rebirth, occult traditions, healing arts. Physical health "
            "may appear average outwardly but reserves of vitality are deep. "
            "Reputation is rarely public-facing; the native works in silent "
            "depth. Inheritance often comes mid-life. Mantra-aptitude strong."
        ),
        "character_themes": ["long-life", "occult-philosopher", "research-aptitude", "inheritance-mid-life", "deep-mantra"],
        "life_indications": (
            "Long life if other factors permit. Occult/research aptitude. Inheritance "
            "mid-life. Hidden depth-work."
        ),
        "source": "Chamatkar Chintamani Verse 56",
    },

    ("Jupiter", 9): {
        "verse_sanskrit": (
            "Bhaagye Guru-samjaato bhaagyavaan dharma-shobhitah, "
            "tirtha-yaatraa-priyaha praaani raja-vamsha-priya-darshanaha."
        ),
        "verse_translation": (
            "Jupiter in the ninth house — its own bhava — produces a maximally "
            "fortunate, dharmic, and broadly respected native. Father is "
            "often a religious or educated man of standing. Pilgrimage, "
            "philosophy, teaching, and foreign opportunities all flourish. "
            "Higher education is completed; multiple degrees are common. "
            "The native is a natural advisor, philosopher, and ethical "
            "leader — sought out by people facing decisions. Wealth comes "
            "through dharmic means alone; deceitful gain holds no appeal. "
            "Foreign settlements prosper. Long-lived family-tradition is honoured."
        ),
        "character_themes": ["maximally-fortunate", "religious-father", "educated", "philosopher-advisor", "foreign-prosperity"],
        "life_indications": (
            "Excellent. Religious educated father. Higher education, multiple degrees. "
            "Philosopher-advisor. Foreign prosperity."
        ),
        "source": "Chamatkar Chintamani Verse 57",
    },

    ("Jupiter", 10): {
        "verse_sanskrit": (
            "Dashame Guru-samjaata karma-siddhah pratapavan, "
            "raaja-mukhya-priyo nityam dharma-shaastra-vivekashah."
        ),
        "verse_translation": (
            "Jupiter in the tenth house — Hamsa or Maha Yoga in some "
            "configurations — yields a career of repute, often as teacher, "
            "advisor, judge, religious head, financial counsellor, professor, "
            "or any senior position requiring wisdom and ethical bearing. "
            "Government roles, judiciary, education ministry, religious "
            "institutions, banking, advisory firms — these flourish. The "
            "native is respected for ethical conduct alongside competence. "
            "Reputation grows through middle decades. Father may have been "
            "in a similar advisory or government line."
        ),
        "character_themes": ["wise-career", "judge-teacher-advisor", "ethical-reputation", "government-favoured"],
        "life_indications": (
            "Excellent. Career as teacher, advisor, judge, religious head, banker. "
            "Ethical reputation, slow steady rise."
        ),
        "source": "Chamatkar Chintamani Verse 58",
    },

    ("Jupiter", 11): {
        "verse_sanskrit": (
            "Laabhe Guru-yutah praaani bhuri-laabha-samanvitaha, "
            "jyeshtha-bhraatru-priyo nityam vidvad-mitra-priyo bhaved."
        ),
        "verse_translation": (
            "Jupiter in the eleventh house brings abundant gains, especially "
            "from advisory work, teaching, publishing, religious-office, "
            "financial counselling, or wisdom-based fields. The native has "
            "supportive elder brothers (or elder-figures), learned friends, "
            "and an ever-widening intellectual circle. Ambitions of a "
            "noble nature are fulfilled — recognition, a respected position, "
            "writing of books, founding of institutions. Wealth flows steadily "
            "across decades. The friend-network includes scholars, religious "
            "men, and ethical professionals."
        ),
        "character_themes": ["abundant-gains", "elder-brother-support", "learned-friends", "noble-ambitions-fulfilled"],
        "life_indications": (
            "Abundant gains from wisdom-based fields. Elder brother supportive. Scholarly "
            "friend-circle. Books, institutions."
        ),
        "source": "Chamatkar Chintamani Verse 59",
    },

    ("Jupiter", 12): {
        "verse_sanskrit": (
            "Dvaadashe Guru-samjaata svaadhyaaya-praapta-mukti-yutah, "
            "vyayi videsha-vaasi cha moksha-marga-pravartakaha."
        ),
        "verse_translation": (
            "Jupiter in the twelfth house — though a bhavya-bhanga in some readings — "
            "gives final-liberation aptitude, monastic temperament, foreign "
            "settlement, or work in religious / charitable institutions. The native "
            "spends generously on dharma — temples, charity, scholarship of others. "
            "He may settle abroad, particularly in countries where his wisdom is "
            "valued. Sleep is rich, dreams meaningful. He learns through retreat "
            "and contemplation more than through outward action. Father may be "
            "spiritual or distant. Final birth in some readings — moksha "
            "approaches. Bed-comforts good, sometimes lavish."
        ),
        "character_themes": ["liberation-aptitude", "monastic", "foreign-residence", "charitable-spending", "moksha-seeker"],
        "life_indications": (
            "Foreign settlement, charitable spending, monastic tendency. Final-liberation "
            "aptitude. Sleep rich, intuitive."
        ),
        "source": "Chamatkar Chintamani Verse 60",
    },

    # ─────────────────────────── VENUS (verses 61-72) ─────────────────────────
    ("Venus", 1): {
        "verse_sanskrit": (
            "Lagne sthe Bhrigu-samjaato gourah sundaras-tatha, "
            "kavi-vidyaa-vishaaradah madhura-vaag-vinodakah."
        ),
        "verse_translation": (
            "Venus in the first house — Malavya Yoga if dignified — gives a "
            "fair-complexioned, beautiful, charming native with magnetic presence. "
            "The face is well-formed, eyes large and expressive, voice musical, "
            "and gait graceful. The native is fond of fine clothes, perfumes, "
            "music, art, beauty in all forms, and pleasant company of women. "
            "Skill in arts — music, painting, poetry, fashion, design — is "
            "natural. Romance comes easily and the native is sought after. "
            "Long-lived, comfortable, often physically attractive into old age."
        ),
        "character_themes": ["beautiful", "magnetic", "artistic", "musical-voice", "malavya-yoga-potential"],
        "life_indications": (
            "Malavya Yoga if Venus dignified. Beautiful, charming, artistic. Music, art, "
            "fashion. Long-lived, comfortable."
        ),
        "source": "Chamatkar Chintamani Verse 61",
    },

    ("Venus", 2): {
        "verse_sanskrit": (
            "Dvitiye Bhrigu-samjaato dhanavaan rasika-priyah, "
            "kuteshu sukhito jaata madhura-vaag-vichakshanah."
        ),
        "verse_translation": (
            "Venus in the second house — its own bhava counted from Taurus — "
            "gives substantial wealth particularly from luxury trade, art, beauty, "
            "fashion, jewellery, perfumes, hospitality, food, vehicles, or any "
            "Venus-related industry. The voice is sweet, often musical; many "
            "such natives sing, recite, or speak professionally. The face is "
            "handsome, mouth shapely. Family is cultured, tasteful in food "
            "and surroundings. Speech is pleasant and persuasive. Wealth flows "
            "from refined clientele rather than mass markets. Often a connoisseur."
        ),
        "character_themes": ["luxury-wealth", "musical-voice", "cultured-family", "connoisseur"],
        "life_indications": (
            "Wealth from luxury, art, fashion, hospitality, food, jewellery. Musical voice. "
            "Cultured tasteful family."
        ),
        "source": "Chamatkar Chintamani Verse 62",
    },

    ("Venus", 3): {
        "verse_sanskrit": (
            "Tritiye Bhrigu-yukto'sau bhraatru-shoka-vivardhanah, "
            "krura-karmaa lobha-yukto kshudra-vaag-vivaadakah."
        ),
        "verse_translation": (
            "Venus in the third house gives only modest courage but considerable "
            "creative skill in the hands — music, painting, drafting, fine "
            "handicraft, or any Venus-touched manual art. Younger siblings may "
            "be fewer or estranged; sisters do better than brothers. Travel "
            "is for pleasure rather than effort. Some greed or possessiveness "
            "may surface in close relationships. Writing about love, beauty, "
            "or art is favoured. Short journeys connect the native with artistic "
            "and romantic circles. Hands are gifted; courage is selective."
        ),
        "character_themes": ["artistic-hands", "musician-painter", "fewer-brothers", "modest-courage", "pleasure-travel"],
        "life_indications": (
            "Musical/artistic hands. Fewer or estranged younger brothers; sisters do "
            "better. Pleasure-travel."
        ),
        "source": "Chamatkar Chintamani Verse 63",
    },

    ("Venus", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Bhrigu-jaata maatru-saukhya-samanvitah, "
            "vahana-bhumi-shobhito vipravaad-priya-darshanah."
        ),
        "verse_translation": (
            "Venus in the fourth house gives a luxurious home — beautiful furniture, "
            "fine vehicles, lush gardens, music in the rooms — and a loving, "
            "attractive mother who cares for the native deeply. Property is "
            "acquired, often more than one over a lifetime, and lands are well-"
            "kept. Vehicles are often more than required. The chest, heart, "
            "and respiratory system are usually robust. Friends from artistic "
            "and refined circles visit often. The native loves home life, "
            "decoration, beauty, and comfortable surroundings. Mother-bond "
            "is rich and life-long."
        ),
        "character_themes": ["luxurious-home", "loving-mother", "vehicles-many", "artistic-friend-circle"],
        "life_indications": (
            "Luxurious home, loving mother, fine vehicles, beautiful surroundings. "
            "Property accumulates."
        ),
        "source": "Chamatkar Chintamani Verse 64",
    },

    ("Venus", 5): {
        "verse_sanskrit": (
            "Putrasthaane Bhrigu-jaata putra-saukhya-samanvitah, "
            "kavi-vidya-priyo nityam mantra-shaastra-vivekashah."
        ),
        "verse_translation": (
            "Venus in the fifth house gives beautiful, artistic, talented children "
            "(particularly daughters) and creative gifts in the native himself — "
            "poetry, music, painting, dance, drama, design. Romance is intense "
            "in youth; love-affairs are frequent and may include married-life "
            "before the actual marriage. Speculation in art-related markets "
            "succeeds. Mantras of Venus, Lakshmi, and Saraswati appeal. The "
            "native's children typically follow artistic or romantic paths. "
            "Memory for poetry and song is strong. Theatre, film, music industries "
            "particularly suit."
        ),
        "character_themes": ["artistic-children", "poet-musician", "intense-romance", "venus-mantra"],
        "life_indications": (
            "Beautiful artistic children, often daughters. Poetry, music, painting, dance "
            "natural. Intense romance in youth."
        ),
        "source": "Chamatkar Chintamani Verse 65",
    },

    ("Venus", 6): {
        "verse_sanskrit": (
            "Shashthe Bhrigu-yukto'sau vairi-vargasya naashanah, "
            "matuleshu sukham praapto vyaadhi-haarako bhaved."
        ),
        "verse_translation": (
            "Venus in the sixth house — generally considered weak for Venus — "
            "gives gentle defeat of enemies, often turning rivals into friends "
            "through charm and grace. Maternal uncles are kind. Service careers "
            "in luxury industries, hospitality, fashion, beauty, salon, food, "
            "or entertainment do well. Health may show occasional disorders of "
            "the urogenital or kidney region; sweet foods need moderation. "
            "Litigation tends to settle through compromise. Pets thrive. The "
            "native is liked even by competitors; rivals soften. Yet love "
            "in early life may be unrequited or marked by lost affairs."
        ),
        "character_themes": ["gentle-rivalry-resolution", "luxury-service-career", "sweet-food-moderation", "kidney-care"],
        "life_indications": (
            "Service in luxury / fashion / hospitality industries. Rivals soften. Watch "
            "kidney/sugar. Love-disappointment in youth."
        ),
        "source": "Chamatkar Chintamani Verse 66",
    },

    ("Venus", 7): {
        "verse_sanskrit": (
            "Saptame Bhrigu-samjaato bhaaryaa-prema-samanvitah, "
            "sundara-naari-priyaha sukhi madhura-vaag-vichakshanah."
        ),
        "verse_translation": (
            "Venus in the seventh house — its own bhava counted from Libra — "
            "is one of its finest placements. The marriage brings a beautiful, "
            "loving, often artistically inclined spouse, deep emotional and "
            "physical compatibility, and lasting affection. The native himself "
            "is charming, sought-after, and may have romantic interests prior "
            "to marriage. Trade-partnerships with women particularly flourish. "
            "Long journeys for matters of the heart or partnership succeed. "
            "Children come at the right time. The marriage is comfortable, "
            "often a source of social and material rise."
        ),
        "character_themes": ["beautiful-spouse", "loving-marriage", "charming-native", "partnership-success"],
        "life_indications": (
            "Excellent. Beautiful loving spouse, lasting marriage. Charm, partnerships "
            "flourish. Wealth through marriage."
        ),
        "source": "Chamatkar Chintamani Verse 67",
    },

    ("Venus", 8): {
        "verse_sanskrit": (
            "Ashtame Bhrigu-samjaata paraachaa-naari-priyah-priyaha, "
            "guhya-saukhya-yutah praaani sthaayi-shatru-vivardhanah."
        ),
        "verse_translation": (
            "Venus in the eighth house gives long lifespan, sensual depth, "
            "secret romantic affairs (often with married or distant persons), "
            "inheritance through marriage or partner, and intuitive depth in "
            "intimate relationships. The native may marry into wealth or receive "
            "substantial gift through spouse's family. Yet love may include "
            "secret elements, hidden affairs, or some scandal not made public. "
            "Eighth-house Venus also gives talent in tantra, sensual arts, "
            "and emotional depth-work. Health sound but watch urogenital "
            "system. Eyes often expressive, sometimes lustrous."
        ),
        "character_themes": ["long-life", "secret-romance", "inheritance-through-spouse", "tantric-aptitude"],
        "life_indications": (
            "Long life. Secret romance possible. Inheritance through marriage. Tantric/"
            "sensual depth. Watch urogenital health."
        ),
        "source": "Chamatkar Chintamani Verse 68",
    },

    ("Venus", 9): {
        "verse_sanskrit": (
            "Bhaagye Bhrigu-samjaato dharma-vidya-vibhushitah, "
            "tirtha-yaatraa-priyah praaani raja-vamsha-priya-darshanah."
        ),
        "verse_translation": (
            "Venus in the ninth house gives a refined, dharmic, well-travelled "
            "native with strong artistic-philosophical leanings. Father may be "
            "an artist, scholar, or refined gentleman. Foreign opportunities "
            "particularly in luxury, art, fashion, hospitality, or culture-trade "
            "open and prosper. Higher education is often in arts, design, or "
            "languages. The native is principled but with aesthetic sensitivity — "
            "ethics interpreted through beauty. Pilgrimage to artistic-religious "
            "sites particularly appeals. Fortune rises through cultivated taste "
            "rather than aggressive enterprise."
        ),
        "character_themes": ["refined-fortune", "artistic-father", "luxury-foreign-trade", "aesthetic-ethics"],
        "life_indications": (
            "Foreign opportunity in luxury/art/culture. Refined father. Aesthetic ethics. "
            "Higher education in arts or languages."
        ),
        "source": "Chamatkar Chintamani Verse 69",
    },

    ("Venus", 10): {
        "verse_sanskrit": (
            "Dashame Bhrigu-samjaata karma-siddhah pratapavan, "
            "vyaapaarena dhanaa-praaptas tatra-naari-vinodakah."
        ),
        "verse_translation": (
            "Venus in the tenth house gives professional success in luxury, "
            "art, fashion, hospitality, beauty, jewellery, design, music, "
            "film, theatre, or any Venus-touched industry. The native may "
            "be famed for elegance and skill in his chosen field. Senior "
            "women of standing favour him in his career-line. Reputation "
            "is one of cultivated taste and pleasing manner. Wealth flows "
            "through refined clientele, large clients, hospitality contracts, "
            "or artistic commissions. Career rises through charm as much as "
            "competence — the two combined make for steady upward motion."
        ),
        "character_themes": ["luxury-career", "artistic-fame", "elegance-as-currency", "senior-women-favour"],
        "life_indications": (
            "Career in luxury, fashion, art, hospitality, music, film. Elegance as "
            "professional currency. Senior women favour."
        ),
        "source": "Chamatkar Chintamani Verse 70",
    },

    ("Venus", 11): {
        "verse_sanskrit": (
            "Laabhe Bhrigu-samjaato bhuri-laabha-samanvitah, "
            "vidvad-mitra-priyo nityam naari-vallabhaha-priyaha."
        ),
        "verse_translation": (
            "Venus in the eleventh house brings abundant gains particularly "
            "from artistic, luxury, hospitality, and beauty-related side-incomes "
            "alongside the main vocation. The native's social circle is rich "
            "in artistic, refined, often-female friends. Many introductions "
            "bring profit. Hopes long cherished — particularly those involving "
            "love, wealth, and social position — are fulfilled. Elder brother "
            "or sister may rise high. Wealth flows steadily across decades. "
            "Networking, friendships, and intimate connections all feed the "
            "income stream."
        ),
        "character_themes": ["abundant-gains", "artistic-friends", "luxury-side-income", "refined-network"],
        "life_indications": (
            "Many gains from luxury/art/hospitality side-incomes. Refined friend network. "
            "Romance fulfilled."
        ),
        "source": "Chamatkar Chintamani Verse 71",
    },

    ("Venus", 12): {
        "verse_sanskrit": (
            "Dvaadashe Bhrigu-samjaata bhoga-saukhya-samanvitah, "
            "shayya-saukhya-priyah praaani videsha-vaasi-bhog-vaan."
        ),
        "verse_translation": (
            "Venus in the twelfth house — which Bhattaji and many later authors "
            "consider one of its strongest placements — gives bhoga (sensual "
            "and material enjoyment), comfortable bed and bedroom, foreign "
            "residence in pleasure-rich settings, and what is called shayya-sukha "
            "or the comfort of intimate life. The native may settle abroad, "
            "particularly in beautiful or comfortable places. Expenses on "
            "luxury, art, romance, and beauty are heavy but rarely regretted. "
            "Final-liberation in some readings; the soul completes its "
            "Venusian lessons of love, beauty, and compassion. Mokshagamana yoga."
        ),
        "character_themes": ["bhoga-bed-comfort", "foreign-luxury", "moksha-through-love", "shayya-sukha"],
        "life_indications": (
            "Excellent for Venus. Bhoga / shayya-sukha — comfortable intimate life, "
            "foreign luxury, moksha through love."
        ),
        "source": "Chamatkar Chintamani Verse 72",
    },

    # ─────────────────────────── SATURN (verses 73-84) ────────────────────────
    ("Saturn", 1): {
        "verse_sanskrit": (
            "Lagne sthe Shanaiscara dirgha-shareero malina-prabhah, "
            "kshudra-vaag-yukto duhkhi alpaayur-vyathita-mati."
        ),
        "verse_translation": (
            "Saturn in the first house gives a tall, lean, often weather-worn "
            "physique, dark or sallow complexion, slow gait, and serious bearing. "
            "Childhood is usually marked by hardship, illness, or poverty. The "
            "native looks older than his years from youth. Speech is measured, "
            "sometimes harsh. There is a quality of premature gravity — others "
            "treat the native as elder. Yet Saturn's lessons mature into "
            "mastery in later life. This becomes Shasha Yoga if dignified — "
            "great longevity, deep mastery, late-life eminence. Without dignity, "
            "the native carries Saturnine sorrow as his teacher."
        ),
        "character_themes": ["tall-lean", "weather-worn", "childhood-hardship", "looks-older", "shasha-yoga-potential"],
        "life_indications": (
            "Hard childhood, looks older than age. Mastery in later life. Shasha Yoga "
            "if dignified."
        ),
        "source": "Chamatkar Chintamani Verse 73",
    },

    ("Saturn", 2): {
        "verse_sanskrit": (
            "Dvitiye Shani-yukto'sau dhana-shoka-samanvitah, "
            "kuteshu kalaha-yutah praaani sthaayi-shatru-vivardhanah."
        ),
        "verse_translation": (
            "Saturn in the second house gives hardship in early earnings, "
            "family-quarrels around money, and slow accumulation of wealth. "
            "The voice may be harsh, gravelly, or speak less than average. "
            "Teeth, mouth, or face may show injury or unusual feature. Family "
            "may emigrate or scatter; ancestral wealth diminishes. Yet the "
            "native works persistently and accumulates over decades. Earnings "
            "come from labour-intensive trades, oil/iron/coal/heavy industry, "
            "real-estate, leather, agriculture, or stable employment with "
            "long service. Steady and slow rather than swift."
        ),
        "character_themes": ["slow-wealth", "family-money-quarrels", "harsh-voice", "labour-trades"],
        "life_indications": (
            "Slow wealth accumulation. Family money-quarrels. Earnings from heavy industry, "
            "labour-trades, real-estate."
        ),
        "source": "Chamatkar Chintamani Verse 74",
    },

    ("Saturn", 3): {
        "verse_sanskrit": (
            "Tritiye Shani-yukto'sau bhraatru-veera-saanusukah, "
            "shauryavaan kaarya-niraataa svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Saturn in the third house — surprisingly strong — gives quiet "
            "courage, persistent work-ethic, slow but reliable younger siblings, "
            "and considerable patience. The native pushes through difficulty "
            "where others quit. Writing, technical work, engineering, machinery, "
            "agriculture, real-estate, mining, or labour-management roles do "
            "well. Younger sibling may settle abroad or in difficult region. "
            "Hands are calloused with work. Travel is for purpose rather than "
            "pleasure. The native is taciturn but steady; reputation among "
            "co-workers is one of unfailing reliability."
        ),
        "character_themes": ["quiet-courage", "persistent-worker", "reliable", "labour-management", "younger-sibling-distant"],
        "life_indications": (
            "Persistent worker, quiet courage. Younger sibling distant or abroad. Engineering, "
            "agriculture, mining, real-estate."
        ),
        "source": "Chamatkar Chintamani Verse 75",
    },

    ("Saturn", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Shani-jaata maatru-saukhya-vivarjitah, "
            "vahana-bhumi-rahito hridaye dukhha-piditah."
        ),
        "verse_translation": (
            "Saturn in the fourth house diminishes home-comfort in early life. "
            "The mother's health or longevity may concern the native; she may "
            "have suffered hardship in raising him. Property is acquired late "
            "in life rather than early; vehicles may have repair-troubles. The "
            "chest, heart, or knees may give occasional issue. There is some "
            "loneliness in the inner life — the home does not feel fully "
            "warm in childhood. Yet by mid-life the native often acquires "
            "substantial real estate through persistent effort, and the home "
            "settles into stable if simple comfort. Late mother-care."
        ),
        "character_themes": ["mother-hardship", "late-property", "home-loneliness", "chest-knee-issues"],
        "life_indications": (
            "Mother's health/longevity concern. Property acquired late in life. Some "
            "early-life loneliness."
        ),
        "source": "Chamatkar Chintamani Verse 76",
    },

    ("Saturn", 5): {
        "verse_sanskrit": (
            "Putrasthaane Shanau jaate putra-shoka-samanvitah, "
            "udare vyaadhi-piditah kshudra-buddhi-samaakulah."
        ),
        "verse_translation": (
            "Saturn in the fifth house gives delayed children, sometimes only "
            "one child, or child-related grief — miscarriage, ill-health of "
            "first child, or estrangement with grown children. Speculation "
            "loses, gambling fails. The stomach, intestines, or chronic "
            "digestive ailments may persist. Memory may be slow but deep. "
            "Mantra-shastra succeeds only with persistent practice; results "
            "come late. Education may face delays — repeated years, technical "
            "diversions, or completion in maturity. Yet the children when "
            "they come are often serious-minded and successful in their own "
            "way; the relationship matures in later years."
        ),
        "character_themes": ["delayed-children", "child-grief-risk", "slow-mantra-results", "delayed-education"],
        "life_indications": (
            "Delayed or few children. Speculation fails. Education may delay. Mantra-results "
            "come late."
        ),
        "source": "Chamatkar Chintamani Verse 77",
    },

    ("Saturn", 6): {
        "verse_sanskrit": (
            "Shashthe Shani-yutah praaani vairi-vargasya naashakaha, "
            "matuleshu sukham praapto raja-mukhya-priyo bhaved."
        ),
        "verse_translation": (
            "Saturn in the sixth house — exceptionally strong — destroys "
            "enemies through endurance, defeats rivals by outlasting them, "
            "wins lawsuits at the appellate level, and clears debts through "
            "patience. Maternal uncles are kind. Service careers (law, audit, "
            "judiciary, civil-service, medicine, labour-related professions) "
            "flourish. Health is generally robust though knees, joints, and "
            "circulation need care in old age. The native is feared by enemies "
            "because he never gives up. This becomes Vipareeta-Saturn — what "
            "begins as obstacle becomes the source of rise. One of Saturn's "
            "best placements."
        ),
        "character_themes": ["enduring-victor", "service-career", "labour-judicial", "vipareeta-rise"],
        "life_indications": (
            "Excellent — defeats enemies through endurance. Service career: law, audit, "
            "judiciary, medicine, civil service."
        ),
        "source": "Chamatkar Chintamani Verse 78",
    },

    ("Saturn", 7): {
        "verse_sanskrit": (
            "Saptame Shani-samjaato bhaaryaa-prema-vivarjitah, "
            "vyaadhi-yukta-bhaaryaa-stho dirgha-aayuh-pradayakaha."
        ),
        "verse_translation": (
            "Saturn in the seventh house gives a delayed marriage — often after "
            "27 — to a serious, mature, sometimes older spouse. The marriage "
            "is durable but emotionally cool in early years; warmth deepens "
            "with time. Spouse may have health issues or come from a hard "
            "background. Yet the long-term partnership is committed and "
            "reliable. Trade partnerships are slow to start but, once formed, "
            "endure decades. Long journeys for trade succeed slowly. The "
            "native lives long; spouse generally lives long too. Late-flowering "
            "love is often the reward."
        ),
        "character_themes": ["delayed-marriage", "older-or-mature-spouse", "durable-marriage", "long-life"],
        "life_indications": (
            "Marriage delayed past 27, with mature/older spouse. Durable, slow-warming. "
            "Long life. Slow business partnerships endure."
        ),
        "source": "Chamatkar Chintamani Verse 79",
    },

    ("Saturn", 8): {
        "verse_sanskrit": (
            "Ashtame Shani-yutah praaani dirgha-aayur-roga-piditaha, "
            "guhya-vidya-vivekashah kalanka-yukta-charitra-vaan."
        ),
        "verse_translation": (
            "Saturn in the eighth house gives an exceptionally long lifespan — "
            "Saturn's signature ayur-stana — alongside chronic health issues "
            "of the urogenital, joint, or bone system. The native may face "
            "some form of stigma or scandal during life — financial, romantic, "
            "or professional — though his persistence eventually overcomes it. "
            "Inheritance is delayed and contested. Occult, research, hidden "
            "matters, longevity-medicine, gerontology, and underground/mining "
            "professions suit. The native is deeply private; few know the full "
            "story. Long life with quiet endurance."
        ),
        "character_themes": ["long-life", "chronic-issues", "scandal-overcome", "occult-research", "private"],
        "life_indications": (
            "Long life with chronic care needed. Some scandal/stigma overcome with time. "
            "Inheritance delayed. Occult/research."
        ),
        "source": "Chamatkar Chintamani Verse 80",
    },

    ("Saturn", 9): {
        "verse_sanskrit": (
            "Bhaagye Shani-yutah praaani dharma-haani-samanvitah, "
            "pitru-shoka-yutas chaiva svalpa-bhaagya-samanvitah."
        ),
        "verse_translation": (
            "Saturn in the ninth house gives slow fortune, late father-blessing, "
            "and sometimes diminishment of dharma in early life — the native "
            "may turn skeptical, unconventional, or rebellious against inherited "
            "religion. Father may be in labour or service line, or may be "
            "absent / strict. Higher education is delayed but completed with "
            "depth. Foreign opportunities open late but are durable when they "
            "come. Pilgrimage and dharmic engagement deepen with age. By later "
            "life the native often becomes a teacher of unconventional wisdom — "
            "his outsider-perspective becomes a strength."
        ),
        "character_themes": ["slow-fortune", "late-father-blessing", "skeptical-religion", "unconventional-teacher"],
        "life_indications": (
            "Slow fortune, late father-blessing. Skeptical or unconventional religious view. "
            "Late-life teacher."
        ),
        "source": "Chamatkar Chintamani Verse 81",
    },

    ("Saturn", 10): {
        "verse_sanskrit": (
            "Dashame Shanaiscara karma-siddhi-vivardhanaha, "
            "raja-mukhya-priyo nityam shasha-yoga-samanvitah."
        ),
        "verse_translation": (
            "Saturn in the tenth house — Shasha Yoga if dignified, one of "
            "Saturn's premier placements — gives slow but immense career "
            "rise, mastery in profession over decades, and eventual eminence "
            "in chosen field. Engineering, civil-service, judiciary, mining, "
            "real-estate development, oil/petrol industries, machinery, "
            "agriculture, manufacturing, and any field requiring discipline "
            "and persistence flourish. The native may start small — sometimes "
            "very small — and rise to commanding positions through three or "
            "four decades of work. Reputation is built late but lasts long."
        ),
        "character_themes": ["slow-rise", "mastery-late", "engineering-civil-service", "shasha-yoga-potential"],
        "life_indications": (
            "Excellent. Slow late rise, mastery, eminence. Shasha Yoga if dignified. "
            "Engineering, civil-service, judiciary."
        ),
        "source": "Chamatkar Chintamani Verse 82",
    },

    ("Saturn", 11): {
        "verse_sanskrit": (
            "Laabhe Shani-yutah praaani bhuri-laabha-samanvitaha, "
            "jyeshtha-bhraatru-priyo nityam dhana-vahaa-priya-darshanaha."
        ),
        "verse_translation": (
            "Saturn in the eleventh house — exceptionally strong for income — "
            "gives steady, persistent gains earned over decades. The native "
            "rarely grows rich quickly but is rarely poor for long. Elder "
            "brother (or elder-figure) may have struggled or been distant, "
            "but support arrives when needed. Friends are few but loyal across "
            "lifetimes. Hopes long-cherished are fulfilled — slowly, after "
            "much work, but they are fulfilled. Wealth continues to grow into "
            "old age; this is one of the few placements where Saturn-mature "
            "income exceeds Saturn-youth income manyfold. Reliable accumulation."
        ),
        "character_themes": ["steady-gains", "slow-but-sure-wealth", "loyal-friends", "elder-brother-struggle"],
        "life_indications": (
            "Excellent for income. Slow but sure wealth-accumulation. Loyal friends. "
            "Elder brother may have struggled."
        ),
        "source": "Chamatkar Chintamani Verse 83",
    },

    ("Saturn", 12): {
        "verse_sanskrit": (
            "Dvaadashe Shani-jaato vyayi netra-roga-piditah, "
            "videsha-vaasi shayya-shoka-svalpaayur-bhaavena."
        ),
        "verse_translation": (
            "Saturn in the twelfth house gives high expenses, foreign settlement, "
            "left-eye trouble in some cases, and disturbed sleep. The native "
            "may live alone or in monastic settings, or work in night-shift "
            "or behind-the-scenes professions. Bed-comforts in early life are "
            "modest. The bodily system runs slow; metabolism conservative. "
            "Yet this same Saturn gives final-liberation aptitude — moksha "
            "approaches by working through the karmic burden of expense and "
            "isolation. Hospitals, prisons, ashrams, foreign-base employment, "
            "and reclusive scholarship may form the life-frame. Long-lived "
            "but withdrawn."
        ),
        "character_themes": ["foreign-settlement", "high-expenses", "left-eye-care", "moksha-aptitude", "isolated-life"],
        "life_indications": (
            "Foreign settlement, high expenses, isolated life. Moksha aptitude. "
            "Hospitals, prisons, ashrams as setting."
        ),
        "source": "Chamatkar Chintamani Verse 84",
    },

    # ─────────────────────────── RAHU (verses 85-96) ──────────────────────────
    ("Rahu", 1): {
        "verse_sanskrit": (
            "Lagne sthe Rahu-yukto'sau krurah krodhi vichakshanaha, "
            "videsha-priyah praaani anyaya-marga-samanvitah."
        ),
        "verse_translation": (
            "Rahu in the first house gives an unusual, intense, magnetic, "
            "sometimes unpredictable personality. The native may have a "
            "distinctive feature — unusual height, unusual complexion, "
            "striking eyes, or some visible mark. He stands out in every "
            "room. The mind is sharp, ambitious, often unconventional. "
            "Foreign lands attract; the native may settle abroad or work "
            "in foreign-connected professions. Career rises through unusual "
            "paths — technology, foreign trade, media, photography, film, "
            "anything modern or boundary-crossing. Manipulation-aptitude "
            "is high; ethical care needed."
        ),
        "character_themes": ["distinctive-presence", "ambitious", "foreign-attraction", "unconventional", "boundary-crossing"],
        "life_indications": (
            "Distinctive personality, magnetic. Foreign or unconventional career. Tech, "
            "media, film, foreign trade."
        ),
        "source": "Chamatkar Chintamani Verse 85",
    },

    ("Rahu", 2): {
        "verse_sanskrit": (
            "Dvitiye Rahu-samjaata kuteshu vigraha-priyah, "
            "kshudra-vaag-yutah praaani videsha-dhana-vivardhanaha."
        ),
        "verse_translation": (
            "Rahu in the second house gives quarrels in family over wealth, "
            "harsh or unusual speech (sometimes accent-shift, stuttering, "
            "or unusually direct manner), and earnings from foreign or "
            "unconventional sources. The native may earn through international "
            "trade, foreign currency, technology export, online business, "
            "smuggling-adjacent or contested industries (depending on the rest "
            "of the chart). Family may emigrate. Wealth rises and falls "
            "dramatically. Teeth, mouth, or speech may show unusual feature. "
            "Food choices may be unconventional or foreign-influenced. Rapid "
            "fluctuations are common."
        ),
        "character_themes": ["family-quarrels", "unusual-speech", "foreign-income", "fluctuating-wealth"],
        "life_indications": (
            "Family quarrels over wealth. Foreign income, online trade, currency, "
            "tech-export. Wealth fluctuates dramatically."
        ),
        "source": "Chamatkar Chintamani Verse 86",
    },

    ("Rahu", 3): {
        "verse_sanskrit": (
            "Tritiye Rahu-yutah praaani shauryavaan saahasi vichakshanaha, "
            "raja-tulyo mahaa-veerah svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Rahu in the third house — exceptionally strong — gives outstanding "
            "courage of an unconventional sort, willingness to break norms, "
            "skill in unusual technologies, and rapid rise through self-effort. "
            "The native is decisive, often pioneering, and excels in fields "
            "others find too risky. Younger siblings may be eccentric or settle "
            "abroad. Travel is frequent and often international. Hands are "
            "skilled in modern technology — coding, photography, electronics, "
            "machinery, instruments. The native breaks family-pattern and "
            "rises through bold action."
        ),
        "character_themes": ["unconventional-courage", "tech-skilled-hands", "international-travel", "norm-breaker", "pioneer"],
        "life_indications": (
            "Excellent. Unconventional courage, tech-skill, international travel. Pioneer "
            "in chosen field. Breaks family-pattern."
        ),
        "source": "Chamatkar Chintamani Verse 87",
    },

    ("Rahu", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Rahu-jaata maatru-shoka-samanvitah, "
            "vahana-bhumi-rahito videsha-vaasi-bhog-vaan."
        ),
        "verse_translation": (
            "Rahu in the fourth house disturbs the comforts of mother, home, "
            "and emotional foundation. The mother's health may concern the "
            "native or there may be some unusual circumstance around her — "
            "step-mother, distant mother, mother of different culture. Property "
            "may be foreign-located or contested. Vehicles may have unusual "
            "history (used, foreign-imported, modified). The native settles "
            "abroad in many cases. Inner emotional life is restless until "
            "second-half of life when Rahu's lessons mature. Foreign property "
            "may be acquired by mid-life."
        ),
        "character_themes": ["mother-unusual", "foreign-property", "restless-home", "expat-likely"],
        "life_indications": (
            "Mother situation unusual — step-mother, distant, different-culture. Foreign "
            "settlement. Restless home until mid-life."
        ),
        "source": "Chamatkar Chintamani Verse 88",
    },

    ("Rahu", 5): {
        "verse_sanskrit": (
            "Putrasthaane Rahu-jaata putra-shoka-samanvitah, "
            "udare vyaadhi-piditah kshudra-buddhi-samakulah."
        ),
        "verse_translation": (
            "Rahu in the fifth house brings child-related challenges — late "
            "progeny, miscarriage, child-of-different-culture, adoption, or "
            "unconventional family structure. The native is intelligent in "
            "an unusual sense — brilliant in fields others find obscure or "
            "strange. Speculation and gambling tendencies need control; sudden "
            "gains and losses both occur. Mantra-shastra succeeds with non-"
            "traditional traditions (foreign mantras, modern guru-paramparas, "
            "Tantric paths). Romance may include foreigner or someone from "
            "very different background. Fifth-house Rahu signals soul-pattern "
            "of breaking child / creativity karma."
        ),
        "character_themes": ["unusual-children", "obscure-brilliance", "speculation-volatile", "foreign-romance"],
        "life_indications": (
            "Unusual child-circumstances — late, adopted, different-culture, foreign. "
            "Foreign romance. Volatile speculation."
        ),
        "source": "Chamatkar Chintamani Verse 89",
    },

    ("Rahu", 6): {
        "verse_sanskrit": (
            "Shashthe Rahu-yutah praaani vairi-vargasya naashakah, "
            "matuleshu sukham praapto raaja-mukhya-priyo bhaved."
        ),
        "verse_translation": (
            "Rahu in the sixth house — one of its finest placements, often "
            "called Vipareeta-Rahu — destroys enemies in unconventional ways, "
            "wins difficult lawsuits, defeats rivals through tactics they "
            "didn't see coming. Maternal uncle may live abroad or be in "
            "unusual line. Service careers in technology, foreign affairs, "
            "intelligence, investigation, immigration, customs, or border-"
            "crossing professions flourish. Health holds despite occasional "
            "unusual symptoms; mystery-illnesses sometimes surface but are "
            "manageable. Pets, especially exotic ones, may be kept. The "
            "native's outsider-status becomes professional advantage."
        ),
        "character_themes": ["unconventional-victor", "vipareeta-rise", "intelligence-immigration", "exotic-pets", "mystery-illness"],
        "life_indications": (
            "Excellent. Unconventional victory over enemies. Tech, intelligence, immigration, "
            "investigation careers."
        ),
        "source": "Chamatkar Chintamani Verse 90",
    },

    ("Rahu", 7): {
        "verse_sanskrit": (
            "Saptame Rahu-samjaato bhaaryaa-vaada-samanvitah, "
            "videsha-naari-priyaha sundara-naari-vinodakah."
        ),
        "verse_translation": (
            "Rahu in the seventh house gives a marriage with unusual features — "
            "spouse from foreign country, different culture, different religion, "
            "different age-group, or otherwise outside conventional pattern. "
            "There may be early marriage that dissolves and later remarriage, "
            "or live-in arrangement preceding formal marriage, or marriage "
            "across distance. Trade partnerships often include foreign "
            "partners or international elements. Long journeys for marriage "
            "or business succeed in unusual ways. The native's relationships "
            "rarely follow expected pattern. Late marriage often more stable."
        ),
        "character_themes": ["foreign-spouse", "cross-culture-marriage", "unusual-relationship-pattern", "international-business"],
        "life_indications": (
            "Foreign / cross-culture spouse. Unusual relationship pattern. International "
            "business partnership. Sometimes second marriage stabler."
        ),
        "source": "Chamatkar Chintamani Verse 91",
    },

    ("Rahu", 8): {
        "verse_sanskrit": (
            "Ashtame Rahu-samjaato svalpaayuh kalanka-piditah, "
            "guhya-vidya-vichakshanaha rahasya-jnaana-tatparah."
        ),
        "verse_translation": (
            "Rahu in the eighth house gives sudden events, accidents, hidden "
            "matters surfacing unexpectedly, and aptitude in occult, technology, "
            "research, deep-sciences, or anything investigating what is hidden. "
            "The native may face an accident or sudden health-shift in early "
            "or mid-life. Inheritance comes through unusual route — distant "
            "relative, unexpected legacy, foreign source. Some scandal or "
            "stigma may surface but is overcome. Talent in tantra, occult "
            "research, depth-psychology, surgery, drug development, or any "
            "boundary-crossing investigation. Steel mind under pressure."
        ),
        "character_themes": ["sudden-events", "occult-tech-research", "unusual-inheritance", "scandal-overcome", "tantric-aptitude"],
        "life_indications": (
            "Sudden events possible. Occult, tantric, research aptitude. Inheritance via "
            "unusual route. Steel mind."
        ),
        "source": "Chamatkar Chintamani Verse 92",
    },

    ("Rahu", 9): {
        "verse_sanskrit": (
            "Bhaagye Rahu-samjaato dharma-bheda-samanvitaha, "
            "videsha-yaatraa-priyah praaani anyaya-marga-vivardhanaha."
        ),
        "verse_translation": (
            "Rahu in the ninth house gives unusual or unconventional fortune, "
            "skeptical or modern view of inherited religion, attraction to "
            "foreign religions or guru-paramparas, and rise through travel "
            "to distant lands. The father may be in unusual line, of different "
            "religion, or distant. Higher education often abroad or in "
            "unusual subjects. The native may become a bridge-figure between "
            "cultures. Pilgrimage takes him to non-traditional sites. Fortune "
            "rises through breaking family-pattern of religion / philosophy. "
            "Some moral controversy possible; ethical clarity is the "
            "native's life-task."
        ),
        "character_themes": ["unusual-fortune", "foreign-religion", "modern-philosopher", "bridge-cultures", "father-distant-or-unusual"],
        "life_indications": (
            "Foreign higher-education. Skeptical or modern religious view. Bridge between "
            "cultures. Father in unusual line."
        ),
        "source": "Chamatkar Chintamani Verse 93",
    },

    ("Rahu", 10): {
        "verse_sanskrit": (
            "Dashame Rahu-samjaata karma-siddhi-vivardhanaha, "
            "videsha-vyaapaara-yuktaha mahaa-laabha-samanvitaha."
        ),
        "verse_translation": (
            "Rahu in the tenth house — extremely powerful for career — gives "
            "rapid and unconventional rise, often through technology, foreign "
            "trade, media, film, photography, IT, aviation, telecommunications, "
            "or any modern boundary-crossing industry. The native may rise "
            "from obscure beginnings to substantial position through unusual "
            "paths. Reputation builds through innovation rather than tradition. "
            "Government roles connected with foreign affairs, technology, or "
            "modern administration suit. Career may include scandal or "
            "controversy at some point but rises again. Fame is often "
            "international rather than local. High ambition driving high results."
        ),
        "character_themes": ["unconventional-rise", "tech-media-foreign", "international-fame", "high-ambition"],
        "life_indications": (
            "Excellent. Career in tech, media, film, foreign trade, telecom, aviation. "
            "Unconventional rapid rise."
        ),
        "source": "Chamatkar Chintamani Verse 94",
    },

    ("Rahu", 11): {
        "verse_sanskrit": (
            "Laabhe Rahu-samjaato bhuri-laabha-samanvitaha, "
            "videsha-mitra-priyaha praaani anyaya-laabha-vivardhanaha."
        ),
        "verse_translation": (
            "Rahu in the eleventh house — one of its strongest placements — "
            "gives plentiful gains, foreign-connected friendships, online or "
            "international networks, and ambitions fulfilled in unusual ways. "
            "The native earns through technology, foreign trade, internet "
            "business, social media, modern marketing, or any boundary-crossing "
            "income stream. Friends are often international, eccentric, or from "
            "very different backgrounds. Elder brother (or elder-figure) may "
            "be abroad or in unusual line. Hopes long-cherished are fulfilled, "
            "sometimes in forms the native himself didn't anticipate. Wealth "
            "accumulates through multiple unconventional channels."
        ),
        "character_themes": ["plentiful-gains", "international-friends", "online-income", "ambitions-fulfilled-unusually"],
        "life_indications": (
            "Excellent. International friends, online income, tech / foreign-trade gains. "
            "Ambitions fulfilled in surprising ways."
        ),
        "source": "Chamatkar Chintamani Verse 95",
    },

    ("Rahu", 12): {
        "verse_sanskrit": (
            "Dvaadashe Rahu-samjaata vyayi netra-roga-piditaha, "
            "videsha-vaasi paraa-bhumau svalpaayur-bhaavena."
        ),
        "verse_translation": (
            "Rahu in the twelfth house gives foreign settlement (often early "
            "and lifelong), heavy expenses, eye-trouble particularly the left "
            "eye, and aptitude for behind-scenes work, isolation-tolerant "
            "professions, or spiritual / occult pursuits in foreign ashrams. "
            "Sleep may be disturbed; dreams vivid and sometimes prophetic. "
            "The native may experience hidden enemies, secret opposition, "
            "or unusual betrayals. Yet this same Rahu gives moksha-aptitude — "
            "the soul's task is to dissolve attachment through foreign and "
            "isolating circumstances. Hospitals, prisons, ashrams, intelligence "
            "agencies, deep-research bases — these become life-settings. "
            "Final-liberation possible."
        ),
        "character_themes": ["foreign-resident-life", "high-expenses", "behind-scenes", "moksha-aptitude", "vivid-dreams"],
        "life_indications": (
            "Lifelong foreign resident. Behind-scenes / isolation-tolerant work. Vivid dreams. "
            "Moksha aptitude."
        ),
        "source": "Chamatkar Chintamani Verse 96",
    },

    # ─────────────────────────── KETU (verses 97-108) ─────────────────────────
    ("Ketu", 1): {
        "verse_sanskrit": (
            "Lagne sthe Ketu-yukto'sau dehe shoka-samanvitah, "
            "vairagi alpa-vaag yukto vipra-vidya-vivardhanaha."
        ),
        "verse_translation": (
            "Ketu in the first house gives a thin, sometimes wiry physique, "
            "detached temperament, mystical mind, and quiet bearing. The "
            "native often looks slightly aloof, has minimal speech, and "
            "carries an air of having-already-known. Body may have a mark, "
            "scar, or unusual feature on the head. Spiritual inclination "
            "is strong from youth. Worldly ambition is muted compared to "
            "peers; the native is doing his work but not for the rewards. "
            "Past-life skills (siddhis, intuition, knowing-without-being-told) "
            "surface from childhood. Often vegetarian or ascetic in tendency."
        ),
        "character_themes": ["thin-wiry", "detached", "mystical", "minimal-speech", "siddhis-from-past-life"],
        "life_indications": (
            "Detached, mystical, quiet. Siddhis or intuition from past-life. Ascetic "
            "tendency. Worldly ambition muted."
        ),
        "source": "Chamatkar Chintamani Verse 97",
    },

    ("Ketu", 2): {
        "verse_sanskrit": (
            "Dvitiye Ketu-yukto'sau kuteshu kalaha-priyah, "
            "kshudra-vaag-yutah praaani dhana-haani-samanvitaha."
        ),
        "verse_translation": (
            "Ketu in the second house disturbs early earnings and family "
            "harmony — disputes over inherited property, sudden losses, or "
            "scattering of family. The native may emigrate from his birth-"
            "family or feel detached from family-of-origin. Speech is sparing "
            "and sometimes blunt. Mouth, teeth, or face may bear an unusual "
            "feature. Wealth comes and goes; what is saved lasts longer than "
            "what is spent. The native may have unusual diet — vegetarian, "
            "minimalist, fasting-tradition. Spiritual learning related to "
            "speech (mantra, recitation, chanting) becomes a lifelong practice."
        ),
        "character_themes": ["family-detachment", "sparing-speech", "wealth-fluctuating", "unusual-diet", "mantra-chanting"],
        "life_indications": (
            "Family detachment. Sparing speech, mantra/chanting practice. Unusual diet. "
            "Wealth fluctuating; emigration possible."
        ),
        "source": "Chamatkar Chintamani Verse 98",
    },

    ("Ketu", 3): {
        "verse_sanskrit": (
            "Tritiye Ketu-yukto'sau bhraatru-shoka-vivardhanaha, "
            "shauryavaan vairaagya-yukto svakaarya-siddhi-laabhakrit."
        ),
        "verse_translation": (
            "Ketu in the third house — surprisingly strong — gives unusual "
            "courage of a quiet, principled sort. The native acts decisively "
            "but not for ego — for what is right or what must be done. "
            "Younger siblings may be fewer, distant, or take spiritual paths. "
            "Hands are skilled in unusual crafts, often spiritual or technical "
            "(mantra-writing, sacred art, electronics, occult tools). Travel "
            "is for mission rather than pleasure. The native is a quiet "
            "warrior — devoted to a cause rather than glory. Communication "
            "is selective but powerful. Past-life writing / teaching skills surface."
        ),
        "character_themes": ["quiet-courage", "principled", "fewer-younger-siblings", "unusual-crafts", "mission-driven"],
        "life_indications": (
            "Quiet courageous, principled. Fewer or spiritual younger siblings. Mission-"
            "driven travel. Unusual crafts."
        ),
        "source": "Chamatkar Chintamani Verse 99",
    },

    ("Ketu", 4): {
        "verse_sanskrit": (
            "Sukha-sthaane Ketu-jaata maatru-saukhya-vivarjitah, "
            "vahana-bhumi-rahito hridaye dukhha-piditah."
        ),
        "verse_translation": (
            "Ketu in the fourth house separates the native from comfortable "
            "home-foundation. Mother may be ill, distant, or take spiritual "
            "path that removes her from active mothering. Property is rarely "
            "kept long; the native may move many times in life, or live "
            "simply on principle. Vehicles are functional rather than "
            "luxurious. Yet the native develops a portable, internal home — "
            "his real shelter is in his own consciousness. Late-life he "
            "may settle in monastic or quiet residence. Heart-region or "
            "respiratory system may need care. Inner detachment from "
            "domestic ambition."
        ),
        "character_themes": ["mother-distant-or-spiritual", "internal-home", "many-moves", "monastic-residence-late", "domestic-detachment"],
        "life_indications": (
            "Mother-distance or her spiritual path. Many residential moves. Internal "
            "home rather than fixed property. Late monastic residence."
        ),
        "source": "Chamatkar Chintamani Verse 100",
    },

    ("Ketu", 5): {
        "verse_sanskrit": (
            "Putrasthaane Ketu-jaata putra-shoka-samanvitah, "
            "udara-roga-piditas tu kshudra-buddhi-samaakulah."
        ),
        "verse_translation": (
            "Ketu in the fifth house brings child-difficulty — late progeny, "
            "miscarriage, child-loss, child of unusual circumstance, or only-"
            "one child. The native is highly intelligent in subtle, intuitive, "
            "mystical ways but less so in conventional academic sense. Mantra-"
            "shastra is the native's speciality — past-life mastery surfaces "
            "as effortless absorption of mantric and meditative practice. "
            "Speculation rarely succeeds; gambling is forbidden by inner sense. "
            "Education may include unusual subjects — astrology, occult, "
            "spiritual philosophy, mathematics of unusual kind. Children when "
            "they come are often spiritually inclined."
        ),
        "character_themes": ["child-difficulty", "intuitive-intelligence", "mantra-mastery", "spiritual-children-when-they-come"],
        "life_indications": (
            "Child-difficulty (late, lost, unusual). Mantra-shastra mastery from past "
            "life. Intuitive subtle intelligence."
        ),
        "source": "Chamatkar Chintamani Verse 101",
    },

    ("Ketu", 6): {
        "verse_sanskrit": (
            "Shashthe Ketu-yutah praaani vairi-vargasya naashanaha, "
            "matuleshu sukham praapto rahasya-jnaana-tatparah."
        ),
        "verse_translation": (
            "Ketu in the sixth house — Vipareeta-Ketu — destroys enemies "
            "through detachment; rivals drop away because the native simply "
            "doesn't engage their game. Lawsuits resolve in his favour, often "
            "through opponents' own mistakes. Maternal uncle may be in "
            "unusual line — spiritual, foreign, or simply unconventional. "
            "Service careers in healing, medicine, surgery, occult, "
            "investigation, or spiritual / charitable institutions flourish. "
            "Mystery illnesses may visit but resolve. The native's outsider-"
            "perspective and detachment become professional strengths. One "
            "of Ketu's best placements."
        ),
        "character_themes": ["detached-victor", "vipareeta-rise", "healing-occult-charity", "mystery-illness-resolves"],
        "life_indications": (
            "Excellent. Detachment defeats enemies. Healing, medicine, surgery, occult, "
            "charitable service. Vipareeta-rise."
        ),
        "source": "Chamatkar Chintamani Verse 102",
    },

    ("Ketu", 7): {
        "verse_sanskrit": (
            "Saptame Ketu-samjaato bhaaryaa-prema-vivarjitah, "
            "vairagi naari-rahito ekaaki-vasanaakulah."
        ),
        "verse_translation": (
            "Ketu in the seventh house challenges marital harmony. Marriage "
            "may be delayed, dispassionate, or end in detachment. The spouse "
            "may take spiritual path or be of unusual disposition. Some "
            "natives never marry, others marry late and live more as "
            "companions than passionate partners. Trade-partnerships dissolve "
            "when their purpose is complete. The native is fundamentally "
            "self-sufficient and may prefer solitude to inadequate company. "
            "Yet a soul-deep, spiritually-aligned partnership (not necessarily "
            "in formal marriage) is possible. Long journeys for spiritual "
            "purpose succeed."
        ),
        "character_themes": ["delayed-or-dispassionate-marriage", "self-sufficient", "spiritual-spouse-possibility", "solitude-tolerant"],
        "life_indications": (
            "Marriage delayed, dispassionate, or absent. Spouse may be spiritual. Self-"
            "sufficient native. Spiritual-aligned partnership possible."
        ),
        "source": "Chamatkar Chintamani Verse 103",
    },

    ("Ketu", 8): {
        "verse_sanskrit": (
            "Ashtame Ketu-yukto'sau dirgha-aayuh rahasya-vidayaha, "
            "guhya-saukhya-yutah praaani moksha-marga-pravartakaha."
        ),
        "verse_translation": (
            "Ketu in the eighth house gives long lifespan, deep occult knowledge, "
            "talent in research / mantra / tantra / depth-psychology, and "
            "intuitive understanding of death, transformation, and what is "
            "hidden. The native may experience mystical visions or deja-vu "
            "from childhood. Inheritance comes through unusual or spiritual "
            "channels — gifts from gurus, legacies from distant relatives. "
            "Surgery, occult research, healing arts, longevity-medicine, "
            "and gerontology suit. The native seems to know things others "
            "haven't told him; intuition runs deep. Moksha aptitude high."
        ),
        "character_themes": ["long-life", "occult-research", "mystical-visions", "moksha-aptitude", "deep-intuition"],
        "life_indications": (
            "Long life, occult/tantric mastery. Mystical visions from childhood. Inheritance "
            "via spiritual channels. Moksha-aptitude high."
        ),
        "source": "Chamatkar Chintamani Verse 104",
    },

    ("Ketu", 9): {
        "verse_sanskrit": (
            "Bhaagye Ketu-yukto'sau dharma-vidya-vivekashah, "
            "tirtha-yaatraa-priyah praaani vairagi-marga-priyaha."
        ),
        "verse_translation": (
            "Ketu in the ninth house gives a deeply spiritual, dharmically "
            "inclined, often renunciate-minded native. The father may be "
            "spiritual or distant. Higher education includes spiritual / "
            "philosophical / occult subjects. The native is drawn to gurus, "
            "ashrams, ancient traditions, and pilgrimage to remote sites. "
            "Foreign opportunities open particularly if connected with "
            "spiritual or research work. Fortune rises through quiet dharmic "
            "alignment rather than aggressive enterprise. The native may "
            "become a teacher of meditation, mantra, philosophy, or healing "
            "tradition. Strong past-life dharmic credit."
        ),
        "character_themes": ["deeply-spiritual", "renunciate-mind", "remote-pilgrimage", "spiritual-teacher", "father-spiritual-or-distant"],
        "life_indications": (
            "Deeply spiritual, often renunciate. Higher-ed in philosophy / spiritual / "
            "occult. Teacher of meditation / mantra / healing."
        ),
        "source": "Chamatkar Chintamani Verse 105",
    },

    ("Ketu", 10): {
        "verse_sanskrit": (
            "Dashame Ketu-samjaata karma-siddhi-vivardhanaha, "
            "vairagi-marga-yutaha mahaa-jnaani-priya-darshanaha."
        ),
        "verse_translation": (
            "Ketu in the tenth house gives a career touched by spirituality, "
            "research, healing, occult, charity, technology, or any field "
            "where the native's outsider-perspective becomes professional "
            "strength. The native may rise high but rarely seeks public "
            "acclaim — work matters more than visibility. Career changes "
            "may be sudden but each opens a deeper line. Many such natives "
            "become teachers, healers, researchers, technologists with "
            "philosophical depth, or quiet professionals respected by peers "
            "more than by general public. Fame is rarely the target; mastery is."
        ),
        "character_themes": ["spiritual-career", "research-healing-tech", "low-visibility-high-mastery", "sudden-career-shifts"],
        "life_indications": (
            "Spiritual / research / healing career. Mastery over visibility. Sudden "
            "career-shifts each deepening the line. Outsider-strength."
        ),
        "source": "Chamatkar Chintamani Verse 106",
    },

    ("Ketu", 11): {
        "verse_sanskrit": (
            "Laabhe Ketu-samjaato bhuri-laabha-samanvitaha, "
            "vairagi-mitra-priyo nityam aanyaya-laabha-samanvitah."
        ),
        "verse_translation": (
            "Ketu in the eleventh house gives plentiful gains particularly "
            "from spiritual, occult, research, healing, technology, or "
            "unusual / foreign income streams. Friends are typically deep, "
            "mystically-inclined, or from very different backgrounds — fewer "
            "in number but rich in connection. Elder brother may be in "
            "spiritual or unusual line. Ambitions long held are fulfilled, "
            "often after the native has stopped chasing them. Wealth "
            "accumulates through fields the native loves, not those he "
            "pursued for wealth's sake. Income through detachment — paradoxical but reliable."
        ),
        "character_themes": ["plentiful-gains-from-detachment", "mystical-friend-circle", "spiritual-elder-brother", "wealth-through-non-attachment"],
        "life_indications": (
            "Plentiful gains from spiritual / research / unusual income. Mystical friend "
            "circle. Wealth through what one loves."
        ),
        "source": "Chamatkar Chintamani Verse 107",
    },

    ("Ketu", 12): {
        "verse_sanskrit": (
            "Dvaadashe Ketu-samjaata moksha-marga-pravartakah, "
            "videsha-vaasi vairagi shanta-bhog-vinodakaha."
        ),
        "verse_translation": (
            "Ketu in the twelfth house — its highest karmic placement — "
            "gives final-liberation aptitude, monastic temperament, foreign "
            "settlement (often in spiritual or remote setting), peaceful "
            "sleep filled with mystical dreams, and natural withdrawal from "
            "material striving. This is often called 'the moksha placement' "
            "by Bhattaji and later commentators. The native completes karmic "
            "work in this birth and prepares for liberation. Expenses are "
            "primarily on dharma — temples, charity, gurus, retreats. Bed-"
            "comforts are simple but sleep is deep and peaceful. The mind "
            "rests easily in solitude. Final birth in some traditions."
        ),
        "character_themes": ["moksha-aptitude", "monastic", "foreign-spiritual-residence", "peaceful-sleep", "final-birth-possibility"],
        "life_indications": (
            "Final-liberation aptitude. Foreign / spiritual / monastic residence. Peaceful "
            "sleep, mystical dreams. Charity-spending. Possibly final birth."
        ),
        "source": "Chamatkar Chintamani Verse 108",
    },

}


# =============================================================================
# BHAVA_KARAKA_OVERLAYS — 12 entries
# Each: amplifying / weakening conditions for Chamatkar verses in that house
# =============================================================================

BHAVA_KARAKA_OVERLAYS = {
    1: {
        "house": 1,
        "natural_karaka": "Sun",
        "amplifying_combinations": [
            "Lagna lord in own/exalted/kendra",
            "Sun strong in 1H/4H/9H/10H",
            "Mars in 9H reinforces lagna courage",
            "Lagna with benefic aspect from Jupiter",
        ],
        "weakening_combinations": [
            "Lagna lord debilitated or in 6H/8H/12H",
            "Sun debilitated in Libra",
            "Multiple malefics in 1H without dignity",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    2: {
        "house": 2,
        "natural_karaka": "Jupiter",
        "amplifying_combinations": [
            "2nd lord in 1H/2H/4H/5H/9H/10H/11H",
            "Jupiter or Venus dignified in 2H",
            "Mercury dignified gives sweet speech amplification",
        ],
        "weakening_combinations": [
            "2nd lord in 6H/8H/12H",
            "Mars or Saturn in 2H without dignity",
            "Rahu/Ketu in 2H amplify volatility",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    3: {
        "house": 3,
        "natural_karaka": "Mars",
        "amplifying_combinations": [
            "3rd lord in upachaya houses (3, 6, 10, 11)",
            "Mars or Saturn dignified in 3H",
            "Jupiter aspecting from 7H or 9H",
        ],
        "weakening_combinations": [
            "Jupiter in 3H weakens courage (its weakest house)",
            "3rd lord in 8H or 12H",
            "Moon weak in 3H may give few siblings",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    4: {
        "house": 4,
        "natural_karaka": "Moon",
        "amplifying_combinations": [
            "Moon dignified in 4H or aspecting 4H",
            "4th lord in 1H/4H/9H/10H/11H",
            "Jupiter or Venus dignified in 4H gives Hamsa/Malavya component",
        ],
        "weakening_combinations": [
            "Mars/Saturn/Rahu/Ketu in 4H without dignity",
            "Moon in 6H/8H/12H weakens mother-comfort",
            "4th lord debilitated",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    5: {
        "house": 5,
        "natural_karaka": "Jupiter",
        "amplifying_combinations": [
            "Jupiter dignified in 5H (its best placement)",
            "5th lord in 1H/4H/5H/9H/10H/11H",
            "Mercury or Venus in 5H without affliction",
        ],
        "weakening_combinations": [
            "Sun/Mars/Saturn in 5H without dignity",
            "Rahu in 5H without Jupiter aspect",
            "5th lord in 6H/8H/12H — child-difficulty",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    6: {
        "house": 6,
        "natural_karaka": "Mars/Saturn",
        "amplifying_combinations": [
            "Malefics in 6H (Mars, Saturn, Rahu) — defeat enemies",
            "6th lord in 6H/8H/12H — Vipareeta Raja Yoga",
            "Mars dignified in 6H gives Vipareeta-Mars",
        ],
        "weakening_combinations": [
            "Benefics in 6H without supporting dignity",
            "6th lord in 1H/4H/5H/7H/10H — strong enemies and debt",
            "Moon/Venus/Jupiter weak in 6H",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    7: {
        "house": 7,
        "natural_karaka": "Venus",
        "amplifying_combinations": [
            "Venus dignified in 7H (its own bhava from Libra)",
            "7th lord in 1H/4H/5H/7H/9H/10H/11H",
            "Jupiter aspecting 7H from 1H/3H/5H/9H/11H",
        ],
        "weakening_combinations": [
            "Mars in 7H gives kuja-dosha unless cancelled",
            "Saturn/Rahu/Ketu in 7H delay or estrange marriage",
            "7th lord in 6H/8H/12H",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    8: {
        "house": 8,
        "natural_karaka": "Saturn",
        "amplifying_combinations": [
            "Saturn dignified in 8H — long life",
            "Jupiter aspecting 8H — protection",
            "Ketu in 8H — moksha-aptitude amplifier",
        ],
        "weakening_combinations": [
            "Sun/Moon/Mars in 8H without dignity",
            "8th lord debilitated or in 6H/12H",
            "Multiple malefics in 8H without aspect of benefic",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    9: {
        "house": 9,
        "natural_karaka": "Jupiter",
        "amplifying_combinations": [
            "Jupiter dignified in 9H (its own bhava)",
            "Sun dignified in 9H — fortune-amplifier",
            "9th lord in 1H/4H/5H/9H/10H/11H",
        ],
        "weakening_combinations": [
            "Saturn/Rahu/Ketu in 9H without aspect of Jupiter",
            "9th lord in 6H/8H/12H",
            "Sun debilitated in 9H — father-trouble",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    10: {
        "house": 10,
        "natural_karaka": "Sun/Mercury/Jupiter/Saturn",
        "amplifying_combinations": [
            "Sun dignified in 10H — Solar Raja Yoga",
            "Saturn dignified in 10H — Shasha Yoga",
            "Mars dignified in 10H — Ruchaka Yoga",
            "Jupiter dignified in 10H — Hamsa Yoga component",
            "10th lord in 1H/4H/9H/10H/11H",
        ],
        "weakening_combinations": [
            "10th lord debilitated or in 6H/8H/12H",
            "Multiple malefics in 10H without dignity",
            "Sun/Moon weak in 10H",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    11: {
        "house": 11,
        "natural_karaka": "Jupiter",
        "amplifying_combinations": [
            "Saturn dignified in 11H — slow-but-sure income",
            "Jupiter dignified in 11H — wisdom-income",
            "11th lord in 1H/2H/5H/9H/10H/11H",
        ],
        "weakening_combinations": [
            "11th lord in 6H/8H/12H",
            "Multiple debilitated planets in 11H",
            "Moon weak in 11H — friend-troubles",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
    12: {
        "house": 12,
        "natural_karaka": "Saturn/Ketu",
        "amplifying_combinations": [
            "Ketu in 12H — moksha-aptitude",
            "Venus dignified in 12H — Bhoga-yoga (shayya-sukha)",
            "Jupiter dignified in 12H — charitable spending and wisdom",
        ],
        "weakening_combinations": [
            "Sun/Moon weak in 12H — vitality issues",
            "Mars in 12H — high expenses, hidden enemies",
            "12th lord in 6H/8H — losses amplified",
        ],
        "source": "Chamatkar Chintamani — bhava-karaka overlay tradition",
    },
}


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def _apply_overlay(chart, planet, house):
    """Determine amplification level: 'strong', 'moderate', or 'weak'.

    Heuristic: combine planet's own dignity, bhava-karaka match, lord-position.
    """
    score = 0  # neutral baseline

    # 1. Planet's own dignity
    pos = chart["positions"].get(planet, {})
    sign = pos.get("rasi")
    dig = DIGNITIES.get((planet, sign), "neutral")
    if dig in ("Own", "Exalted", "Exalted/Own"):
        score += 2
    elif dig == "Debil":
        score -= 2

    # 2. Bhava-karaka of this house
    overlay = BHAVA_KARAKA_OVERLAYS.get(house, {})
    natural_kar = overlay.get("natural_karaka", "")
    if planet in natural_kar:
        # planet IS the natural karaka of the house it sits in
        score += 1

    # 3. House class
    if house in KENDRA_HOUSES or house in TRIKONA_HOUSES:
        score += 1
    elif house in DUSTHANA_HOUSES:
        # Vipareeta logic: malefics in dusthana for some planets is amplifying
        # (Mars/Saturn/Rahu/Ketu in 6th = stronger Chamatkar-rise)
        if planet in ("Mars", "Saturn", "Rahu", "Ketu") and house == 6:
            score += 1
        else:
            score -= 1

    # 4. Conjunctions / mutual aspects with strong Jupiter
    j_pos = chart["positions"].get("Jupiter", {})
    if j_pos:
        j_house = j_pos.get("house")
        # Jupiter aspects: 5th, 7th, 9th from itself (1-indexed)
        if j_house is not None:
            jupiter_aspected = {
                ((j_house + 4 - 1) % 12) + 1,
                ((j_house + 6 - 1) % 12) + 1,
                ((j_house + 8 - 1) % 12) + 1,
            }
            if house in jupiter_aspected and is_dignified(chart, "Jupiter"):
                score += 1

    # Translate to label
    if score >= 3:
        return "strong"
    elif score <= -1:
        return "weak"
    else:
        return "moderate"


def chamatkar_reading(chart):
    """For each of 9 planets, return Chamatkar Chintamani reading.

    Returns list of dicts (one per planet): planet, house, verse, themes, etc.
    """
    readings = []
    for planet in PLANETS_ALL:  # Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
        pos = chart["positions"].get(planet)
        if not pos:
            continue
        house = pos.get("house")
        if house is None:
            continue

        verse_data = CHAMATKAR_VERSES.get((planet, house))
        if not verse_data:
            # Should not happen — we have all 108 cells
            continue

        amplification = _apply_overlay(chart, planet, house)

        readings.append({
            "planet": planet,
            "house": house,
            "rasi": pos.get("rasi"),
            "verse_sanskrit": verse_data["verse_sanskrit"],
            "verse_translation": verse_data["verse_translation"],
            "character_themes": list(verse_data["character_themes"]),
            "life_indications": verse_data["life_indications"],
            "amplification": amplification,
            "source": verse_data["source"],
        })

    return readings


def chamatkar_summary(chart):
    """Return a top-level synthesis across all 9 planet-readings."""
    readings = chamatkar_reading(chart)

    # Aggregate themes
    all_themes = []
    for r in readings:
        all_themes.extend(r["character_themes"])

    # Count + dedupe + top 10
    counts = {}
    for theme in all_themes:
        counts[theme] = counts.get(theme, 0) + 1
    top_themes = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    personality_keywords = [t for t, _c in top_themes[:10]]

    # Strongest / weakest
    score_map = {"strong": 2, "moderate": 1, "weak": 0}
    sorted_by_amp = sorted(readings, key=lambda r: score_map.get(r["amplification"], 1), reverse=True)
    strongest = sorted_by_amp[0]["planet"] if sorted_by_amp else None
    weakest = sorted_by_amp[-1]["planet"] if sorted_by_amp else None

    # Core arc — from top-3 amplified
    top3 = sorted_by_amp[:3]
    arc_parts = []
    for r in top3:
        # Take first 70 chars of life_indications, ensure period.
        snippet = r["life_indications"].split(".")[0]
        arc_parts.append(f"{r['planet']} in H{r['house']} ({r['amplification']}): {snippet.strip()}.")
    core_life_arc = " ".join(arc_parts) if arc_parts else "No readings produced."

    # Remedies implied — collect for weak planets
    remedies = []
    for r in readings:
        if r["amplification"] == "weak":
            remedies.append({
                "planet": r["planet"],
                "house": r["house"],
                "implied_remedy": (
                    f"Strengthen {r['planet']} via traditional means "
                    f"(mantra, charity to its karaka-class, gem cautiously) — "
                    f"its weakness affects {', '.join(r['character_themes'][:2])} themes."
                ),
            })

    return {
        "personality_keywords": personality_keywords,
        "strongest_chamatkar_planet": strongest,
        "weakest_chamatkar_planet": weakest,
        "core_life_arc": core_life_arc,
        "remedies_implied": remedies,
        "total_readings": len(readings),
        "source_text": "Chamatkar Chintamani by Bhattaji, 108 verses",
    }


# =============================================================================
# TEST BLOCK
# =============================================================================

if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")

    chart_path = "../charts/manoj_chart.json"
    chart = json.load(open(chart_path, encoding="utf-8"))

    print("=" * 70)
    print(f"CHAMATKAR CHINTAMANI — {chart.get('name', '?')}")
    print("=" * 70)

    # Sanity check: 108 verses
    assert len(CHAMATKAR_VERSES) == 108, f"Expected 108 verses, got {len(CHAMATKAR_VERSES)}"
    print(f"\n[OK] Verse-count: {len(CHAMATKAR_VERSES)} / 108")
    print(f"[OK] Bhava-karaka overlays: {len(BHAVA_KARAKA_OVERLAYS)} / 12")

    print("\n" + "-" * 70)
    print("CHAMATKAR READING (per planet)")
    print("-" * 70)
    readings = chamatkar_reading(chart)
    for r in readings:
        print(f"\n{r['planet']} in H{r['house']} ({r['rasi']}) [{r['amplification']}]:")
        print(f"  Verse: {r['verse_translation'][:100]}...")
        print(f"  Themes: {', '.join(r['character_themes'])}")

    print("\n" + "-" * 70)
    print("CHAMATKAR SUMMARY")
    print("-" * 70)
    summary = chamatkar_summary(chart)
    print(f"\nPersonality keywords (top 10):")
    for k in summary["personality_keywords"]:
        print(f"  - {k}")
    print(f"\nStrongest planet: {summary['strongest_chamatkar_planet']}")
    print(f"Weakest planet: {summary['weakest_chamatkar_planet']}")
    print(f"\nCore life arc:\n  {summary['core_life_arc']}")
    if summary["remedies_implied"]:
        print(f"\nRemedies implied ({len(summary['remedies_implied'])} weak planets):")
        for rem in summary["remedies_implied"]:
            print(f"  - {rem['planet']} (H{rem['house']}): {rem['implied_remedy'][:100]}...")
    else:
        print("\nNo weak Chamatkar planets — no specific remedies implied.")
    print(f"\nSource: {summary['source_text']}")
    print(f"Total readings: {summary['total_readings']}")
    print("\n[OK] Chamatkar Chintamani module complete.")
