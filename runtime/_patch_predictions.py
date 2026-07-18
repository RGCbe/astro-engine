"""Patch generate_report.py — replace all_predictions() with prediction-only text."""
import re, sys
from pathlib import Path

SRC = Path(__file__).parent / "generate_report.py"
text = SRC.read_text(encoding="utf-8")

NEW_FUNC = '''def all_predictions(chart):
    """All domain predictions — prediction text only, no astrological technical terms shown to user."""
    pos=chart["positions"]
    lagna_idx=chart["lagna_idx"]
    moon=pos["Moon"]
    pred={}
    mds,_,_,_=vimshottari(chart)

    def lord_of(house):
        sign=RASIS[(lagna_idx+house-1)%12]
        return RASI_LORDS[sign]

    def occupants(house):
        return [p for p,pd in pos.items() if pd["house"]==house]

    def lord_house(house):
        l=lord_of(house)
        return pos[l]["house"] if l in pos else None

    # ── 1. SELF & PERSONALITY ──
    nak=chart["janma_nakshatra"]
    ak_planet=chara_karakas(chart)[0][1]
    sun_dig=DIGNITIES.get(("Sun",pos["Sun"]["rasi"]),"neutral")
    merc_dig=DIGNITIES.get(("Mercury",pos["Mercury"]["rasi"]),"neutral")
    sat_dig=DIGNITIES.get(("Saturn",pos["Saturn"]["rasi"]),"neutral")
    jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    LAGNA_BODY={
        "Aries":"medium build, athletic, sharp features, scar or mark on the head; impulsive walk",
        "Taurus":"thick-set, strong neck, attractive face, slow and steady gait",
        "Gemini":"tall thin frame, expressive hands, animated speech, restless",
        "Cancer":"round face, fair complexion, soft body, emotional eyes",
        "Leo":"tall, broad shoulders, kingly posture, magnetic presence",
        "Virgo":"medium height, slender, refined features, careful walk",
        "Libra":"well-proportioned, attractive, graceful, charming smile",
        "Scorpio":"medium-strong build, intense eyes, secretive expression",
        "Sagittarius":"tall, broad and generous build, jovial face, philosophical look",
        "Capricorn":"thin frame, prominent bones, serious expression, slow walk",
        "Aquarius":"tall thin frame, unusual features, distinctive look",
        "Pisces":"medium, soft body, dreamy eyes, gentle expression",
    }
    pred["self"]=[
        f"<b>Physical appearance</b> — {LAGNA_BODY.get(chart[\'lagna\'],\'\')}. "
        f"The body carries this signature throughout life — in build, in gait, and in first impression.",

        f"<b>Core personality</b> — {NAKSHATRA_PERSONALITY.get(nak,\'\')}. "
        f"This is the deepest personality layer — the part that never changes regardless of circumstances or age.",

        f"<b>Mind and thinking style</b> — " + (
        "You think rapidly and analytically. Strong at reasoning, facts, and logical argument. Arguments and analysis come naturally."
        if merc_dig in ["Own","Exalted","Exalted/Own"] else
        "You are intuitive and experiential — you learn best through doing and feeling, not through books or theory alone."
        if merc_dig=="Debil" else
        "Your mind is balanced — you move comfortably between feeling and analysis depending on the situation."),

        f"<b>Emotional nature</b> — " + (
        "Passionate and expressive — emotions run hot, enthusiasm ignites quickly, and you bring fire to everything you care about."
        if moon["rasi"] in ["Aries","Leo","Sagittarius"] else
        "Steady and practical — emotions run deep but are rarely displayed. You need stability and dislike sudden change."
        if moon["rasi"] in ["Taurus","Virgo","Capricorn"] else
        "Curious and social — you process emotions through communication and connection. Boredom is your true enemy."
        if moon["rasi"] in ["Gemini","Libra","Aquarius"] else
        "Deeply sensitive and intuitive — you feel everything intensely. Your emotional world is rich but sometimes overwhelming."),

        f"<b>Soul\'s core purpose</b> — Your life revolves around the themes of {PLANET_ARCHETYPES.get(ak_planet,\'\')}. "
        f"Every major experience — whether lucky or painful — is nudging you toward mastery in this domain.",

        f"<b>Discipline and wisdom</b> — " + (
        "You have a naturally disciplined character — structure and hard work come built-in. You are the person others rely on for consistency."
        if sat_dig in ["Own","Exalted"] else
        "Discipline is your life\'s greatest teacher — you will be tested repeatedly in this area, and each test builds character."
        if sat_dig=="Debil" else
        "Your sense of discipline is moderate — functional but not exceptional.") + " " + (
        "Your moral compass is strong — a natural ethical sense that guides decisions even under pressure."
        if jup_dig in ["Own","Exalted"] else
        "Developing wisdom and ethical clarity is an ongoing process — lessons come through experience rather than being inborn."
        if jup_dig=="Debil" else
        "Wisdom and good judgment are available to you when genuinely sought."),

        f"<b>How you communicate</b> — " + (
        "Eloquent, polished, and persuasive — words are your tool. People listen when you speak."
        if lord_of(2) in ["Mercury","Venus","Jupiter"] else
        "Direct and frank — you say what you mean without decoration, which people either love or find too blunt."
        if lord_of(2) in ["Mars","Sun"] else
        "Measured and careful — you think before you speak, and when you do, it carries weight."),

        f"<b>Learning and intellect</b> — " + (
        "You learn fastest through reading, research, and analytical breakdown. Academic environments suit you well."
        if pos["Mercury"]["rasi"] in ["Gemini","Virgo"] else
        "You learn through emotion, intuition, and lived experience. Facts alone do not move you — stories and meaning do."
        if pos["Mercury"]["rasi"] in ["Cancer","Scorpio","Pisces"] else
        "You learn through observation and hands-on practice. You need to see things in action."),

        f"<b>Self-confidence</b> — " + (
        "Natural, healthy self-confidence — comfortable with authority and leadership without being arrogant."
        if sun_dig in ["Own","Exalted"] else
        "Your confidence comes and goes — you sometimes undersell yourself. Learning to claim your authority fully is a key life task."
        if sun_dig=="Debil" else
        "Your sense of self is balanced — confident enough to lead when needed, humble enough to follow."),

        f"<b>Will power and action</b> — " + (
        "Strong decisive will — you act first and adjust later. Hesitation is rare; momentum is your natural state."
        if pos["Mars"]["house"] in [1,3,6,10,11] else
        "Reflective will — you plan carefully before acting. Not impulsive, but deliberate and strategic when you move."),

        f"<b>Memory and retention</b> — " + (
        "Sharp, retentive memory — you hold onto details, faces, conversations, and facts with ease. People are often surprised by what you recall."
        if abs(pos["Mercury"]["rasi_idx"]-pos["Moon"]["rasi_idx"])<=2 else
        "Selective emotional memory — you remember deeply what matters to your heart, but routine details pass through."),
    ]

    # ── 2. PARENTS ──
    h9_occ=occupants(9); h9_lord=lord_of(9); h9_lord_h=lord_house(9)
    h4_occ=occupants(4); h4_lord=lord_of(4); h4_lord_h=lord_house(4)
    sun_h=pos["Sun"]["house"]; sun_dig=DIGNITIES.get(("Sun",pos["Sun"]["rasi"]),"neutral")
    moon_h=pos["Moon"]["house"]; moon_dig=DIGNITIES.get(("Moon",moon["rasi"]),"neutral")
    pred["parents"]=[
        f"<b>Father\'s overall life</b> — " + (
        "Your father had a strong, commanding presence — likely involved in authority, government, or leadership-type work. He carried himself with dignity and was respected in his field or community."
        if sun_dig in ["Own","Exalted","Exalted/Own"] else
        "Your father faced significant challenges in health, career, or personal life. There may have been periods of illness or difficulty that tested him. His journey had a teaching quality for you."
        if sun_dig=="Debil" else
        "Your father was a stable, hardworking figure — not highly dramatic, but consistent and reliable. His influence on your life came more through example than through wealth or power."),

        f"<b>Father\'s health and longevity</b> — " + (
        "Your father is likely to enjoy good health and long life — his vitality is well-supported."
        if sun_dig in ["Own","Exalted","Exalted/Own"] else
        "Your father\'s health is an area of concern — illnesses, chronic issues, or a shorter life are possibilities to be aware of. Extra care and timely medical attention are advised."
        if sun_dig=="Debil" else
        "Your father\'s health follows normal cycles — not exceptional worry, but regular monitoring is wise.") + " " + (
        "The broader indicators reinforce a stable life journey for him."
        if h9_lord_h in [1,4,5,7,9,10,11] else
        "Some periods in his life bring significant tests or disruptions — the chart shows this as part of his journey."),

        f"<b>Father\'s profession and status</b> — " + (
        "Your father is naturally drawn to authority, leadership, or government service. He carries himself as someone in charge, and others recognise that naturally."
        if sun_h in [1,10] else
        "Your father\'s career was tied to social connections, partnerships, or trade. He dealt with the public or worked in a people-facing role."
        if sun_h in [7,11] else
        "Your father\'s work involved communication, teaching, or creative expression — he may have been a writer, teacher, or skilled specialist."
        if sun_h in [3,5] else
        "Your father\'s career had its challenges — possibly self-made through difficult circumstances."
        if sun_h in [6,8,12] else
        "Your father had a well-balanced career path — steady rather than spectacular, building over time."),

        f"<b>Mother\'s overall life</b> — " + (
        "Your mother has a powerful nurturing energy — likely a devoted, loving, and deeply present mother who shaped your emotional world profoundly. Her influence on you is immense and long-lasting."
        if moon_dig in ["Own","Exalted","Exalted/Own"] else
        "Your relationship with your mother carries complexity — there may have been emotional distance, separation, or a difficult beginning. The bond, while present, had to be worked for on both sides."
        if moon_dig=="Debil" else
        "Your mother was a balanced, supportive presence — warm and caring without being overwhelming. A quiet strength behind the scenes of your life."),

        f"<b>Bond with your mother</b> — " + (
        "Deep and lifelong emotional bond with your mother. She is your emotional anchor and safe harbour. Her guidance shaped your inner world more than almost anything else."
        if moon_h in [1,4,5,9] else
        "Your mother\'s influence is strongest in your public life and social success — she may have pushed you toward achievement and visibility."
        if moon_h in [10,11] else
        "The mother relationship has a karmic, transformative quality — lessons in letting go, growth through separation, or a spiritual dimension to the bond."
        if moon_h in [6,8,12] else
        "Warm and reliable mother bond — present when needed, giving space when appropriate."),

        f"<b>Father-child relationship</b> — " + (
        "Your father was a strong authority figure — respected but possibly experienced as distant or commanding. The relationship held high expectations."
        if sun_h in [1,4,7,10] else
        "Your father and you had a warm connection built around learning, travel, or shared philosophies. He was more a friend or guide than a stern authority."
        if sun_h in [3,5,9,11] else
        "The father relationship carried its challenges — distance, illness, absence, or difficult circumstances. Yet these experiences shaped your independence."),

        f"<b>Parental bond comparison</b> — " + (
        "You were clearly closer to your mother — she was the emotional centre of home life while your father was more peripheral or demanding."
        if moon_h in [1,4] and sun_h in [6,8,12] else
        "Both parents were significant but in different ways — your father shaped your outer ambition while your mother shaped your inner world."
        if sun_h in [1,10] and moon_h in [4,9] else
        "Both parental bonds were present and functional — a relatively stable home environment overall."),

        f"<b>Inheritance from parents</b> — " + (
        "Strong indicators of inheritance — family property, ancestral wealth, or meaningful financial legacy from one or both parents."
        if h4_lord_h in [2,11] or h9_lord_h in [2,11] else
        "Inheritance is modest — wealth in your life will largely be self-built rather than received from the family."),

        f"<b>Parental influence across life</b> — "
        f"Parental influence is strongest during the early years and resurfaces during periods of major transition. "
        f"Watch especially for health events in the parents during the dasha periods of the lords of the 4th and 9th houses.",
    ]

    # ── 3. SIBLINGS ──
    h3_occ=occupants(3); h3_lord=lord_of(3); h3_lord_h=lord_house(3)
    h11_occ=occupants(11); h11_lord=lord_of(11); h11_lord_h=lord_house(11)
    mars_h=pos["Mars"]["house"]; mars_dig=DIGNITIES.get(("Mars",pos["Mars"]["rasi"]),"neutral")
    pred["siblings"]=[
        f"<b>Siblings overview</b> — " + (
        "You are likely to have active sibling dynamics — at least one sibling who plays a notable role in your life."
        if h3_occ or h11_occ else
        "You may be an only child, or if siblings exist they play a less central role in your life journey."),

        f"<b>Relationship quality with siblings</b> — " + (
        "Strong, supportive, and protective sibling relationships. You have each other\'s backs. The bond may be tested but ultimately holds firm."
        if mars_dig in ["Own","Exalted","Exalted/Own"] else
        "Sibling dynamics carry friction, competition, or periods of estrangement. Communication and deliberate effort are needed to maintain bonds."
        if mars_dig=="Debil" else
        "Balanced sibling relationships — neither overly close nor distant. You support each other when it matters."),

        f"<b>Younger siblings\' life path</b> — "
        f"Your younger sibling(s) tend toward careers or life paths involving " + (
        "wealth, family, or communication." if h3_lord_h in [2,3] else
        "home, creativity, or stability." if h3_lord_h in [4,5] else
        "partnership, foreign work, or transformation." if h3_lord_h in [7,8,12] else
        "career, public recognition, or social achievement." if h3_lord_h in [10,11] else
        "challenges that build character.") +
        " Their success and yours are often interlinked.",

        f"<b>Elder siblings\' role in your life</b> — " + (
        "Elder siblings or cousins are sources of gain, support, and friendship for you — they open doors or provide encouragement at key moments."
        if h11_lord_h in [1,2,5,11] else
        "Elder siblings follow a largely independent path — you respect each other but live separate lives."
        if h11_lord_h in [6,8,12] else
        "Elder siblings are present in the background — helpful occasionally but not a primary source of support."),

        f"<b>Your own courage and initiative</b> — " + (
        "Bold and action-oriented — you confront challenges head-on, are not easily intimidated, and have natural leadership energy."
        if mars_h in [1,3,6,10] else
        "Thoughtful and measured — you plan before you act. Your strength lies in strategy, not brute force."
        if mars_h in [4,7] else
        "Courage is built through experience rather than innate — you grow bolder as you mature and accumulate wins."),

        f"<b>Sibling wellbeing</b> — " + (
        "The chart shows no major red flags for sibling health or longevity — overall positive trajectory."
        if mars_dig not in ["Debil"] and mars_h not in [6,8,12] else
        "There may be health concerns for a sibling at some point in life — worth ensuring regular contact and care."),

        f"<b>When sibling themes peak</b> — "
        f"Sibling-related events — their marriages, career shifts, migrations, or health events — "
        f"come into strong focus during the active dasha periods tied to the 3rd and 11th houses. "
        f"These are natural times for sibling bonding or resolution of old tensions.",
    ]

    # ── 4. EDUCATION ──
    h5_occ=occupants(5); h5_lord=lord_of(5); h5_lord_h=lord_house(5)
    merc_h=pos["Mercury"]["house"]; merc_dig=DIGNITIES.get(("Mercury",pos["Mercury"]["rasi"]),"neutral")
    jup_h=pos["Jupiter"]["house"]; jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    rahu_h=pos["Rahu"]["house"]
    pred["education"]=[
        f"<b>Early schooling experience</b> — " + (
        "Smooth, supported school years — good environment, helpful teachers, and steady academic progress."
        if h4_lord_h in [1,4,5,9,10,11] else
        "Early schooling had disruptions — multiple schools, difficult peers, or an environment that wasn\'t ideal. You had to work harder than others."
        if h4_lord_h in [6,8,12] else
        "Ordinary school experience — neither exceptionally good nor particularly difficult."),

        f"<b>Learning ability and style</b> — " + (
        "Rapid, analytical mind — you excelled in subjects requiring precision and logical reasoning. Mathematics, science, and structured argument are natural strengths."
        if merc_dig in ["Own","Exalted","Exalted/Own"] else
        "Intuitive, experiential learner — you grasped subjects you cared about deeply while struggling with rote memorisation. You think in concepts and patterns, not facts."
        if merc_dig=="Debil" else
        "Balanced learning capacity — you adapt to different subjects and handle both analytical and creative tasks."),

        f"<b>Higher education</b> — " + (
        "Strong higher education indicators — you likely completed a degree or advanced qualification, possibly with distinction. Academic achievement was a real chapter in your story."
        if h9_lord_h in [1,5,9,10,11] else
        "Higher education faced obstacles — financial, motivational, or circumstantial. You may have taken a non-linear path, or substituted experience for formal degrees."
        if h9_lord_h in [6,8,12] else
        "Moderate higher education journey — you completed what was needed, though not the most glamorous academic experience."),

        f"<b>Subjects and specialisation</b> — " + (
        "Technical, scientific, or mathematical fields are your strongest domains. Engineering, computers, finance, law — anything requiring systematic thinking."
        if pos["Mercury"]["rasi"] in ["Gemini","Virgo"] else
        "Humanities, arts, psychology, or spiritual subjects draw you — you understand people, meaning, and beauty better than algorithms."
        if pos["Mercury"]["rasi"] in ["Cancer","Scorpio","Pisces"] else
        "Practical, applied fields — business, administration, or trades where you can learn and produce simultaneously."),

        f"<b>Foreign education or study abroad</b> — " + (
        "Strong possibility of studying abroad or through foreign-origin institutions and knowledge systems."
        if rahu_h in [9,12] or h9_lord_h in [12] else
        "Education is primarily domestic — foreign study may have been considered but not the primary path."),

        f"<b>Lifelong learning</b> — " + (
        "Your love of learning does not stop with formal education — you are a natural lifelong student. Books, courses, mentors, and new ideas feed your mind well into later decades."
        if jup_dig in ["Own","Exalted"] or jup_h in [1,5,9] else
        "Formal education may have ended early — further learning comes through work and experience rather than structured programmes."),

        f"<b>Creative and artistic education</b> — " + (
        "Strong aptitude for arts, music, or creative pursuits — these could have been developed through education or were self-taught."
        if h5_occ and any(p in h5_occ for p in ["Venus","Moon","Mercury"]) else
        "Technical or intellectual tracks dominated education — arts were a side interest rather than a central pursuit."),

        f"<b>Peak academic years</b> — "
        f"Academic success peaks during Mercury and Jupiter dasha periods — the natural education engines of the chart. "
        f"Results in formal examinations, certifications, or competitive selections tend to come in these windows.",
    ]

    # ── 5. MARRIAGE ──
    h7_occ=occupants(7); h7_lord=lord_of(7); h7_lord_h=lord_house(7)
    ven_h=pos["Venus"]["house"]; ven_dig=DIGNITIES.get(("Venus",pos["Venus"]["rasi"]),"neutral")
    is_manglik=pos["Mars"]["house"] in [1,2,4,7,8,12]
    now_m=dt.datetime.now()
    marriage_windows=[]
    for md in mds:
        if md["lord"] in ["Venus","Jupiter","Moon"] and md["end"]>now_m:
            is_active=md["start"]<=now_m<=md["end"]
            marriage_windows.append((md["lord"],md["start"].strftime("%b %Y"),md["end"].strftime("%b %Y"),is_active))
    SPOUSE_SIGN_NATURE={
        "Aries":"energetic, independent, pioneering, sometimes impatient",
        "Taurus":"steady, sensual, loyal, comfort-loving, stubborn at times",
        "Gemini":"witty, communicative, social, changeable",
        "Cancer":"nurturing, emotional, home-loving, protective",
        "Leo":"charismatic, proud, generous, dramatic",
        "Virgo":"analytical, service-oriented, health-conscious, sometimes critical",
        "Libra":"charming, diplomatic, artistic, balance-seeking",
        "Scorpio":"intense, loyal, secretive, transformative",
        "Sagittarius":"philosophical, adventurous, freedom-loving, direct",
        "Capricorn":"ambitious, disciplined, career-focused, reserved",
        "Aquarius":"independent, unconventional, humanitarian, intellectual",
        "Pisces":"empathetic, spiritual, creative, sensitive",
    }
    h7_sign=RASIS[(lagna_idx+6)%12]
    spouse_nature=SPOUSE_SIGN_NATURE.get(h7_sign,"balanced and adaptable")
    pred["marriage"]=[
        f"<b>Marriage timing</b> — " + (
        "The chart supports marriage in the mid-to-late 20s or early 30s — a natural window within favourable planetary periods."
        if ven_h in [1,2,5,7,11] else
        "Marriage may come slightly later than peers — the chart suggests taking time to develop individually before the right partner arrives."
        if ven_h in [6,8,12] else
        "Marriage timing is average — within the normal window for your social context.") + (
        " The current period is an active marriage window." if any(w[3] for w in marriage_windows) else ""),

        f"<b>Upcoming marriage windows</b> — " + (
        "; ".join(f"{w[0]} period {w[1]}–{w[2]}" + (" ★ NOW" if w[3] else "") for w in marriage_windows[:3])
        if marriage_windows else
        "Major Venus/Jupiter/Moon periods have mostly passed — marriage is still possible through Antar Dasha activations."),

        f"<b>Spouse personality</b> — Your partner is likely to be {spouse_nature}. "
        f"The 7th house sign gives the primary personality template of the life partner.",

        f"<b>Spouse background and appearance</b> — " + (
        "Your spouse is likely to be attractive, charming, and artistic — someone who draws attention naturally."
        if ven_dig in ["Own","Exalted","Exalted/Own"] else
        "Your spouse may come from a challenging background or carry their own life burdens — this becomes a shared journey of growth."
        if ven_dig=="Debil" else
        "Your spouse is likely pleasant and balanced — a reliable life companion.") + (
        " They may come from a different region, culture, or background than your own family." if h7_lord_h in [9,12] else ""),

        f"<b>Marriage quality and happiness</b> — " + (
        "A harmonious, long-lasting marriage is strongly indicated — the chart supports a loving and supportive partnership."
        if ven_dig in ["Own","Exalted","Exalted/Own"] and h7_lord_h in [1,2,4,5,7,9,10,11] else
        "Marriage goes through real challenges — possibly financial strain, communication difficulties, or differences in values. Success requires conscious effort from both sides."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Marriage is stable and functional — a reliable partnership built on mutual respect."),

        f"<b>Mars and marriage intensity</b> — " + (
        "Mars influences the marriage zone — intensity, passion, and directness define the partnership dynamic. A partner who can match your energy is essential."
        if is_manglik else
        "No Mars intensity influence on the marriage house — partnership energies are more harmonious by default."),

        f"<b>Possibility of second relationship</b> — " + (
        "The chart suggests the possibility of a second significant relationship in life — either a second marriage or a major committed partnership after the first."
        if h7_lord_h in [8,12] or (h7_occ and any(p in h7_occ for p in ["Saturn","Rahu"])) else
        "The chart indicates one primary, lasting marriage — serial relationships are not the chart\'s pattern."),

        f"<b>Spouse\'s career</b> — " + (
        "Your spouse is likely to have an independent career or business — a professionally active and ambitious partner."
        if h7_lord_h in [3,6,10,11] else
        "Your spouse may be in a creative, healing, or service-oriented field — teacher, doctor, artist, or social worker type."
        if h7_lord_h in [4,5,9] else
        "Your spouse\'s career follows a conventional or family-supported path."),
    ]

    # ── 6. CHILDREN ──
    h5_occ=occupants(5); h5_lord=lord_of(5); h5_lord_h=lord_house(5)
    jup_h=pos["Jupiter"]["house"]; jup_dig=DIGNITIES.get(("Jupiter",pos["Jupiter"]["rasi"]),"neutral")
    pred["children"]=[
        f"<b>Children — likelihood and ease</b> — " + (
        "Strong, easy conception indicators — children come naturally and early in marriage. Fertility is not a concern in this chart."
        if jup_dig in ["Own","Exalted"] and h5_lord_h in [1,5,9,11] else
        "Conception may require some patience — the chart suggests delayed children or possible need for medical support. This does not mean no children — the journey may take longer."
        if jup_dig=="Debil" or h5_lord_h in [6,8,12] else
        "Children arrive in normal course — no exceptional ease or difficulty indicated."),

        f"<b>Number of children</b> — " + (
        "The chart suggests 2–3 children are well-supported."
        if not h5_occ or jup_h in [1,5,9,11] else
        "One or two children is the natural indication — quality of the parent-child bond matters more than quantity."),

        f"<b>Children\'s character</b> — " + (
        "Children are likely to be intelligent, academically gifted, or artistic — they will make the family proud through achievements."
        if any(p in h5_occ for p in ["Jupiter","Mercury","Venus","Moon"]) else
        "Children will be energetic and strong-willed — their path requires a firm but loving guiding hand."
        if any(p in h5_occ for p in ["Mars","Sun"]) else
        "Children follow a straightforward, steady path — solid contributors to the family."),

        f"<b>Timing of first child</b> — " + (
        "First child typically arrives within 1–3 years of marriage, in a Jupiter or Venus sub-period."
        if jup_dig in ["Own","Exalted"] else
        "First child may come after age 30 or after a waiting period — the chart suggests the right time is when life circumstances are stable."
        if h5_lord_h in [6,8,12] or jup_dig=="Debil" else
        "First child comes in normal timing — within the first few years of marriage, in a favourable dasha."),

        f"<b>Parent-child bond</b> — " + (
        "Deep, devoted, and fulfilling parent-child relationship — children bring profound joy and are a central life theme. You are made to be a parent."
        if jup_dig in ["Own","Exalted"] or h5_lord_h in [1,4,5,9] else
        "The parent-child relationship, while loving, may carry challenges — children might be demanding or need extra support. The bond grows through these trials."
        if h5_lord_h in [6,8,12] else
        "A warm, balanced parent-child dynamic — you provide structure and love in equal measure."),

        f"<b>Children\'s success</b> — " + (
        "Children are likely to find success in their careers and social standing — they bring honour to the family name."
        if h5_lord_h in [9,10,11] else
        "Children may face their own life challenges — their path requires more patience from you. The reward comes later."
        if h5_lord_h in [6,8,12] else
        "Children\'s success is steady and self-built — not dramatic, but solid."),

        f"<b>Spiritual connection through children</b> — "
        f"Children serve as a spiritual mirror and karmic teacher — your deepest growth as a person comes through the experience of parenthood. "
        f"This is a marked theme in the chart.",
    ]

    # ── 7. CAREER & PROFESSION ──
    h10_occ=occupants(10); h10_lord=lord_of(10); h10_lord_h=lord_house(10)
    h6_lord=lord_of(6); h6_lord_h=lord_house(6)
    karakas_list=chara_karakas(chart)
    karaka_amk=karakas_list[1][1] if len(karakas_list)>1 else "Mercury"
    CAREER_BY_PLANET={
        "Sun":"government, administration, politics, leadership, medicine",
        "Moon":"public service, hospitality, nursing, import-export, real estate",
        "Mars":"engineering, military, police, surgery, real estate, sports",
        "Mercury":"IT, finance, accounting, writing, teaching, commerce, consulting",
        "Jupiter":"education, law, banking, religion, advisory roles",
        "Venus":"arts, fashion, entertainment, luxury goods, design, hospitality",
        "Saturn":"mining, agriculture, construction, labour management, research",
        "Rahu":"technology, foreign companies, unconventional fields, media",
        "Ketu":"research, spirituality, medicine, mystical arts",
    }
    pred["career"]=[
        f"<b>Natural career domain</b> — Your strongest professional fields are: "
        f"{CAREER_BY_PLANET.get(h10_lord,\'general management and leadership\')}. "
        f"These are the arenas where your natural talents and chart energy converge.",

        f"<b>Soul\'s career calling</b> — Beyond the practical field, your deeper professional calling involves "
        f"{CAREER_BY_PLANET.get(karaka_amk,\'advisory and wisdom-sharing roles\')}. "
        f"This is what gives your work meaning beyond the paycheck.",

        f"<b>Job vs. business</b> — " + (
        "You are built for independent work — entrepreneurship, consulting, or leadership. A salaried routine constrains you. Business or a senior position with autonomy is where you thrive."
        if h10_lord_h in [1,3,7,10] else
        "You perform best in an established organisational structure — a career with seniority, team support, and a clear growth ladder suits you more than starting from scratch."
        if h10_lord_h in [4,5,9] else
        "You can succeed in either — the path that fits your life phase is the right one."),

        f"<b>Career trajectory</b> — " + (
        "Strong upward career trajectory — promotions, recognition, and increasing authority are well-marked. The career builds in visible steps."
        if h10_lord_h in [1,4,9,10,11] else
        "Career has a non-linear path — setbacks and rebuilds are part of the story. The eventual position is often better than what the early years suggested."
        if h10_lord_h in [6,8,12] else
        "Steady, moderate career growth — consistent advancement without dramatic highs or lows."),

        f"<b>Government vs. private sector</b> — " + (
        "Strong government or public sector alignment — stability, authority, and public trust are your career environment."
        if h10_lord in ["Sun","Saturn","Jupiter"] else
        "Private sector, business, or entrepreneurship is the natural domain — you flourish outside bureaucratic structures."
        if h10_lord in ["Mercury","Venus","Rahu"] else
        "You can function in either — the sector matters less than the role and autonomy within it."),

        f"<b>Career peak years</b> — "
        f"Career peaks typically come during the Maha Dasha or Antar Dasha of the 10th lord. "
        f"These are the years when the professional story accelerates — promotions, launches, public recognition, or major role changes.",

        f"<b>Foreign career opportunities</b> — " + (
        "Strong foreign career component — working abroad, for foreign companies, or in internationally-oriented roles is a marked possibility."
        if pos["Rahu"]["house"] in [9,10,12] or h10_lord_h in [12] else
        "Career is primarily domestic — international work is supplemental to the main professional story."),

        f"<b>Authority and leadership</b> — " + (
        "Natural leadership capacity — people follow you without being asked. Management and leadership roles come because others recognise your capacity."
        if h10_lord in ["Sun","Jupiter","Mars"] or h10_lord_h in [1,4,10] else
        "Leadership grows through expertise — you earn authority through knowledge and track record rather than through born charisma."),

        f"<b>Career in later life</b> — " + (
        "Later career years (post-45) bring the greatest recognition. The early years build the foundation; the second half delivers the rewards."
        if jup_dig in ["Own","Exalted"] else
        "Career activity may gradually reduce in later years — a natural pull toward quieter work or semi-retirement. A healthy transition."),
    ]

    # ── 8. WEALTH ──
    h2_occ=occupants(2); h2_lord=lord_of(2); h2_lord_h=lord_house(2)
    h11_lord=lord_of(11); h11_lord_h=lord_house(11)
    ven_dig=DIGNITIES.get(("Venus",pos["Venus"]["rasi"]),"neutral")
    pred["wealth"]=[
        f"<b>Wealth potential overall</b> — " + (
        "High wealth potential — the chart supports significant financial accumulation. Multiple income sources are indicated."
        if jup_dig in ["Own","Exalted"] and h2_lord_h in [1,2,5,9,10,11] else
        "Wealth requires sustained effort — the chart shows financial challenges that must be overcome through discipline and conservative investment. Avoid speculation."
        if jup_dig=="Debil" else
        "Moderate wealth — you will build a comfortable life but significant riches require deliberate effort and smart financial decisions."),

        f"<b>Primary income source</b> — " + (
        "Career and profession is the primary wealth engine — steady, structured income that grows with seniority and expertise."
        if h2_lord_h in [6,10] else
        "Business and self-generated income is the primary wealth path — entrepreneurial activity, trading, or consulting."
        if h2_lord_h in [3,7] else
        "Wealth comes through multiple streams — property, investments, family money, and career income all contribute."
        if h2_lord_h in [2,11] else
        "Income is tied to partnerships, foreign work, or unconventional sources."),

        f"<b>Inheritance and family wealth</b> — " + (
        "Meaningful family inheritance — either in money, property, or valuable assets that come to you in due course."
        if h2_lord_h in [2,4,9] else
        "Wealth is primarily self-built — what the family provides is support and values, not money."),

        f"<b>Peak wealth years</b> — "
        f"Wealth peaks are most prominent during Venus, Jupiter, and the 2nd/11th house lord periods in the Vimshottari sequence. "
        f"Invest during these periods rather than spending excessively.",

        f"<b>Debt and financial risk</b> — " + (
        "Low debt risk — you are naturally inclined toward financial prudence."
        if h2_lord_h not in [6,8,12] and sat_dig not in ["Debil"] else
        "Debt is a real risk — possible financial overextension or loans that become burdens. Conservative financial planning is essential. Avoid co-signing for others."),

        f"<b>Best investments</b> — " + (
        "Property, gold, and traditional investments are your strongest wealth-builders. Real estate especially is well-indicated."
        if pos["Mars"]["house"] in [1,4,10] or pos["Saturn"]["house"] in [4,10] else
        "Stocks, business equity, or knowledge-based investments are better for you than physical assets alone."),

        f"<b>Financial life in later years</b> — " + (
        "Comfortable and secure financial life in later years — the chart supports building enough to live well without financial anxiety in old age."
        if jup_dig in ["Own","Exalted"] or h11_lord_h in [1,2,9,11] else
        "Later financial years require pre-planning — creating a pension, investment corpus, or property that yields income is essential. Don\'t leave this to chance."),

        f"<b>Overall wealth verdict</b> — " + (
        "A wealth-building chart — a financially comfortable and eventually prosperous life through sustained, disciplined effort."
        if jup_h in [1,4,5,7,9,11] else
        "Wealth comes but not without effort and some setbacks. Those who plan carefully do well."),
    ]

    # ── 9. HEALTH ──
    h6_occ=occupants(6); h8_occ=occupants(8); h8_lord=lord_of(8)
    asc_lord=chart.get("lagna_lord","Jupiter")
    asc_lord_dig=DIGNITIES.get((asc_lord,pos[asc_lord]["rasi"]),"neutral") if asc_lord in pos else "neutral"
    pred["health"]=[
        f"<b>Overall constitution</b> — " + (
        "Robust health constitution — natural resistance to illness, good immunity, and generally high energy. You bounce back from illness faster than most."
        if asc_lord_dig in ["Own","Exalted","Exalted/Own"] else
        "Sensitive health constitution — more susceptible to environmental, emotional, and dietary triggers. Your body requires careful maintenance."
        if asc_lord_dig=="Debil" else
        "Average constitution — neither unusually strong nor fragile. Health responds well to standard care and regular habits."),

        f"<b>Body\'s vulnerable zones</b> — "
        f"The most common health challenges are tied to " + (
        "digestion, stomach, and emotional or stress-linked conditions."
        if chart["lagna"] in ["Cancer","Virgo"] else
        "joints, bones, skin, and chronic conditions."
        if chart["lagna"] in ["Capricorn","Aquarius"] else
        "head, blood pressure, and heat-related conditions."
        if chart["lagna"] in ["Aries","Leo","Scorpio"] else
        "lungs, throat, and respiratory issues."
        if chart["lagna"] in ["Taurus","Gemini","Libra"] else
        "liver, thighs, and excess-related conditions."),

        f"<b>Mental health and emotional balance</b> — " + (
        "Strong psychological resilience — you can handle significant stress without breaking. Mental health is one of your genuine strengths."
        if moon_dig in ["Own","Exalted","Exalted/Own"] else
        "Mental and emotional vulnerability is present — anxiety, overthinking, or mood instability can be recurring challenges. Mindfulness, routine, and social connection are protective factors."
        if moon_dig=="Debil" else
        "Emotionally balanced most of the time, with some sensitivity to stress. Standard self-care keeps you on an even keel."),

        f"<b>Surgery or hospitalisation risk</b> — " + (
        "The chart does not flag major surgery or hospitalisation risk above average — standard medical care is the relevant approach."
        if not h8_occ and pos["Mars"]["house"] not in [6,8,12] else
        "There is some indication of a significant medical event — possibly surgery, hospitalisation, or intensive treatment. This is not permanent; it is a defined period followed by recovery."),

        f"<b>Longevity indicators</b> — " + (
        "Strong longevity indicators — the chart supports a long life with productive years well into old age."
        if asc_lord_dig in ["Own","Exalted"] and jup_dig not in ["Debil"] else
        "Longevity requires conscious health investment — proactive health management is genuinely important."
        if asc_lord_dig=="Debil" else
        "Average to moderate longevity — taking care of the body, especially between ages 35–55, directly influences the later decades."),

        f"<b>Diet and lifestyle recommendations</b> — " + (
        "You thrive on regularity — consistent meal times, adequate sleep, and a structured daily routine protect your health better than any medicine."
        if chart["lagna"] in ["Virgo","Capricorn","Taurus"] else
        "Your health is strongly tied to your emotional state — stress management is non-negotiable. When you are at peace emotionally, the body responds well."
        if chart["lagna"] in ["Cancer","Scorpio","Pisces"] else
        "Physical activity is your health lifeline — the body needs movement and regular exercise to stay in balance. A sedentary lifestyle is your primary health risk."),

        f"<b>Health in peak years (25–45)</b> — " + (
        "Peak working years are generally healthy — the body supports the demands placed on it during this period."
        if asc_lord_dig not in ["Debil"] else
        "Watch health carefully during high-pressure work periods — the body absorbs professional stress and needs deliberate recovery time."),

        f"<b>Ageing and health after 50</b> — " + (
        "Health holds up well into later years with reasonable care."
        if jup_dig in ["Own","Exalted"] else
        "After 50, preventive health focus becomes essential — joints, heart, and digestion are areas to monitor proactively."),
    ]

    # ── 10. TRAVEL & FOREIGN ──
    h12_occ=occupants(12); h12_lord=lord_of(12); h12_lord_h=lord_house(12)
    pred["travel"]=[
        f"<b>Foreign travel pattern</b> — " + (
        "Significant international travel and foreign connection is marked — this is someone whose life story includes meaningful time in foreign lands."
        if rahu_h in [9,12] or h12_lord_h in [1,9,12] else
        "Travel is present but not a defining life theme — domestic or regional movement is more prominent than international."),

        f"<b>Foreign settlement possibility</b> — " + (
        "Genuine possibility of living abroad for an extended period — foreign residence, work, or even permanent settlement in another country is supported by the chart."
        if pos["Rahu"]["house"] in [9,12] and h12_lord_h in [1,4,12] else
        "Foreign settlement is not strongly marked — you may travel significantly but home base remains in the country of origin."),

        f"<b>Career-driven travel</b> — " + (
        "Career and foreign opportunities are linked — professional growth often involves crossing borders, working with international clients, or relocating for work."
        if h10_lord_h in [9,12] or pos["Rahu"]["house"]==10 else
        "Career growth is primarily domestic — international work is supplemental to the main professional story."),

        f"<b>Pilgrimage and spiritual travel</b> — " + (
        "A strong pull toward sacred places, pilgrimage sites, or spiritually significant travel. At least one major pilgrimage or spiritually transformative journey is marked in the chart."
        if h9_lord_h in [9,12] or pos["Jupiter"]["house"] in [9,12] else
        "Religious travel is occasional rather than a defining theme."),

        f"<b>Age of significant foreign travel</b> — "
        f"Foreign travel becomes significant typically in the Rahu or 12th lord Maha Dasha period. "
        f"For many, this corresponds to the late 20s or 30s — a natural expansion phase.",

        f"<b>Travel challenges and returns</b> — " + (
        "Travel is generally smooth and rewarding — journeys open doors rather than creating problems."
        if h12_lord_h not in [6,8] else
        "Some journeys bring complications — visa issues, unexpected delays, or health challenges abroad. Travel with extra preparation and flexibility."),

        f"<b>Connection to foreign cultures</b> — " + (
        "A natural affinity for foreign cultures, languages, and ways of life — you assimilate well in different environments and often feel more at home abroad than expected."
        if pos["Rahu"]["house"] in [1,9,12] else
        "You appreciate foreign exposure but the heart remains rooted — home culture and family ties pull you back consistently."),
    ]

    # ── 11. PROPERTY & ASSETS ──
    h4_occ=occupants(4); h4_lord=lord_of(4); h4_lord_h=lord_house(4)
    pred["property"]=[
        f"<b>Home ownership</b> — " + (
        "Strong property ownership indicators — you are likely to own your home and possibly additional property. Real estate is part of your wealth story."
        if h4_lord_h in [1,2,4,5,9,10,11] and pos["Mars"]["house"] in [1,4,10] else
        "Property ownership comes eventually but may require patience — possibly renting through early and middle years before owning in the 35–45 window."
        if h4_lord_h in [6,8,12] else
        "Standard property journey — ownership comes at the right life stage without exceptional difficulty."),

        f"<b>Ancestral property</b> — " + (
        "Some ancestral property is indicated — either inherited land, home, or family assets that come to you in due course."
        if h4_lord_h in [2,4,9] else
        "Ancestral property is not a major factor — what you own, you build yourself through your own earnings."),

        f"<b>Multiple properties</b> — " + (
        "The chart supports owning more than one property in life — a primary home plus investment property or land is achievable."
        if jup_dig in ["Own","Exalted"] and pos["Mars"]["house"] in [1,4,7,10] else
        "One good home is the chart\'s realistic indication — multi-property portfolios require deliberate saving and planning."),

        f"<b>Vehicles and luxury assets</b> — " + (
        "Comfortable vehicle ownership — you will drive good vehicles as a natural part of your lifestyle, not just as a necessity."
        if ven_dig in ["Own","Exalted"] else
        "Vehicles are functional tools rather than status symbols — practical choices over luxury."),

        f"<b>Home environment quality</b> — " + (
        "Your home is a place of comfort, beauty, and emotional restoration — you invest in making your living space genuinely pleasant."
        if h4_lord_h in [1,4,5] and ven_dig in ["Own","Exalted"] else
        "Home is functional and adequate — not a luxury priority, but it serves your needs well."),

        f"<b>Property in foreign lands</b> — " + (
        "Some possibility of owning or holding property abroad — through work placement, investment, or foreign residence."
        if pos["Rahu"]["house"] in [4,12] else
        "Property is domestic — no strong indicator of foreign real estate."),

        f"<b>Best timing for property purchase</b> — "
        f"Property acquisition is best attempted during Jupiter, Venus, or Saturn Maha Dasha periods — "
        f"these are the natural asset-building windows in the chart.",
    ]

    # ── 12. SOCIAL STATUS, FAME, POWER ──
    h10_occ=occupants(10); h10_lord=lord_of(10); h10_lord_h=lord_house(10)
    sun_h=pos["Sun"]["house"]
    pred["status"]=[
        f"<b>Fame and public recognition</b> — " + (
        "Genuine fame potential — this chart can achieve widespread recognition, public honour, or significant social standing. The name carries weight."
        if h10_lord_h in [1,9,10,11] and sun_dig in ["Own","Exalted"] else
        "Local or professional recognition is more strongly marked than broad fame — respected in your field or community."
        if h10_lord_h in [1,5,9] else
        "Fame is not the primary chart theme — you build reputation through work rather than through visibility."),

        f"<b>Authority and leadership capacity</b> — " + (
        "Natural authority — people follow you without being asked. Leadership positions arrive because others recognise your capacity."
        if h10_lord in ["Sun","Jupiter","Mars"] or sun_dig in ["Own","Exalted"] else
        "Leadership comes through expertise — you earn respect through proven capability rather than natural charisma."),

        f"<b>Career recognition timing</b> — " + (
        "Recognition tends to come in the 35–50 age range — the career builds for years before the public rewards begin. Early patience is rewarded substantially later."
        if h10_lord_h in [4,8,9] else
        "Recognition can come relatively early — the chart supports visibility even in the 25–35 window if the right opportunities are pursued actively."),

        f"<b>Government honours and awards</b> — " + (
        "Some possibility of formal honours, awards, or government recognition during a peak career period."
        if sun_dig in ["Own","Exalted"] and h10_lord_h in [1,9,10] else
        "Formal awards are not strongly marked — recognition in this chart comes through peer respect and professional reputation."),

        f"<b>Social standing in community</b> — " + (
        "Respected and well-regarded in your social circle and community — people trust your judgment and seek your opinion."
        if jup_dig in ["Own","Exalted"] or h10_lord_h in [1,4,9] else
        "Social standing is average — neither exceptionally prominent nor marginal. You move comfortably in your social environment."),

        f"<b>Online presence and media</b> — " + (
        "The chart supports public visibility in media, online platforms, or content creation — a voice that others listen to."
        if pos["Rahu"]["house"] in [3,10,11] else
        "Media presence is not a natural chart strength — professional accomplishment, not public personality, is the better route to recognition."),

        f"<b>Reputation and character</b> — " + (
        "Low reputation-damage risk — the chart does not indicate major scandals or falls from grace. Character remains intact."
        if h10_lord_h not in [6,8,12] and pos["Saturn"]["house"] not in [1,10] else
        "There is a risk period where reputation faces challenge — maintaining ethical standards during Saturn transit periods is essential."),
    ]

    # ── 13. RELATIONSHIPS & ENEMIES ──
    h7_lord=lord_of(7); h7_lord_h=lord_house(7)
    h6_lord=lord_of(6); h6_lord_h=lord_house(6)
    pred["relationships"]=[
        f"<b>Friendship and social network</b> — " + (
        "Wide, warm, and loyal social network — you attract friends naturally and maintain long-term friendships with ease. Your circle is a genuine source of support and joy."
        if jup_dig in ["Own","Exalted"] or h11_lord_h in [1,2,5,11] else
        "Selective and smaller friendship circle — you prefer a few deep relationships over many shallow ones. Quality matters far more than quantity."
        if h11_lord_h in [6,8,12] else
        "Balanced social life — functional friendships that serve both connection and practical purposes."),

        f"<b>Romantic nature</b> — " + (
        "Romantic and expressive in love — you fall deeply and commit fully. Love is one of life\'s great themes for you."
        if ven_dig in ["Own","Exalted"] else
        "Cautious in romance — you protect your heart and need trust to be established before opening emotionally. When you do commit, it is wholehearted."
        if ven_dig=="Debil" else
        "Balanced approach to romance — neither impulsively romantic nor emotionally guarded."),

        f"<b>Enemies and opposition</b> — " + (
        "Few significant enemies — you do not invite conflict and your chart does not attract serious opposition."
        if pos["Mars"]["house"] not in [1,7] and h6_lord_h not in [1,7] else
        "You will face real opponents in life — people who actively work against your interests. Navigate opposition strategically rather than emotionally."),

        f"<b>Hidden enemies</b> — " + (
        "Some risk of betrayal or hidden opposition — someone in your inner circle may work against you at some point. Discretion about personal plans is wise."
        if pos["Saturn"]["house"] in [4,7,12] or pos["Rahu"]["house"] in [7,12] else
        "Hidden enemies are not a major chart theme — most opposition you face is visible and manageable."),

        f"<b>Legal disputes</b> — " + (
        "Moderate legal dispute risk — some involvement with legal matters in one chapter of life. Property, business, or family law is the likely domain."
        if h6_lord_h in [1,7,10] else
        "Legal disputes are not a featured life theme — conflicts generally resolve through negotiation rather than formal proceedings."),

        f"<b>Trust and betrayal patterns</b> — " + (
        "Your trust is strong but sometimes misplaced — you see the best in people, which is beautiful but occasionally exploited. Trusting your instincts about character is a key life lesson."
        if moon_dig in ["Own","Exalted"] else
        "You are naturally guarded with trust — it takes time for others to earn your full confidence. This protects you from betrayal but can slow meaningful connections."),

        f"<b>Forgiveness and reconciliation</b> — " + (
        "You have a healthy capacity for forgiveness — broken relationships can often be repaired with you through honest conversation."
        if jup_dig in ["Own","Exalted"] else
        "Old wounds take time to heal with you — forgiveness is a deliberate act that requires real effort. The effort is worth it."),
    ]

    # ── 14. SPIRITUALITY ──
    h9_occ=occupants(9); h9_lord=lord_of(9); h9_lord_h=lord_house(9)
    h12_occ=occupants(12); h12_lord=lord_of(12); h12_lord_h=lord_house(12)
    ketu_h=pos["Ketu"]["house"]
    pred["spirituality"]=[
        f"<b>Spiritual orientation</b> — " + (
        "Deeply spiritual by nature — religion, philosophy, or inner seeking is a genuine life theme. You have a contemplative dimension that runs through everything you do."
        if ketu_h in [1,4,5,8,9,12] or h9_lord_h in [9,12] else
        "Religious participation is conventional and family-tradition oriented — you follow inherited practices with respect but are not driven to deep independent seeking."),

        f"<b>Religious practice style</b> — " + (
        "Ritual, mantra, and structured devotion resonate with you — you connect to the divine through form, discipline, and repetition."
        if chart["lagna"] in ["Taurus","Virgo","Capricorn","Scorpio"] else
        "You connect to the divine through nature, silence, and direct inner experience rather than elaborate ritual."
        if chart["lagna"] in ["Cancer","Pisces","Sagittarius"] else
        "Your spirituality is philosophically oriented — you seek to understand the underlying principles rather than just practise surface rituals."),

        f"<b>Guru and teacher relationship</b> — " + (
        "A significant spiritual teacher or guru figure is part of your life journey — someone who transforms your understanding of existence at a pivotal moment."
        if jup_dig in ["Own","Exalted"] or h9_lord_h in [9] else
        "Spiritual learning for you is more through books, solo inquiry, and life experience than through a single revered teacher."),

        f"<b>Meditation and inner practice</b> — " + (
        "Natural meditator — inner stillness is accessible to you when you commit to the practice. You are capable of genuine depth in contemplative work."
        if ketu_h in [1,8,12] or chart["lagna"] in ["Pisces","Scorpio"] else
        "Meditation is not your natural spiritual channel — you connect better through active service, devotion, or philosophical study."),

        f"<b>Moksha and liberation orientation</b> — " + (
        "The chart has a marked spiritual liberation component — in later life, worldly ambitions naturally give way to a deeper pull toward meaning, service, and inner peace."
        if ketu_h in [8,12] or h12_lord_h in [12] else
        "Moksha is not the dominant chart theme — this is a life oriented toward dharmic engagement with the world, not withdrawal from it."),

        f"<b>Charity and service</b> — " + (
        "Genuine charitable impulse — giving back and serving those less fortunate are natural expressions of your values."
        if jup_dig in ["Own","Exalted"] or h12_lord_h in [9,12] else
        "Charity is occasional rather than a core life expression — you give when moved but it is not a defining theme."),

        f"<b>Spiritual timing</b> — "
        f"Spiritual depth typically increases markedly during Ketu and Jupiter Maha Dasha periods — "
        f"natural times for retreats, life-review, philosophical change, or religious commitment intensification.",
    ]

    # ── 15. TALENTS & SKILLS ──
    h5_occ=occupants(5); h3_occ=occupants(3); h3_lord=lord_of(3)
    ven_h=pos["Venus"]["house"]
    pred["talents"]=[
        f"<b>Musical and artistic talent</b> — " + (
        "Strong musical and artistic talent — whether as a performer, composer, or deeply appreciative listener, music is woven into your soul. Creative arts in general are a genuine gift."
        if ven_dig in ["Own","Exalted"] or ven_h in [1,2,5] else
        "Aesthetic appreciation is present but performing arts are not the primary talent — you enjoy art more as a consumer than as creator."),

        f"<b>Writing and communication talent</b> — " + (
        "Natural writer and communicator — words come easily, arguments form cleanly, and your ability to express complex ideas accessibly is above average."
        if merc_dig in ["Own","Exalted","Exalted/Own"] or merc_h in [1,3,5] else
        "Communication is functional rather than exceptional — writing and speaking work as tools but are not standout gifts."),

        f"<b>Technical and analytical talent</b> — " + (
        "Strong technical capacity — you can handle complex systems, numbers, and analytical problems with genuine aptitude. Engineering, computing, mathematics, or strategic planning are natural domains."
        if merc_dig in ["Own","Exalted","Exalted/Own"] and chart["lagna"] in ["Gemini","Virgo","Capricorn","Aquarius"] else
        "Technical ability is adequate rather than exceptional — you can learn technical skills but they are not your primary edge."),

        f"<b>Sports and physical talent</b> — " + (
        "Athletic ability is genuinely present — coordination, physical drive, and competitive spirit make you effective in sport or physical disciplines."
        if mars_dig in ["Own","Exalted","Exalted/Own"] or pos["Mars"]["house"] in [1,3,6] else
        "Sports are enjoyable but not a standout talent — casual participation rather than competitive achievement."),

        f"<b>Teaching and mentoring talent</b> — " + (
        "Natural teacher and mentor — you have an ability to explain, inspire, and develop others that is a genuine gift. Students and juniors respond well to your guidance."
        if jup_dig in ["Own","Exalted"] or jup_h in [1,5,9] else
        "Teaching is possible but not an innate gift — you prefer doing to teaching."),

        f"<b>Intuitive and psychic sensitivity</b> — " + (
        "Unusually strong intuition — a sense for reading situations, people, and upcoming events that others do not have. This can be developed into a real practical skill."
        if ketu_h in [1,4,8,12] or chart["lagna"] in ["Cancer","Scorpio","Pisces"] else
        "Intuition operates at a normal level — useful but not a defining gift."),

        f"<b>Language and multilingual capacity</b> — " + (
        "Natural language ability — learning foreign languages comes relatively easily. You may become genuinely proficient in more than two languages through life."
        if merc_h in [3,9] or pos["Rahu"]["house"] in [3,9] else
        "Language facility is average — you learn what you need but not beyond practical necessity."),

        f"<b>Hidden or undeveloped talents</b> — "
        f"The chart suggests talents in the creative and intuitive domains that may be undeveloped — "
        f"perhaps suppressed in favour of practical career demands. These deserve deliberate cultivation, especially in the second half of life.",
    ]

    # ── 16. PAST LIVES & KARMA ──
    ketu_h=pos["Ketu"]["house"]; rahu_h=pos["Rahu"]["house"]
    sat_h=pos["Saturn"]["house"]
    pred["past_lives"]=[
        f"<b>Past life skills</b> — "
        f"You come into this life with already-developed skills in the domain of {HOUSE_THEMES.get(ketu_h,\'?\')}. "
        f"These come almost too naturally — which can create a paradox of competence without fulfilment. The soul has been here before.",

        f"<b>Soul\'s current growth edge</b> — "
        f"This lifetime\'s growth challenge is in the domain of {HOUSE_THEMES.get(rahu_h,\'?\')}. "
        f"This is where you will stretch, fail, obsess, and eventually master something unfamiliar to the soul. "
        f"It may feel unnatural but it is where growth happens.",

        f"<b>Debt to father lineage</b> — " + (
        "Indicators of father-lineage karmic debt are present — this shows up as challenges related to father, authority, or career that have a karmic resolution quality. Past-life issues with authority are being healed in this lifetime."
        if sun_h in [6,8,12] or sun_dig=="Debil" else
        "No strong father-lineage karmic debt — the paternal line karma is relatively clear in this chart."),

        f"<b>Debt to mother lineage</b> — " + (
        "Some mother-lineage karmic pattern is present — the mother relationship or feminine-lineage themes carry a dimension requiring healing through patience and forgiveness."
        if moon_dig=="Debil" or moon_h in [6,8,12] else
        "Mother-lineage karma is relatively resolved — the maternal bond in this life is more choice than karmic obligation."),

        f"<b>Relational karmic debt</b> — " + (
        "A past-life relational debt pattern is indicated — this shows up as complex romantic or partner dynamics in this lifetime. The soul is working through something unfinished from a past bond."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Relationship karma is relatively clean — romantic bonds in this life are more choice than karmic obligation."),

        f"<b>Inherited merit from past lives</b> — " + (
        "Strong inherited merit is present — the soul carries significant positive karma that shows up as unexpected help, fortunate timing, and a sense that the universe looks out for you at critical moments."
        if jup_dig in ["Own","Exalted"] or h9_lord_h in [9,11] else
        "Merit from past lives is moderate — what you receive in grace is balanced by what you must earn through effort. The universe is fair rather than generous."),

        f"<b>Karmic life pattern overall</b> — "
        f"This is a soul in active, engaged karmic processing — not a quiet life, but a meaningful one filled with significant lessons, "
        f"meaningful relationships, and the sense that events happen for a reason. The spiritual dimension of life is never far.",

        f"<b>How to resolve karmic debt</b> — "
        f"Service, charity, ritual for ancestors (especially on eclipse days and Amavasya), "
        f"and healing the specific relationships indicated by the problem planets are the most effective remedial paths in this chart.",
    ]

    # ── 17. ANNUAL PREDICTIONS ──
    today_ann=dt.datetime.now()
    b_ann=chart["birth"]
    birth_dt_ann=dt.datetime(b_ann["year"],b_ann["month"],b_ann["day"],b_ann["hour"],b_ann["min"])
    age_now=(today_ann-birth_dt_ann).days/365.25
    muntha_house=int(age_now%12)+1
    cur_md_lord=None; cur_md_years=None
    for md in mds:
        if md["start"]<=today_ann<=md["end"]:
            cur_md_lord=md["lord"]; cur_md_years=md["years"]; break
    pred["annual"]=[
        f"<b>Current year focus</b> — "
        f"The yearly activation falls on the domain of {HOUSE_THEMES.get(muntha_house,\'?\')} this year. "
        f"Events related to these themes are more likely and more significant during this annual cycle.",

        f"<b>Maha Dasha context</b> — " + (
        f"You are currently in the {cur_md_lord} Maha Dasha — a {cur_md_years:.1f}-year period shaped by {PLANET_ARCHETYPES.get(cur_md_lord,\'\')} themes. The annual layer runs inside this larger context."
        if cur_md_lord else
        "Your current Maha Dasha context provides the backdrop for all annual events — the yearly shifts are sub-themes within the larger period."),

        f"<b>This year\'s opportunity</b> — " + (
        "Career advancement and public recognition — push for visible achievements this year."
        if muntha_house in [10,11] else
        "Relationship building and partnership — important connections are made this year."
        if muntha_house in [7,9] else
        "Home, family, and property decisions — a good year for domestic investment."
        if muntha_house in [4,5] else
        "Inner reflection and spiritual growth — less external action, more inner consolidation."
        if muntha_house in [8,12] else
        "Health, service, and daily routine improvements — a foundational year for long-term wellbeing."),

        f"<b>This year\'s caution</b> — "
        f"The current annual cycle also activates a challenge zone — be cautious in decisions involving "
        f"{HOUSE_THEMES.get((muntha_house+5)%12+1,\'?\')} and avoid reckless commitments in this domain.",

        f"<b>Best months this year</b> — "
        f"The months when Jupiter and Venus transit favourable positions from your natal Moon tend to be "
        f"the peak months for any major initiative, decision, or life event this year.",

        f"<b>Annual wealth cycle</b> — " + (
        "Financially strong year — potential for income increase or windfall. A year to take calculated financial risks."
        if muntha_house in [2,11] else
        "Moderate financial activity — maintain and don\'t over-extend."
        if muntha_house in [1,4,5] else
        "Watch for unexpected expenses — financial conservatism and an emergency fund are important this cycle."),

        f"<b>Relationships this year</b> — " + (
        "Partnership and social themes are highlighted — marriage, business partnerships, or important new relationships are potential features this cycle."
        if muntha_house in [7,11] else
        "This is more an introspective than socially expansive year — existing relationships deepen while new connections are fewer."),

        f"<b>Health this year</b> — " + (
        "No major health flag this year — routine maintenance and standard care are sufficient."
        if muntha_house not in [6,8,12] else
        "Pay attention to health signals this year — do not ignore symptoms or postpone medical check-ups."),
    ]

    # ── 18. SPECIFIC EVENT PROBABILITIES ──
    pred["specific"]=[
        f"<b>Financial windfall or sudden gain</b> — " + (
        "Some probability of a significant unexpected financial event — inheritance, prize, unexpected business opportunity, or investment payoff during a Jupiter or Venus peak period."
        if jup_dig in ["Own","Exalted"] or (pos["Rahu"]["house"] in [2,11] and jup_h in [1,5,9,11]) else
        "Windfalls are not strongly marked — wealth in this chart is earned through effort rather than arriving unexpectedly. Stay cautious of get-rich-quick temptation."),

        f"<b>Legal or court matter risk</b> — " + (
        "Some legal involvement is possible in life — property, business, or family disputes that enter the formal legal system. Professional legal advice when needed is important."
        if h6_lord_h in [1,7,10] or pos["Saturn"]["house"] in [7,6] else
        "Legal disputes are not a significant life feature — conflicts resolve through negotiation rather than formal proceedings."),

        f"<b>Political career possibility</b> — " + (
        "The chart has markers for possible political involvement or significant public leadership — either direct political career or major influence in organisational leadership."
        if sun_dig in ["Own","Exalted"] and h10_lord_h in [1,9,10] else
        "Political career is not well-indicated — leadership expressed through professional excellence rather than political office."),

        f"<b>Accident or injury risk</b> — " + (
        "Some elevated accident risk during Mars-activated periods. Caution with vehicles, machinery, or physical risk during these windows."
        if mars_dig=="Debil" or pos["Mars"]["house"] in [6,8,12] else
        "Accident risk is at normal average level — standard caution and safety practices are sufficient."),

        f"<b>Legal restriction or imprisonment risk</b> — " + (
        "No strong indicator of imprisonment or severe legal restriction. The chart does not show this as a likely life feature."
        if h12_lord_h not in [1,6] and pos["Saturn"]["house"] not in [1,12] else
        "There is some indicator of legal restriction risk in certain periods — extreme caution around legal compliance, especially during Saturn-Rahu activations."),

        f"<b>Major medical event</b> — " + (
        "A significant health event at some point in life is a possibility — surgery, serious illness, or extended recovery. Being forewarned allows proactive care."
        if h8_occ or (pos["Mars"]["house"] in [6,8] and pos["Saturn"]["house"] in [6,8]) else
        "No major medical event is strongly marked — health journey follows a relatively normal trajectory."),

        f"<b>Relationship separation risk</b> — " + (
        "The chart shows some risk of marital tension or separation — incompatibility, third-party influence, or a major life disruption. Relationships require conscious maintenance."
        if ven_dig=="Debil" or h7_lord_h in [6,8,12] else
        "Marital stability is well-supported — separation is not a marked chart feature."),

        f"<b>Spiritual awakening event</b> — " + (
        "A genuine spiritual awakening or life-reorientation event is marked — likely during Ketu or Saturn Maha Dasha. The life before and after will feel qualitatively different."
        if ketu_h in [1,4,8,9,12] else
        "Spiritual development is gradual rather than a dramatic awakening — steady growth in wisdom rather than a crisis-led revelation."),
    ]

    return pred
'''

# Find and replace the old function
pattern = r'def all_predictions\(chart\):.*?return pred\n'
match = re.search(pattern, text, re.DOTALL)
if not match:
    print("ERROR: could not find all_predictions() in file")
    sys.exit(1)

new_text = text[:match.start()] + NEW_FUNC + '\n' + text[match.end():]
SRC.write_text(new_text, encoding="utf-8")
print(f"Done. Replaced all_predictions() ({match.end()-match.start()} chars -> {len(NEW_FUNC)} chars)")
print(f"File size: {SRC.stat().st_size/1024:.0f} KB")
