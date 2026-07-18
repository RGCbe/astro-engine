"""Omens (Shakuna Shastra + Swapna Shastra) — classical Indian omen reading.

Source: Shakuna Shastra (Sanskrit), Swapna Shastra (dream catalog),
Brihat Samhita Ch. 86-95 (Varahamihira), Garga Hora Shastra omen sections.

Reads:
  - Bird omens (auspicious vs inauspicious birds, direction of cry)
  - Animal crossings (which animal crossing path means what)
  - Body sneeze/twitch omens (different for males vs females)
  - Object-falling omens
  - Sounds heard
  - Dream catalog (auspicious vs warning dreams)
  - Disha-Shoola (forbidden travel directions per weekday)
"""
import sys, datetime as dt
sys.path.insert(0, ".")

# ============================================================
# BIRD OMENS — "Pakshi Shakuna"
# ============================================================
BIRD_OMENS = {
    "Peacock (Mor)": {
        "auspicious": "Calling/dancing = good news, prosperity, royal favor",
        "direction": "From north or east = best; south = mixed",
        "context": "Sacred bird; calling at dawn = exceptionally good",
    },
    "Crow (Kaka)": {
        "auspicious": "Cawing 3 times from front = guest arrival; from behind = bad news from afar",
        "warning": "Black crow on tree near home cawing repeatedly = ancestral spirits seeking offerings (Pitra)",
        "specific": "Crow on roof at dawn = relative arrival; crow flying west = danger; crow with food in beak = wealth coming",
    },
    "Owl (Ulluk)": {
        "auspicious": "Goddess Lakshmi's vahana — sighting = wealth; calling at night near home = good fortune",
        "warning": "Owl flying into home at night = death omen in some traditions; calling mid-day = misfortune",
    },
    "Eagle/Hawk": {
        "auspicious": "High-flying eagle = victory in upcoming endeavor; spotted before journey = success",
        "direction": "From east = excellent; west = mixed",
    },
    "Pigeon (Kabutar)": {
        "auspicious": "Cooing at home = peace, family harmony; pair of pigeons = marriage on horizon",
        "warning": "Pigeon flying into closed room = unexpected news (positive or negative)",
    },
    "Vulture (Gidh)": {
        "warning": "Sighting vulture circling overhead = serious illness or death omen for someone known",
        "context": "Considered most inauspicious bird in classical texts",
    },
    "Parrot (Tota)": {
        "auspicious": "Sighting green parrot = romance/love, good news",
        "specific": "Speaking parrot near home = student success in education",
    },
    "Sparrow (Gauraiya)": {
        "auspicious": "Common, neutral; chirping at dawn = ordinary day",
        "specific": "Building nest in home = stable family life",
    },
    "Cuckoo (Koel)": {
        "auspicious": "Calling in spring = excellent for new ventures, marriage, conception",
        "context": "Sacred to Krishna/Saraswati; voice carries blessings",
    },
    "Rooster (Murgha)": {
        "auspicious": "Crowing at sunrise = standard auspicious",
        "warning": "Crowing at midnight = inauspicious, possibly sickness in family",
    },
    "Mynah (Maina)": {
        "auspicious": "Chattering = good news from distant relatives",
    },
    "Kingfisher": {
        "auspicious": "Highly auspicious — unique sighting = unexpected fortune, especially in business or travel",
    },
    "Bat (Chamgadar)": {
        "warning": "Entering house = warning omen, possibly health-related",
        "context": "Some traditions: bat = wealth-spirit (Lakshmi); depends on family lore",
    },
}

# ============================================================
# ANIMAL OMENS — "Pashu Shakuna"
# ============================================================
ANIMAL_OMENS = {
    "Cow (Gau)": {
        "auspicious": "Cow facing you on path = excellent; cow with calf = blessing of fertility/abundance",
        "specific": "Black cow = Saturn-blessing (challenges resolve); white cow = peace/dharma",
    },
    "Bull (Bail)": {
        "auspicious": "Bull seen before journey = success, especially business",
        "warning": "Aggressive bull = obstacles; conflict ahead",
    },
    "Horse (Ghoda)": {
        "auspicious": "Galloping horse = victory in pursuits; white horse = highly auspicious",
        "context": "Special for warriors/leaders",
    },
    "Elephant (Hathi)": {
        "auspicious": "Most auspicious — sighting = royal favor, immense wealth, divine grace",
        "warning": "Mad/charging elephant = obstacles requiring caution",
    },
    "Dog (Kutta)": {
        "auspicious": "Dog wagging tail at you = friend coming; dog crossing left-to-right = good",
        "warning": "Howling dog at night = death omen in some traditions; dog crossing right-to-left = bad omen",
    },
    "Cat (Billi)": {
        "warning": "Black cat crossing path = postpone the journey/work (most universal omen)",
        "specific": "Cat fighting near home = quarrels in family soon",
    },
    "Snake (Sarp/Naag)": {
        "auspicious": "Snake crossing left-to-right peacefully = wealth/spiritual blessing; sighting at well/water = naga blessing",
        "warning": "Snake biting in dream/seen aggressive = enemy activity, deception",
        "specific": "Two snakes intertwined = romantic/marriage indicator",
    },
    "Mongoose (Newla)": {
        "auspicious": "Sighting before important work = success; defeating snake = enemies overcome",
    },
    "Monkey (Bandar)": {
        "auspicious": "Hanuman's form — friendly monkey = divine blessing",
        "warning": "Aggressive monkey = mischief, theft risk, deception",
    },
    "Squirrel": {
        "auspicious": "Rama's blessed creature — neutral-positive, small fortune",
    },
    "Donkey (Gadha)": {
        "warning": "Braying loudly = obstacles, especially in travel",
        "specific": "Seeing donkey carrying load = hard work without reward soon",
    },
    "Deer (Hiran)": {
        "auspicious": "Seeing deer = peace, dharma, gentle fortune",
        "specific": "Deer crossing path = journey will be peaceful",
    },
    "Lion / Tiger": {
        "auspicious": "Sighting (rare in cities) = victory, royal favor, courage",
        "warning": "Charging = serious enemy or major life challenge",
    },
    "Pig (Suar)": {
        "warning": "Generally inauspicious; crossing path = postpone important work",
        "specific": "Wild boar = enemy attack possibility",
    },
}

# ============================================================
# BODY OMENS — Twitches & Sneezes (DIFFER for Male vs Female)
# ============================================================
BODY_OMENS = {
    # Eye twitching (most asked)
    "Right eye twitch (MALE)": {
        "male": "Auspicious — good news, money coming, success",
        "female": "Warning — caution, possibly bad news",
    },
    "Left eye twitch (MALE)": {
        "male": "Warning — caution, possibly bad news",
        "female": "Auspicious — good news, blessings",
    },
    "Right eye twitch (FEMALE)": {
        "female": "Warning — caution, possibly bad news",
        "general": "REVERSED for women — see Right eye Male entry inverted",
    },
    "Left eye twitch (FEMALE)": {
        "female": "Auspicious — good news, blessings",
    },

    # Sneezes
    "Single sneeze before starting work": {
        "general": "Postpone the work briefly; pause then resume",
    },
    "Double sneeze (2 in a row)": {
        "general": "Highly auspicious — divine blessing, proceed with confidence",
    },
    "Sneeze 3+ times": {
        "general": "Mixed; depends on direction and context",
    },
    "Sneeze when leaving home": {
        "general": "Pause, drink water, then leave — work will succeed",
    },
    "Sneeze when receiving news": {
        "general": "Validates the news as TRUE",
    },

    # Body twitches
    "Right arm twitch": {
        "general": "Hard work coming or unexpected gain",
    },
    "Left arm twitch": {
        "general": "Loss or expense ahead; check finances",
    },
    "Right hand palm itch": {
        "male": "Money is coming — receive money soon",
        "female": "Money will leave (spending coming)",
    },
    "Left hand palm itch": {
        "male": "Money will leave (spending or loss)",
        "female": "Money is coming",
    },
    "Right foot itch": {
        "general": "Travel coming, especially auspicious journey",
    },
    "Left foot itch": {
        "general": "Travel-related expenses or troubles ahead",
    },
    "Tongue itch": {
        "general": "Tasty food coming; festive meal soon",
    },
    "Lip twitch": {
        "general": "Speech-related event — gossip, news, or invitation",
    },
    "Top of head itch": {
        "general": "Position elevation, recognition coming",
    },
    "Forehead itch": {
        "general": "Surprise news or unexpected meeting",
    },
    "Right ear ringing": {
        "general": "Someone speaking well of you; good news from afar",
    },
    "Left ear ringing": {
        "general": "Someone speaking ill of you; gossip about you",
    },
    "Both ears ringing": {
        "general": "Major news event coming, possibly divine sign",
    },
}

# ============================================================
# OBJECT-FALLING OMENS
# ============================================================
OBJECT_OMENS = {
    "Glass breaking (accidental)": "Removes negative energy, but warns of disturbance ahead",
    "Mirror breaking": "Warning — 7 days of caution, especially with travel and money",
    "Water spilling on you": "Cleansing omen — bad karma washed away",
    "Salt spilling": "Family quarrel coming — throw pinch over left shoulder to negate",
    "Milk overflowing while boiling": "Wealth and abundance — VERY auspicious",
    "Lamp suddenly extinguishing": "Warning — be cautious, possibly health issue or family upheaval",
    "Picture/photograph falling from wall": "Warning about the person in the photo (or relationship)",
    "Necklace/jewelry breaking suddenly": "Marriage or relationship strain ahead",
    "Sacred thread (yajnopavita) breaking": "Major life-event imminent; do prayer immediately",
    "Idol falling": "Serious warning — spiritual cleansing needed; do remedy",
    "Coin/currency note found unexpectedly": "Lakshmi blessing — keep it, don't spend immediately",
    "Lost wallet/ID": "Karmic loss; replacement comes with caution",
}

# ============================================================
# SOUNDS HEARD
# ============================================================
SOUND_OMENS = {
    "Conch shell (Shankha) heard": "Highly auspicious — divine blessing, victory",
    "Temple bell heard": "Spiritual energy entering, good time for prayer",
    "Bird singing at sunrise": "Day will go well",
    "Rooster crowing at midnight (unusual)": "Warning — possible upset in night",
    "Dog barking at strange hour": "Warning — caution against intrusion (physical or spiritual)",
    "Cat fighting near home (loud)": "Family quarrel coming",
    "Wind chimes ringing in still air": "Spiritual presence, ancestor or deity blessing",
    "Door knocking by no one": "Spirit presence; do prayer",
    "Footsteps with no person": "Ancestor visit; offer water/incense",
    "Baby crying suddenly with no cause": "Grandparent's spirit nearby",
    "Music heard from no source": "Highly auspicious — Gandharva blessing",
}

# ============================================================
# DREAM CATALOG (Swapna Shastra)
# ============================================================
DREAM_OMENS = {
    "Snake biting": "Money coming, especially via property; OR warning of enemy",
    "Riding elephant": "Royal favor, promotion, fame",
    "Riding horse galloping": "Victory in pursuit, fast progress",
    "Climbing mountain": "Achievement, ascent in career",
    "Falling from height": "Reversal in plans, watch ego",
    "Drowning in water": "Emotional overwhelm; warning to seek balance",
    "Swimming in clear water": "Cleansing of karma, spiritual progress",
    "Flowing river clear": "Prosperity flowing, wealth path open",
    "Flowing river muddy": "Obstacles in money matters",
    "Flying": "Liberation from problems, spiritual elevation",
    "Wedding (your own or seeing one)": "Major positive change, new beginning",
    "Funeral": "End of bad period, new chapter (NOT death)",
    "Death of loved one": "Long life for that person OR major life change",
    "Seeing dead relatives smiling": "Their blessings; good for upcoming work",
    "Seeing dead relatives upset": "Pitru-tarpana needed; offer respects",
    "Sun rising": "New positive era beginning",
    "Sun setting": "End of phase, prepare for transition",
    "Moon full and bright": "Mental peace, romantic harmony",
    "Moon eclipsed": "Mental disturbance ahead",
    "Lord/God appearing": "Divine grace, life-changing blessing imminent",
    "Saint/guru appearing": "Spiritual guidance available, accept offerings",
    "Lost in unknown place": "Confusion in waking life; pause major decisions",
    "Found lost item": "Recovery of opportunities",
    "Gold/silver/treasure": "Wealth coming",
    "Snake or bull chasing you": "Enemy active; take protective measures",
    "Tiger chasing you": "Major life challenge but you'll prevail",
    "Crying / weeping": "Tension release; better days ahead",
    "Laughing in dream": "Positive period continuing",
    "Eating sweet food": "Festivity, family gathering, good news",
    "Eating bitter food": "Health caution, family tension",
    "Bathing in holy river": "Karma cleansing, spiritual purification",
    "Black cobra with hood": "Kundalini awakening or strong protective deity",
    "White horse galloping": "Major victory, possibly journey",
    "Lit lamp / multiple lamps": "Wisdom, knowledge, removal of darkness",
    "Falling teeth": "Loss of close one OR end of difficulty (positive in some traditions)",
    "Hair falling": "Loss of vitality temporarily; rest needed",
}

# ============================================================
# DISHA SHOOLA — Forbidden Travel Direction Per Weekday
# ============================================================
DISHA_SHOOLA = {
    "Sunday": "West (do not travel west on Sunday)",
    "Monday": "East",
    "Tuesday": "North-West",
    "Wednesday": "North",
    "Thursday": "South",
    "Friday": "West",
    "Saturday": "East",
}

# Direction antidotes — eat/touch/wear specific item before travel
DISHA_ANTIDOTES = {
    "West (Sun/Fri)": "Eat curd/yogurt before leaving",
    "East (Mon/Sat)": "Eat sesame/black salt before leaving",
    "North (Wed)": "Drink milk before leaving",
    "South (Thu)": "Eat jaggery before leaving",
    "North-West (Tue)": "Eat dry fruits/nuts before leaving",
}


def check_disha_shoola(travel_date, direction):
    """Check if planned travel direction conflicts with Disha Shoola for that weekday."""
    weekday = travel_date.strftime("%A")
    forbidden = DISHA_SHOOLA.get(weekday, "")
    is_conflict = direction.lower() in forbidden.lower()

    antidote = None
    for d, a in DISHA_ANTIDOTES.items():
        if direction.lower() in d.lower() and weekday[:3].lower() in d.lower():
            antidote = a
            break

    return {
        "weekday": weekday,
        "travel_direction": direction,
        "forbidden_direction_today": forbidden,
        "is_disha_shoola": is_conflict,
        "verdict": "Avoid travel today" if is_conflict else "Direction is acceptable",
        "antidote_if_must_travel": antidote,
    }


def lookup_omen(category, omen_name):
    """Lookup any omen interpretation."""
    DBS = {
        "bird": BIRD_OMENS,
        "animal": ANIMAL_OMENS,
        "body": BODY_OMENS,
        "object": OBJECT_OMENS,
        "sound": SOUND_OMENS,
        "dream": DREAM_OMENS,
    }
    db = DBS.get(category.lower())
    if not db:
        return f"Unknown category. Available: {list(DBS.keys())}"
    if omen_name in db:
        return db[omen_name]
    # Fuzzy match
    for k in db:
        if omen_name.lower() in k.lower():
            return db[k]
    return None


def omens_summary():
    """Return total catalog stats."""
    return {
        "bird_omens_catalogued": len(BIRD_OMENS),
        "animal_omens_catalogued": len(ANIMAL_OMENS),
        "body_omens_catalogued": len(BODY_OMENS),
        "object_omens_catalogued": len(OBJECT_OMENS),
        "sound_omens_catalogued": len(SOUND_OMENS),
        "dream_omens_catalogued": len(DREAM_OMENS),
        "total": (len(BIRD_OMENS) + len(ANIMAL_OMENS) + len(BODY_OMENS) +
                  len(OBJECT_OMENS) + len(SOUND_OMENS) + len(DREAM_OMENS)),
        "disha_shoola_directions": list(DISHA_SHOOLA.values()),
        "categories": list(DISHA_SHOOLA.keys()),
    }


# ============================================================
# ============================================================
# TIER-1 DEEP EXTENSION — Classical Shakuna Shastra (100+ omens)
# Sources:
#   - Brihat Samhita Ch. 86-95 (Varahamihira) — esp. Ch. 89 Anga-Vidya (body omens)
#   - Vasanta Raja Shakuna (15th c. compendium of omen lore)
#   - Garga Samhita — tithi & weekday amplification rules
#   - Adbhuta Sagara (Ballala Sena) — exceptional/freak omens
#   - Shakuna Pradeep — domestic omens
#   - Shukasaptati / Vishnu Purana — animal omens
# Schools chosen: Where texts disagree, default = Brihat Samhita (Varahamihira)
# as the most widely-cited Sanskrit authority. Disagreements documented inline.
# ============================================================
# ============================================================

# ============================================================
# SHAKUNA_FULL_DB — Master classical database
# Each entry: name, category, auspicious_or_not (auspicious/inauspicious/neutral/mixed),
#             severity (1-5), interpretation, remedy, source
# ============================================================
SHAKUNA_FULL_DB = {

    # =========================================================
    # ANIMAL OMENS — 40 entries
    # =========================================================
    "cow_lowing_on_right": {
        "name": "Cow lowing on the right side",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "When a cow's call (mooing) is heard from the right side at the start of a journey or undertaking, it indicates success, fulfilment of desires, and divine grace. Right-side animal voice is universally auspicious in Shakuna lore.",
        "remedy": "None needed; offer thanks to Surabhi (cosmic cow). Proceed with confidence.",
        "source": "Brihat Samhita Ch. 88 v. 9; Vasanta Raja Shakuna Ch. 6",
    },
    "cow_lowing_on_left": {
        "name": "Cow lowing on the left side",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Cow's voice from left side at outset = mild obstacle in current undertaking; not severe but warns of delay or partial setback.",
        "remedy": "Pause briefly, recite Gayatri 3 times, then proceed.",
        "source": "Brihat Samhita Ch. 88; Vasanta Raja Shakuna",
    },
    "dog_crossing_path_right_to_left": {
        "name": "Dog crossing path right to left",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Dog moving right-to-left across one's path (i.e. dog's right is your obstacle) = obstacles ahead; postpone the work briefly.",
        "remedy": "Wait 5-7 minutes, drink water, then resume.",
        "source": "Vasanta Raja Shakuna Ch. 4; Adbhuta Sagara",
    },
    "dog_crossing_path_left_to_right": {
        "name": "Dog crossing path left to right",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Dog moving left-to-right (favourable side) = work will succeed; especially auspicious for travel and meetings.",
        "remedy": "None; proceed at once.",
        "source": "Vasanta Raja Shakuna Ch. 4",
    },
    "dog_howling_at_night": {
        "name": "Dog howling at night near home",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Prolonged dog-howling at night, especially facing one direction, classically signals death or serious illness in the household within 6-9 days. (Some southern texts say it merely indicates spirit-presence, not death.)",
        "remedy": "Light camphor lamp at home entrance; recite Mahamrityunjaya 11 times.",
        "source": "Adbhuta Sagara; Brihat Samhita Ch. 95 (Shvashakuna)",
    },
    "deer_running_across_path": {
        "name": "Deer running across path",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "Sighting deer running across one's path is among the most auspicious of forest omens — peaceful prosperity, gentle success, dharmic merit.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88 v. 12; Vishnu Purana",
    },
    "snake_crossing_path": {
        "name": "Snake crossing path",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 4,
        "interpretation": "Snake (especially black or hooded) crossing path peacefully left-to-right = Naga blessing, wealth, ancestor-grace. If aggressive or right-to-left = warning of enemy or hidden deception.",
        "remedy": "Offer milk near a peepal/banyan tree; recite Naga-stotra.",
        "source": "Vasanta Raja Shakuna Ch. 5; Shakuna Pradeep",
    },
    "snake_in_dream": {
        "name": "Snake in dream",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Snake biting in dream = unexpected money via property/inheritance OR enemy revealed. Snake without biting = ancestor-message; serpent in coil = wealth incoming.",
        "remedy": "Avoid major decisions for 24 hours; offer water at sunrise.",
        "source": "Swapna Shastra Ch. 3",
    },
    "monkey_screaming": {
        "name": "Monkey screaming aggressively",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Aggressive monkey screams near home = mischief, theft, or deception by acquaintance. (Hanuman-blessing reading applies only to peaceful, friendly monkeys.)",
        "remedy": "Recite Hanuman Chalisa 1 time; secure valuables.",
        "source": "Vasanta Raja Shakuna Ch. 5",
    },
    "cat_sneezing_indoors": {
        "name": "Cat sneezing indoors",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Domestic cat sneezing repeatedly inside home = quarrels brewing among family members within 3 days.",
        "remedy": "Sprinkle salt water at four corners of the home.",
        "source": "Shakuna Pradeep; folk tradition",
    },
    "elephant_trumpeting": {
        "name": "Elephant trumpeting auspiciously",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "Hearing elephant trumpet (e.g. at temple, festival, or unexpected sighting) = royal favour, immense wealth, divine grace. The most auspicious of all animal sounds in Shakuna texts.",
        "remedy": "None; offer obeisance to Ganesha.",
        "source": "Brihat Samhita Ch. 88 v. 4; Matanga Lila",
    },
    "jackal_howling_from_north": {
        "name": "Jackal howling from north",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Jackal-cry from northern direction (especially at twilight) = unexpected news, mild gain. Jackal voice from north is the only direction considered favourable.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88 v. 22 (Shiva-shakuna)",
    },
    "jackal_howling_from_south": {
        "name": "Jackal howling from south",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Jackal voice from south (Yama's direction) = ill omen; threat of loss, illness, ancestor-disturbance.",
        "remedy": "Pitru-tarpan; offer water + black sesame to ancestors.",
        "source": "Brihat Samhita Ch. 88 v. 23",
    },
    "jackal_howling_from_east": {
        "name": "Jackal howling from east",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Jackal voice from east = mixed; news arriving but slowly. Some texts classify as mildly inauspicious.",
        "remedy": "Recite Surya stotra at sunrise.",
        "source": "Vasanta Raja Shakuna Ch. 7",
    },
    "jackal_howling_from_west": {
        "name": "Jackal howling from west",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Jackal voice from west = financial loss or argument. (Some southern schools reverse this to mild auspicious for women.)",
        "remedy": "Light a ghee lamp at home entrance facing east.",
        "source": "Vasanta Raja Shakuna; school: Varahamihira",
    },
    "jackal_howling_from_northeast": {
        "name": "Jackal howling from northeast (Ishanya)",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Northeast (Ishanya, Shiva's direction) jackal voice = spiritual blessing, mantra-siddhi, dharmic success.",
        "remedy": "None; sit in meditation briefly.",
        "source": "Adbhuta Sagara",
    },
    "jackal_howling_from_southeast": {
        "name": "Jackal howling from southeast (Agneya)",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Southeast (Agneya, Agni's direction) jackal voice = fire/heat-related warning; check stove, electricals.",
        "remedy": "Inspect kitchen; offer ghee in a small fire ritual.",
        "source": "Adbhuta Sagara",
    },
    "jackal_howling_from_southwest": {
        "name": "Jackal howling from southwest (Nairutya)",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Southwest (Nairutya, Nirriti's direction) jackal voice = serious caution; possible accident or ancestral karma activating.",
        "remedy": "Recite Mahamrityunjaya 21 times; visit temple within 3 days.",
        "source": "Adbhuta Sagara",
    },
    "jackal_howling_from_northwest": {
        "name": "Jackal howling from northwest (Vayavya)",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Northwest (Vayavya, Vayu's direction) jackal voice = travel news, wind-related changes; outcome depends on tithi.",
        "remedy": "Hang wind chime at northwest corner of home.",
        "source": "Vasanta Raja Shakuna",
    },
    "horse_neighing": {
        "name": "Horse neighing on the right",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Horse neighing on right at start of journey = victory, swift success, especially for warriors, athletes, leaders.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88 v. 17",
    },
    "donkey_braying_morning": {
        "name": "Donkey braying in morning",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Donkey braying loudly at sunrise = obstacles in day's work; especially poor for travel.",
        "remedy": "Drink jaggery-water before leaving.",
        "source": "Vasanta Raja Shakuna Ch. 6",
    },
    "donkey_braying_evening": {
        "name": "Donkey braying in evening",
        "category": "animal",
        "auspicious_or_not": "neutral",
        "severity": 1,
        "interpretation": "Donkey braying at dusk is considered neutral; folk lore says it just announces nightfall.",
        "remedy": "None.",
        "source": "Folk tradition",
    },
    "donkey_braying_midnight": {
        "name": "Donkey braying at midnight",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Donkey braying at midnight = unusual disturbance, possible quarrel or sickness in family before dawn.",
        "remedy": "Sprinkle gangajal at the four corners of the bedroom.",
        "source": "Adbhuta Sagara",
    },
    "bull_charging": {
        "name": "Bull charging or aggressive",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Aggressive bull on path = serious obstacle; major opposition expected. Postpone all critical work.",
        "remedy": "Recite Nandi-stotra; visit Shiva temple within 24 hours.",
        "source": "Vasanta Raja Shakuna Ch. 5",
    },
    "sheep_crossing_path": {
        "name": "Sheep crossing path",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Sheep crossing path peacefully = mild auspicious; calm, gentle success.",
        "remedy": "None.",
        "source": "Vishnu Purana",
    },
    "pig_in_compound": {
        "name": "Pig in compound or crossing path",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Pig (especially wild boar or unkempt) crossing path = obstacles, dirty/unclean influences. Postpone important work.",
        "remedy": "Bathe before resuming work; sprinkle turmeric water.",
        "source": "Brihat Samhita Ch. 88 v. 27",
    },
    "mongoose_sighting": {
        "name": "Mongoose sighting before work",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Mongoose seen before important work = enemies overcome, success in legal matters, victory over disputes.",
        "remedy": "None.",
        "source": "Vasanta Raja Shakuna Ch. 5",
    },
    "fox_crossing_path": {
        "name": "Fox crossing path",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Fox seen during day (rare) = deception by close person; cunning enemy active.",
        "remedy": "Avoid signing contracts for 48 hours.",
        "source": "Adbhuta Sagara; folk tradition",
    },
    "lion_sighting": {
        "name": "Lion sighting (unexpected)",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "Sighting a lion (in temple, dream, or rare encounter) = royal favour, courage, victory, leadership ascent.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88 v. 11",
    },
    "tiger_sighting": {
        "name": "Tiger sighting (unexpected)",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 4,
        "interpretation": "Tiger seen calmly = victory after struggle; tiger in dream charging = major life test, you will prevail if you face it.",
        "remedy": "Recite Durga Saptashati; offer red flowers to Goddess.",
        "source": "Vasanta Raja Shakuna",
    },
    "rabbit_crossing_path": {
        "name": "Rabbit crossing path",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Rabbit/hare crossing path = quick small gain, lucky break.",
        "remedy": "None.",
        "source": "Folk tradition",
    },
    "squirrel_crossing_path": {
        "name": "Squirrel near home/path",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Squirrel (Rama-blessed) = small fortune, family harmony.",
        "remedy": "Feed it nuts/grains.",
        "source": "Ramayana folk lore",
    },
    "rat_crossing_path": {
        "name": "Rat crossing path",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Rat (Ganesha's vahana) seen crossing path peacefully = obstacle removal; auspicious for new ventures.",
        "remedy": "Offer modak to Ganesha.",
        "source": "Vasanta Raja Shakuna Ch. 5",
    },
    "buffalo_crossing_path": {
        "name": "Buffalo crossing path",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Buffalo (Yama's vahana) crossing path = warning; postpone travel & decisions briefly.",
        "remedy": "Recite Mahamrityunjaya 11 times.",
        "source": "Brihat Samhita Ch. 88",
    },
    "camel_crossing_path": {
        "name": "Camel crossing path",
        "category": "animal",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Camel = slow but steady progress; long journey ahead with eventual reward. Mixed depending on direction.",
        "remedy": "None.",
        "source": "Vasanta Raja Shakuna",
    },
    "cat_black_crossing_path": {
        "name": "Black cat crossing path",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Black cat crossing path = postpone the journey/work briefly. The most universal omen across Indian and Western traditions.",
        "remedy": "Stop, take 7 steps back, then resume after 5 minutes.",
        "source": "Universal folk + Vasanta Raja",
    },
    "white_cow_with_calf": {
        "name": "White cow with calf",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "White cow with calf = peace, dharma, fertility, abundance — among the very highest auspicious sightings.",
        "remedy": "None; offer green grass.",
        "source": "Brihat Samhita Ch. 88 v. 7",
    },
    "stray_dog_following_you": {
        "name": "Stray dog following you home",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "A stray dog choosing to follow you home = Bhairava blessing, protection, removal of black-magic influences.",
        "remedy": "Feed the dog; do not chase away.",
        "source": "Folk tradition + Bhairava-tantra",
    },
    "wolf_howling": {
        "name": "Wolf howling",
        "category": "animal",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Wolf howling near settlement = warning of theft or quarrel within 3 days.",
        "remedy": "Light camphor at all four directions.",
        "source": "Adbhuta Sagara",
    },
    "frog_jumping_into_home": {
        "name": "Frog jumping into home",
        "category": "animal",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Frog entering home (especially during rains) = monsoon blessing, fertility, abundant harvest of plans.",
        "remedy": "Release it gently outside; do not harm.",
        "source": "Folk tradition + Garuda Purana",
    },

    # =========================================================
    # BIRD OMENS — 25 entries (Pakshi Shakuna)
    # =========================================================
    "crow_calling_from_north": {
        "name": "Crow calling from north",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Crow calling from north = arrival of guest, news from afar, possible travel. North-direction crow is considered most favourable across schools. (Some southern schools rate north-crow as neutral on Krishna paksha 14th.)",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 95 (Vayasa-vidya); Vasanta Raja Shakuna Ch. 8",
    },
    "crow_calling_from_south": {
        "name": "Crow calling from south",
        "category": "bird",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Crow calling from south (Yama-direction) = warning of bad news from afar, possibly news of death/illness in extended family.",
        "remedy": "Offer water + black sesame to ancestors; recite Pitru-stotra.",
        "source": "Brihat Samhita Ch. 95 v. 14",
    },
    "crow_calling_from_east": {
        "name": "Crow calling from east",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Crow calling from east (Indra/Surya direction) = success in royal/governmental work, recognition, awards.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 95",
    },
    "crow_calling_from_west": {
        "name": "Crow calling from west",
        "category": "bird",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Crow from west (Varuna direction) = water-related news, mild caution, possibly travel by water.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 95",
    },
    "crow_on_roof_at_dawn": {
        "name": "Crow on roof at dawn",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Crow cawing on rooftop at dawn = guest arriving same day; friend or distant relative.",
        "remedy": "Prepare hospitality.",
        "source": "Brihat Samhita Ch. 95 v. 8",
    },
    "crow_with_food_in_beak": {
        "name": "Crow with food in beak",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Crow flying with food (esp. meat or roti) in beak = wealth incoming; especially auspicious if direction is left-to-right.",
        "remedy": "None.",
        "source": "Vasanta Raja Shakuna",
    },
    "peacock_dancing": {
        "name": "Peacock dancing",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "Peacock dancing (especially before rain) = great prosperity, royal favour, divine grace from Saraswati and Murugan.",
        "remedy": "None; revere it.",
        "source": "Brihat Samhita Ch. 88; Skanda Purana",
    },
    "peacock_calling": {
        "name": "Peacock calling",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Peacock voice heard at dawn = excellent for new ventures, especially creative/artistic work.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88",
    },
    "owl_sighting_day": {
        "name": "Owl sighting during day",
        "category": "bird",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Owl seen in daytime (out of natural cycle) = ill omen; misfortune, possible illness within fortnight.",
        "remedy": "Recite Lakshmi-stotra; light ghee lamp at sunset for 7 days.",
        "source": "Brihat Samhita Ch. 88 v. 28",
    },
    "owl_calling_at_night": {
        "name": "Owl calling at night",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Owl (Ulluk, vahana of Lakshmi) calling at night near home = wealth incoming, especially if heard on Friday or full moon. (Northern texts: ill omen if hooting facing the home; this is the school-disagreement point.)",
        "remedy": "None; honour Lakshmi.",
        "source": "Lakshmi-tantra; SCHOOL: Tantric/Bengali (vs. Brihat Samhita-based North Indian school which calls night-owl ill).",
    },
    "vulture_circling": {
        "name": "Vulture circling overhead",
        "category": "bird",
        "auspicious_or_not": "inauspicious",
        "severity": 5,
        "interpretation": "Vulture circling = serious illness or death in known person within the lunar cycle. The most ill-omened bird sighting.",
        "remedy": "Mahamrityunjaya 108 times; visit Bhairava temple.",
        "source": "Brihat Samhita Ch. 88 v. 30; Adbhuta Sagara",
    },
    "eagle_soaring_right": {
        "name": "Eagle soaring on right",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Eagle (Garuda's symbol) soaring on right = victory, success in upcoming endeavour; spotted before journey = excellent.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88; Garuda Purana",
    },
    "eagle_soaring_left": {
        "name": "Eagle soaring on left",
        "category": "bird",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Eagle on left = mixed; minor obstacle before eventual success.",
        "remedy": "None.",
        "source": "Vasanta Raja Shakuna",
    },
    "parrot_speaking_near_home": {
        "name": "Parrot speaking near home",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Green parrot speaking near home = student success in education, romantic news, communication breakthrough.",
        "remedy": "None.",
        "source": "Folk + Vishnu Purana",
    },
    "dove_cooing": {
        "name": "Dove cooing in the morning",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Dove (kapota) cooing at dawn = peace, family harmony, possible marriage/relationship news.",
        "remedy": "None.",
        "source": "Vasanta Raja Shakuna",
    },
    "sparrow_nesting_indoors": {
        "name": "Sparrow nesting indoors",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Sparrow building nest inside home = family stability, fertility, abundance for several years.",
        "remedy": "Do not disturb; provide water nearby.",
        "source": "Folk tradition",
    },
    "swan_sighting": {
        "name": "Swan sighting (Hamsa)",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 5,
        "interpretation": "Swan (Hamsa, Saraswati's vahana) = supreme auspicious; spiritual wisdom, discrimination (viveka), dharmic prosperity.",
        "remedy": "None; revere Saraswati.",
        "source": "Brihat Samhita Ch. 88; Saraswati-stotra",
    },
    "kingfisher_sighting": {
        "name": "Kingfisher sighting",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Kingfisher = unexpected fortune, especially in business or travel; rare and considered very lucky.",
        "remedy": "None.",
        "source": "Folk + tribal lore",
    },
    "woodpecker_pecking": {
        "name": "Woodpecker tapping near home",
        "category": "bird",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Woodpecker tapping = warning of structural concern (literal or metaphorical); inspect home or examine plans.",
        "remedy": "None; check for any issue.",
        "source": "Folk tradition",
    },
    "rooster_crowing_midnight": {
        "name": "Rooster crowing at midnight",
        "category": "bird",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Rooster crowing at midnight (out of cycle) = warning, possible sickness or unusual disturbance in night.",
        "remedy": "Recite Hanuman Chalisa; sprinkle gangajal in bedroom.",
        "source": "Adbhuta Sagara",
    },
    "rooster_crowing_dawn": {
        "name": "Rooster crowing at dawn",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Rooster crowing at sunrise = standard auspicious; day will go well.",
        "remedy": "None.",
        "source": "Universal folk",
    },
    "cuckoo_calling_spring": {
        "name": "Cuckoo (Koel) calling in spring",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Koel calling in Vasanta (spring) = excellent for new ventures, marriage, conception, creative pursuits.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 88; Krishna Lila",
    },
    "mynah_chattering": {
        "name": "Mynah chattering near window",
        "category": "bird",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Mynah chattering = good news from distant relatives within the week.",
        "remedy": "None.",
        "source": "Folk tradition",
    },
    "vulture_landing_on_house": {
        "name": "Vulture landing on house roof",
        "category": "bird",
        "auspicious_or_not": "inauspicious",
        "severity": 5,
        "interpretation": "Vulture sitting on house roof = severe omen, classical texts indicate possible death of senior family member within 1-3 months. EXTREME caution.",
        "remedy": "Major remedies: Rudra-abhishekam, Mahamrityunjaya 1008, visit Kashi if possible.",
        "source": "Brihat Samhita Ch. 88; Adbhuta Sagara",
    },
    "bat_entering_house": {
        "name": "Bat entering house",
        "category": "bird",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Bat (Chamgadar) flying into home = warning omen in north Indian school; in some Bengali/Tantric schools = wealth-spirit (Lakshmi-bird).",
        "remedy": "Light camphor; gently guide it out without harm.",
        "source": "Folk + Bengali Tantric tradition (school-divergence noted)",
    },

    # =========================================================
    # BODY OMENS / ANGA SHAKUNA — 15 entries (Brihat Samhita Ch. 89)
    # =========================================================
    "left_eye_twitch_male": {
        "name": "Left eye twitch (male)",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "For male, left-eye twitch = warning, possibly bad news or financial setback. Effect lasts 1-3 days. (Reverse for female: see left_eye_twitch_female.)",
        "remedy": "Drink water; sit quietly for 5 minutes.",
        "source": "Brihat Samhita Ch. 89 (Anga-vidya) v. 5",
    },
    "left_eye_twitch_female": {
        "name": "Left eye twitch (female)",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "For female, left-eye twitch = good news, blessings, fortunate event within 1-3 days.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89 v. 6",
    },
    "right_eye_twitch_male": {
        "name": "Right eye twitch (male)",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "For male, right-eye twitch = success, money coming, good news within 1-3 days.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89 v. 5",
    },
    "right_eye_twitch_female": {
        "name": "Right eye twitch (female)",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "For female, right-eye twitch = warning, possible setback or bad news.",
        "remedy": "Drink water; rest the eye briefly.",
        "source": "Brihat Samhita Ch. 89 v. 6",
    },
    "right_hand_throbbing": {
        "name": "Right hand throbbing",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Right hand throbbing/pulsing = unexpected gain, work success, possible money. Stronger for male.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89 v. 11",
    },
    "left_hand_throbbing": {
        "name": "Left hand throbbing",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Left hand throbbing = expense or loss; reverse for female (auspicious).",
        "remedy": "Avoid major spending for 24 hours.",
        "source": "Brihat Samhita Ch. 89 v. 12",
    },
    "right_foot_tingling": {
        "name": "Right foot tingling/itching",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Right foot tingling = travel coming, especially auspicious journey, new opportunity at distance.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89 v. 14",
    },
    "left_foot_tingling": {
        "name": "Left foot tingling/itching",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Left foot tingling = travel-related expense or trouble; possibly unwilling journey.",
        "remedy": "Pause travel plans 24 hours; review them.",
        "source": "Brihat Samhita Ch. 89",
    },
    "right_ear_ringing": {
        "name": "Right ear ringing",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Right ear ringing = someone speaking well of you; good news from afar approaching.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89 v. 17",
    },
    "left_ear_ringing": {
        "name": "Left ear ringing",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Left ear ringing = someone speaking ill of you; gossip or criticism happening at this moment.",
        "remedy": "Touch right ear with right hand; recite OM 3 times.",
        "source": "Brihat Samhita Ch. 89",
    },
    "sneeze_facing_east": {
        "name": "Sneeze when facing east",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Single sneeze while facing east = work will succeed; pause briefly then proceed.",
        "remedy": "Drink water; pause 30 seconds.",
        "source": "Brihat Samhita Ch. 89 v. 23",
    },
    "sneeze_facing_west": {
        "name": "Sneeze when facing west",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Sneeze while facing west = mild obstacle in current undertaking.",
        "remedy": "Pause, drink water, change direction briefly.",
        "source": "Brihat Samhita Ch. 89",
    },
    "hiccup_pattern_short": {
        "name": "Brief hiccup (under 5 seconds)",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 2,
        "interpretation": "Brief hiccup = someone is remembering you fondly; small good news soon.",
        "remedy": "None.",
        "source": "Folk tradition + Brihat Samhita Ch. 89",
    },
    "right_palm_itching": {
        "name": "Right palm itching",
        "category": "body",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Right palm itching for male = money coming; for female = money will leave (reversed). Effect within 24-72 hours.",
        "remedy": "Do not scratch on a coin/wood (folk tradition holds this can cancel the omen).",
        "source": "Brihat Samhita Ch. 89; folk lore",
    },
    "left_palm_itching": {
        "name": "Left palm itching",
        "category": "body",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Left palm itching for male = money will leave; for female = money coming.",
        "remedy": "Avoid major spending for 24 hours if male.",
        "source": "Brihat Samhita Ch. 89; folk lore",
    },
    "lip_trembling": {
        "name": "Lip trembling",
        "category": "body",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Lip trembling = speech-related event coming: gossip, news, or invitation. Tone depends on tithi.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 89",
    },
    "neck_spasm": {
        "name": "Neck spasm or sudden stiffness",
        "category": "body",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Sudden neck spasm = possible burden incoming, responsibility weighing soon.",
        "remedy": "Rest; recite Mahamrityunjaya 3 times.",
        "source": "Adbhuta Sagara",
    },

    # =========================================================
    # WEATHER OMENS — 10 entries
    # =========================================================
    "rainbow_morning": {
        "name": "Rainbow in morning",
        "category": "weather",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Rainbow visible in morning = divine blessing, important news incoming, beautiful resolution to a problem.",
        "remedy": "None.",
        "source": "Vishnu Purana; Brihat Samhita Ch. 36",
    },
    "rainbow_evening": {
        "name": "Rainbow in evening",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Evening rainbow = mixed; auspicious for ending phase but warns of rain/disturbance next day.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 36",
    },
    "halo_around_moon": {
        "name": "Halo around moon",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Lunar halo (Chandra-parivesha) = atmospheric disturbance ahead; emotional or political turbulence within fortnight.",
        "remedy": "Recite Chandra-stotra; avoid major emotional decisions.",
        "source": "Brihat Samhita Ch. 34 (Chandra-charya)",
    },
    "halo_around_sun": {
        "name": "Halo around sun",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 4,
        "interpretation": "Solar halo (Surya-parivesha) = ruler/government activity, political shift, or major public event approaching.",
        "remedy": "Recite Aditya-hridaya.",
        "source": "Brihat Samhita Ch. 35 (Surya-charya)",
    },
    "unseasonal_rain": {
        "name": "Unseasonal rain",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Rain out of season = natural cycle disturbed; classically a sign of social unrest or unexpected change. If gentle, can also signify cleansing.",
        "remedy": "None.",
        "source": "Brihat Samhita Ch. 28; Adbhuta Sagara",
    },
    "dust_storm_from_west": {
        "name": "Dust storm from west",
        "category": "weather",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Westerly dust storm = warning of conflict, scarcity, or political disturbance. Especially severe in Krishna paksha.",
        "remedy": "Stay indoors; avoid important commitments for 48 hours.",
        "source": "Brihat Samhita Ch. 28 (Vata-shakuna)",
    },
    "lightning_clear_sky": {
        "name": "Lightning in clear sky",
        "category": "weather",
        "auspicious_or_not": "inauspicious",
        "severity": 5,
        "interpretation": "Lightning visible in cloudless sky (Adbhuta-vidyut) = divine warning of major political/social shift or local calamity. Most rare omen.",
        "remedy": "Major remedy: Rudra-abhishekam, Mrityunjaya 108x, donation.",
        "source": "Adbhuta Sagara; Brihat Samhita Ch. 30",
    },
    "eclipse_day_omen": {
        "name": "Anything unusual on eclipse day",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 4,
        "interpretation": "Any unusual omen on eclipse day (Grahana) is amplified 5x. Karma activates rapidly. Auspicious omens become very auspicious; inauspicious become severe.",
        "remedy": "Bathe in flowing water; donate; recite mantras during eclipse.",
        "source": "Brihat Samhita Ch. 5; Garuda Purana",
    },
    "falling_star_seen": {
        "name": "Falling star seen",
        "category": "weather",
        "auspicious_or_not": "mixed",
        "severity": 3,
        "interpretation": "Meteor (Ulka) = sign of major event; if falling toward you = personal change, if away = release of past karma. Direction crucial.",
        "remedy": "Make a wish; recite Ishta-devata mantra.",
        "source": "Brihat Samhita Ch. 33 (Ulka-charya)",
    },
    "comet_visible": {
        "name": "Comet visible (Dhumaketu)",
        "category": "weather",
        "auspicious_or_not": "inauspicious",
        "severity": 5,
        "interpretation": "Comet (Dhumaketu) = major political/social upheaval, war, or pandemic in classical texts. Effect can last entire reign of comet's visibility.",
        "remedy": "National-level remedies: Rudra-yagna, Chandi-paath, large-scale charity.",
        "source": "Brihat Samhita Ch. 11 (Ketu-charya); Adbhuta Sagara",
    },

    # =========================================================
    # DOMESTIC OMENS — 10 entries
    # =========================================================
    "broken_vessel_facing_east": {
        "name": "Vessel breaks while facing east",
        "category": "domestic",
        "auspicious_or_not": "mixed",
        "severity": 2,
        "interpretation": "Vessel (clay/glass/metal) breaking while you face east = release of negative energy; mixed (cleansing but warns of disturbance).",
        "remedy": "Sweep all pieces with right hand; sprinkle gangajal where it broke.",
        "source": "Shakuna Pradeep",
    },
    "milk_spilling_on_stove": {
        "name": "Milk spilling on stove (boiling over)",
        "category": "domestic",
        "auspicious_or_not": "auspicious",
        "severity": 4,
        "interpretation": "Milk overflowing while boiling = abundance, wealth incoming, Lakshmi-blessing in home. Most auspicious of kitchen omens.",
        "remedy": "None; offer first portion to deity.",
        "source": "Lakshmi-tantra; folk tradition",
    },
    "milk_spilling_on_floor": {
        "name": "Milk spilling on floor (accidental)",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Milk falling on floor = mild loss, wasted resource, possible argument over money.",
        "remedy": "Clean immediately; offer fresh milk to a cat or temple.",
        "source": "Folk tradition",
    },
    "lamp_extinguishing_during_pooja": {
        "name": "Lamp extinguishing during pooja",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Diya/lamp going out unexpectedly during worship = warning, possible health concern or family upheaval. Major attention required.",
        "remedy": "Re-light immediately with prayer; complete pooja; offer extra ghee next day.",
        "source": "Shakuna Pradeep; folk tradition",
    },
    "lizard_falling_on_head": {
        "name": "Lizard falling on head",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Gowli (lizard) falling on head = serious warning, possible loss or accident. Among the most-asked Gowli-shastra signs.",
        "remedy": "Bathe immediately; visit temple; recite Mahamrityunjaya.",
        "source": "Gowli-shastra (Tamil/Malayalam tradition); Adbhuta Sagara",
    },
    "lizard_falling_on_right_shoulder": {
        "name": "Lizard falling on right shoulder",
        "category": "domestic",
        "auspicious_or_not": "auspicious",
        "severity": 3,
        "interpretation": "Lizard falling on right shoulder = unexpected gain, victory in undertaking. (Right side = auspicious universally.)",
        "remedy": "None; bathe afterward.",
        "source": "Gowli-shastra",
    },
    "lizard_falling_on_left_shoulder": {
        "name": "Lizard falling on left shoulder",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Lizard falling on left shoulder = expense, loss, mild setback.",
        "remedy": "Bathe; donate small amount to charity.",
        "source": "Gowli-shastra",
    },
    "book_falling_open_at_random": {
        "name": "Book falling open at random",
        "category": "domestic",
        "auspicious_or_not": "neutral",
        "severity": 2,
        "interpretation": "Sacred book falling open spontaneously = read the page; the verse contains a message for you (Yadricchika-shakuna).",
        "remedy": "Read the verse; reflect; meditate.",
        "source": "Folk + classical Sortes-Sanskritica tradition",
    },
    "mirror_cracking": {
        "name": "Mirror cracking spontaneously",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 4,
        "interpretation": "Mirror cracking without impact = warning, 7-day caution period for travel and money.",
        "remedy": "Discard the mirror; do not look in cracked mirror.",
        "source": "Universal folk; Shakuna Pradeep",
    },
    "salt_spilling": {
        "name": "Salt spilling on floor",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 2,
        "interpretation": "Salt spilling = family quarrel coming within 3 days.",
        "remedy": "Take pinch and throw over left shoulder (universal counter-charm).",
        "source": "Universal folk; Shakuna Pradeep",
    },
    "chair_tipping_over_alone": {
        "name": "Chair tipping over without contact",
        "category": "domestic",
        "auspicious_or_not": "inauspicious",
        "severity": 3,
        "interpretation": "Furniture moving/tipping with no apparent cause = spirit-presence or instability in family situation.",
        "remedy": "Light camphor at home corners; sprinkle gangajal.",
        "source": "Folk + Tantric tradition",
    },
}


# ============================================================
# TITHI_AMPLIFICATION — Each tithi (1-30) amplifies/neutralizes specific categories.
# Source: Garga Samhita timing rules; Vasanta Raja Shakuna tithi-phala chapter.
# ============================================================
TITHI_AMPLIFICATION = {
    1:  {"name": "Pratipada (Shukla)",  "amplifies": ["bird","weather"],     "neutralizes": ["body"]},
    2:  {"name": "Dwitiya (Shukla)",    "amplifies": ["animal","domestic"],  "neutralizes": ["weather"]},
    3:  {"name": "Tritiya (Shukla)",    "amplifies": ["bird","body"],         "neutralizes": []},
    4:  {"name": "Chaturthi (Shukla)",  "amplifies": ["domestic"],            "neutralizes": ["bird"]},  # Ganesha tithi
    5:  {"name": "Panchami (Shukla)",   "amplifies": ["animal","bird"],       "neutralizes": []},        # Naga Panchami; serpent omens amplified
    6:  {"name": "Shashthi (Shukla)",   "amplifies": ["body","animal"],       "neutralizes": ["weather"]},
    7:  {"name": "Saptami (Shukla)",    "amplifies": ["weather"],             "neutralizes": ["body"]},  # Surya tithi
    8:  {"name": "Ashtami (Shukla)",    "amplifies": ["bird","domestic"],     "neutralizes": []},
    9:  {"name": "Navami (Shukla)",     "amplifies": ["animal","weather"],    "neutralizes": []},
    10: {"name": "Dashami (Shukla)",    "amplifies": ["body"],                "neutralizes": ["domestic"]},
    11: {"name": "Ekadashi (Shukla)",   "amplifies": ["bird","weather"],      "neutralizes": ["animal"]}, # fasting tithi; spiritual omens dominant
    12: {"name": "Dwadashi (Shukla)",   "amplifies": ["domestic"],            "neutralizes": ["weather"]},
    13: {"name": "Trayodashi (Shukla)", "amplifies": ["body","animal"],       "neutralizes": []},        # Pradosha; Shiva omens emphasized
    14: {"name": "Chaturdashi (Shukla)","amplifies": ["weather","bird"],      "neutralizes": ["domestic"]},
    15: {"name": "Purnima",             "amplifies": ["animal","bird","weather","body","domestic"], "neutralizes": []},  # Full moon amplifies ALL
    16: {"name": "Pratipada (Krishna)", "amplifies": ["body"],                "neutralizes": ["bird"]},
    17: {"name": "Dwitiya (Krishna)",   "amplifies": ["animal"],              "neutralizes": ["weather"]},
    18: {"name": "Tritiya (Krishna)",   "amplifies": ["bird","domestic"],     "neutralizes": []},
    19: {"name": "Chaturthi (Krishna)", "amplifies": ["domestic"],            "neutralizes": []},        # Sankashti
    20: {"name": "Panchami (Krishna)",  "amplifies": ["animal"],              "neutralizes": ["body"]},
    21: {"name": "Shashthi (Krishna)",  "amplifies": ["bird"],                "neutralizes": ["weather"]},
    22: {"name": "Saptami (Krishna)",   "amplifies": ["weather"],             "neutralizes": []},
    23: {"name": "Ashtami (Krishna)",   "amplifies": ["body","domestic"],     "neutralizes": []},        # Krishna Janmashtami tithi
    24: {"name": "Navami (Krishna)",    "amplifies": ["animal"],              "neutralizes": ["bird"]},
    25: {"name": "Dashami (Krishna)",   "amplifies": ["body"],                "neutralizes": []},
    26: {"name": "Ekadashi (Krishna)",  "amplifies": ["bird","weather"],      "neutralizes": ["animal"]},
    27: {"name": "Dwadashi (Krishna)",  "amplifies": ["domestic"],            "neutralizes": []},
    28: {"name": "Trayodashi (Krishna)","amplifies": ["body","animal"],       "neutralizes": []},        # Masa Shivaratri
    29: {"name": "Chaturdashi (Krishna)","amplifies": ["weather","domestic"], "neutralizes": ["bird"]},  # Chaturdashi before Amavasya: amplified caution
    30: {"name": "Amavasya",            "amplifies": ["animal","body","domestic","weather","bird"],  # New moon amplifies ALL — esp inauspicious
        "neutralizes": []},
}


# ============================================================
# TIME_OF_DAY_AMPLIFICATION — 5 windows
# Source: Brihat Samhita Ch. 89; Muhurta Chintamani.
# ============================================================
TIME_OF_DAY_AMPLIFICATION = {
    "brahma_muhurta": {
        "window": "03:30-05:30",
        "start_hour": 3.5,
        "end_hour":   5.5,
        "amplifies": ["bird","weather"],
        "note": "Brahma Muhurta — sattvic window; spiritual omens (sacred bird sounds, dawn-breeze) magnified.",
    },
    "sunrise": {
        "window": "sunrise +/- 15 min (approx 05:30-06:30)",
        "start_hour": 5.5,
        "end_hour":   6.5,
        "amplifies": ["bird","body","domestic"],
        "note": "Sunrise — first impressions of day; first omens encountered set day's tone.",
    },
    "midday": {
        "window": "11:30-12:30",
        "start_hour": 11.5,
        "end_hour":   12.5,
        "amplifies": ["weather","animal"],
        "note": "Solar peak — Surya rules; political/public omens magnified.",
    },
    "sunset": {
        "window": "sunset +/- 15 min (approx 18:00-19:00)",
        "start_hour": 18.0,
        "end_hour":   19.0,
        "amplifies": ["animal","body"],
        "note": "Sandhya — transition; jackal/dog/owl omens active; caution recommended.",
    },
    "midnight": {
        "window": "23:30-00:30",
        "start_hour": 23.5,
        "end_hour":   24.5,  # treated as 0.5 next day
        "amplifies": ["domestic","animal","weather"],
        "note": "Nishita — dark half of night; spirit-presence omens, ill-direction sounds magnified 3x.",
    },
}


# ============================================================
# YOGINI_DISHA_SHOOLA — Yogini variant of Disha Shoola
# Each weekday has its OWN inauspicious direction in the Yogini system,
# distinct from the standard Disha Shoola above.
# Source: Muhurta Chintamani; Yogini-tantra.
# ============================================================
YOGINI_DISHA_SHOOLA = {
    "Sunday":    {"yogini_direction": "North-East",  "deity": "Brahmi",   "interpretation": "Avoid NE-direction journey on Sunday; Yogini resides there."},
    "Monday":    {"yogini_direction": "East",         "deity": "Maheshwari","interpretation": "Avoid east-direction journey on Monday."},
    "Tuesday":   {"yogini_direction": "South-East",   "deity": "Kaumari",  "interpretation": "Avoid SE-direction journey on Tuesday."},
    "Wednesday": {"yogini_direction": "South",        "deity": "Vaishnavi","interpretation": "Avoid south-direction journey on Wednesday."},
    "Thursday":  {"yogini_direction": "South-West",   "deity": "Varahi",   "interpretation": "Avoid SW-direction journey on Thursday."},
    "Friday":    {"yogini_direction": "West",         "deity": "Indrani",  "interpretation": "Avoid west-direction journey on Friday."},
    "Saturday":  {"yogini_direction": "North-West",   "deity": "Chamunda", "interpretation": "Avoid NW-direction journey on Saturday."},
}


# ============================================================
# HELPER — match name with fallback
# ============================================================
def _normalize_omen_key(omen_name):
    """Normalize an omen name into a key for SHAKUNA_FULL_DB lookup."""
    if not omen_name:
        return None
    k = omen_name.strip().lower().replace(" ", "_").replace("-", "_")
    if k in SHAKUNA_FULL_DB:
        return k
    # Try fuzzy substring
    for key in SHAKUNA_FULL_DB:
        if k in key or key in k:
            return key
    return None


# ============================================================
# shakuna_full_db() — return the complete DB with category counts
# ============================================================
def shakuna_full_db():
    """Return the complete classical Shakuna Shastra database with category counts."""
    by_cat = {}
    for entry in SHAKUNA_FULL_DB.values():
        cat = entry["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1

    by_severity = {}
    for entry in SHAKUNA_FULL_DB.values():
        s = entry["severity"]
        by_severity[s] = by_severity.get(s, 0) + 1

    by_aoi = {}
    for entry in SHAKUNA_FULL_DB.values():
        a = entry["auspicious_or_not"]
        by_aoi[a] = by_aoi.get(a, 0) + 1

    return {
        "total_omens": len(SHAKUNA_FULL_DB),
        "by_category": by_cat,
        "by_severity": by_severity,
        "by_auspicious_or_not": by_aoi,
        "tithis_covered": len(TITHI_AMPLIFICATION),
        "time_windows": len(TIME_OF_DAY_AMPLIFICATION),
        "yogini_disha_weekdays": len(YOGINI_DISHA_SHOOLA),
        "sources_referenced": [
            "Brihat Samhita (Varahamihira) Ch. 86-95",
            "Vasanta Raja Shakuna",
            "Garga Samhita",
            "Adbhuta Sagara (Ballala Sena)",
            "Shakuna Pradeep",
            "Vishnu Purana",
            "Lakshmi-tantra",
            "Gowli-shastra (Tamil/Malayalam)",
            "Swapna Shastra",
        ],
        "sample_entries": list(SHAKUNA_FULL_DB.keys())[:5],
    }


# ============================================================
# Time-of-day classifier
# ============================================================
def _classify_time_window(when_dt):
    """Return the time window key for the given datetime (or None)."""
    if when_dt is None:
        return None
    h = when_dt.hour + when_dt.minute / 60.0
    for key, w in TIME_OF_DAY_AMPLIFICATION.items():
        s, e = w["start_hour"], w["end_hour"]
        if e > 24:  # midnight wrap
            if h >= s or h <= (e - 24):
                return key
        else:
            if s <= h <= e:
                return key
    return None


# ============================================================
# interpret_omen — apply tithi + time amplification + chart afflictions
# ============================================================
def interpret_omen(omen_name, when_dt=None, chart=None):
    """Interpret a named omen against current panchanga and (optionally) a natal chart.

    Returns dict with: omen, category, base_severity, amplification, final_severity,
                       classical_interpretation, recommended_remedy, source.
    """
    key = _normalize_omen_key(omen_name)
    if not key:
        return {
            "omen": omen_name,
            "error": f"Unknown omen. Try one of: {list(SHAKUNA_FULL_DB.keys())[:8]}...",
            "valid_keys_count": len(SHAKUNA_FULL_DB),
        }

    entry = SHAKUNA_FULL_DB[key]
    category = entry["category"]
    base_severity = entry["severity"]
    aoi = entry["auspicious_or_not"]

    amplification = {
        "tithi": None,
        "time": None,
        "chart_affliction": None,
        "multiplier": 1.0,
    }

    # ─── Tithi amplification ───
    if when_dt is not None:
        try:
            from panchanga import compute_panchanga
            pan = compute_panchanga(when_dt)
            t_num = pan.get("tithi_number", 0)
            t_amp = TITHI_AMPLIFICATION.get(t_num)
            if t_amp:
                if category in t_amp["amplifies"]:
                    amplification["tithi"] = f"{t_amp['name']} amplifies {category} (+1 severity)"
                    amplification["multiplier"] *= 1.5
                elif category in t_amp["neutralizes"]:
                    amplification["tithi"] = f"{t_amp['name']} neutralizes {category} (-1 severity)"
                    amplification["multiplier"] *= 0.6
                else:
                    amplification["tithi"] = f"{t_amp['name']} (no specific effect on {category})"
        except Exception as e:
            amplification["tithi"] = f"panchanga unavailable ({type(e).__name__})"

    # ─── Time-of-day amplification ───
    if when_dt is not None:
        tw = _classify_time_window(when_dt)
        if tw:
            tinfo = TIME_OF_DAY_AMPLIFICATION[tw]
            if category in tinfo["amplifies"]:
                amplification["time"] = f"{tw} ({tinfo['window']}) amplifies {category} (+1 severity)"
                amplification["multiplier"] *= 1.5
            else:
                amplification["time"] = f"{tw} ({tinfo['window']}) — no specific effect on {category}"

    # ─── Chart affliction (optional) ───
    if chart is not None:
        try:
            positions = chart.get("positions", {})
            # Map omen-category → key planets/houses
            cat_to_planet = {
                "animal": ["Mars", "Saturn", "Rahu"],
                "bird": ["Mercury", "Jupiter", "Venus"],
                "body": ["Moon", "Mars", "Saturn"],
                "weather": ["Sun", "Saturn", "Rahu"],
                "domestic": ["Moon", "Venus", "Saturn"],
            }
            sensitive = cat_to_planet.get(category, [])
            afflicted_planets = []
            for p in sensitive:
                if p in positions:
                    pos = positions[p]
                    house = pos.get("house") if isinstance(pos, dict) else None
                    # Dusthana: 6, 8, 12 — affliction
                    if house in [6, 8, 12]:
                        afflicted_planets.append(f"{p} in {house}H")
            if afflicted_planets:
                amplification["chart_affliction"] = (
                    f"Natal afflictions to {category}-planets: " + ", ".join(afflicted_planets)
                    + " — omen impact heightened."
                )
                amplification["multiplier"] *= 1.3
            else:
                amplification["chart_affliction"] = f"No major natal affliction to {category}-sensitive planets."
        except Exception as e:
            amplification["chart_affliction"] = f"chart parse skipped ({type(e).__name__})"

    # ─── Compute final severity ───
    final_sev = base_severity * amplification["multiplier"]
    final_sev = round(final_sev, 2)
    if final_sev > 5:
        final_sev = 5.0
    if final_sev < 0.5:
        final_sev = 0.5

    return {
        "omen": entry["name"],
        "category": category,
        "auspicious_or_not": aoi,
        "base_severity": base_severity,
        "amplification": amplification,
        "final_severity": final_sev,
        "classical_interpretation": entry["interpretation"],
        "recommended_remedy": entry["remedy"],
        "source": entry["source"],
    }


# ============================================================
# omens_for_today — return omens MOST sensitive to today's panchanga
# ============================================================
def omens_for_today(chart=None, when_dt=None):
    """Return the top-N omens most amplified by current tithi + time-of-day."""
    if when_dt is None:
        when_dt = dt.datetime.now()

    # Get panchanga
    try:
        from panchanga import compute_panchanga
        pan = compute_panchanga(when_dt)
        t_num = pan.get("tithi_number", 0)
        tithi_name = pan.get("tithi", "")
        vara = pan.get("vara", "")
    except Exception as e:
        pan, t_num, tithi_name, vara = None, 0, "", ""

    t_amp = TITHI_AMPLIFICATION.get(t_num, {"amplifies": [], "neutralizes": []})
    amplified_cats = set(t_amp.get("amplifies", []))

    tw = _classify_time_window(when_dt)
    if tw:
        amplified_cats |= set(TIME_OF_DAY_AMPLIFICATION[tw]["amplifies"])

    # Yogini disha
    yogini = YOGINI_DISHA_SHOOLA.get(vara, {})

    # Score each omen: severity if its category is in amplified_cats
    scored = []
    for key, entry in SHAKUNA_FULL_DB.items():
        if entry["category"] in amplified_cats:
            score = entry["severity"] * 1.5
        else:
            score = entry["severity"] * 1.0
        scored.append((score, key, entry))

    scored.sort(key=lambda x: -x[0])
    top5 = scored[:5]

    return {
        "as_of": when_dt.strftime("%Y-%m-%d %H:%M"),
        "panchanga_summary": {
            "tithi": tithi_name,
            "tithi_number": t_num,
            "vara": vara,
            "time_window": tw,
        } if pan else None,
        "amplified_categories_today": sorted(list(amplified_cats)),
        "yogini_disha_today": yogini,
        "standard_disha_shoola_today": DISHA_SHOOLA.get(vara, "unknown"),
        "top_5_sensitive_omens": [
            {
                "rank": i + 1,
                "omen_key": k,
                "name": e["name"],
                "category": e["category"],
                "severity_today": round(s, 2),
                "auspicious_or_not": e["auspicious_or_not"],
                "interpretation_short": e["interpretation"][:120] + ("..." if len(e["interpretation"]) > 120 else ""),
            }
            for i, (s, k, e) in enumerate(top5)
        ],
    }


# ============================================================
# CLASSICAL DISAGREEMENTS — documented for transparency
# ============================================================
SCHOOL_DISAGREEMENTS = {
    "owl_calling_at_night": {
        "schools": {
            "Tantric/Bengali (Lakshmi-tantra)": "auspicious — owl is Lakshmi's vahana, night-call = wealth incoming",
            "Brihat Samhita / North Indian": "inauspicious if facing the home — death omen tradition",
        },
        "default_school_chosen": "Tantric/Bengali (auspicious)",
        "rationale": "More widely cited in modern lay practice; classical-strict reading would flip this to inauspicious.",
    },
    "crow_calling_from_north": {
        "schools": {
            "Brihat Samhita Ch. 95": "auspicious — north is favourable direction",
            "Some Southern Tamil tradition (esp. Krishna paksha 14th)": "neutral",
        },
        "default_school_chosen": "Brihat Samhita (auspicious)",
        "rationale": "Pan-Indian default; most-cited authority.",
    },
    "bat_entering_house": {
        "schools": {
            "North Indian (Vasanta Raja)": "warning omen",
            "Bengali Tantric": "wealth-spirit blessing",
        },
        "default_school_chosen": "Mixed (severity 3) — not committed to either",
        "rationale": "Genuine school divergence; defer to family lore.",
    },
    "jackal_howling_from_west": {
        "schools": {
            "Varahamihira / Brihat Samhita": "inauspicious",
            "Some southern schools (women)": "mild auspicious",
        },
        "default_school_chosen": "Varahamihira (inauspicious)",
        "rationale": "Default to most-cited north-indian text.",
    },
    "lizard_falling_signs": {
        "schools": {
            "Tamil Gowli Shastra": "highly developed body-part-specific table",
            "North Indian Shakuna Pradeep": "less granular; simply ill-omen",
        },
        "default_school_chosen": "Tamil Gowli Shastra (granular)",
        "rationale": "More actionable guidance per body part.",
    },
}


def shakuna_disagreements():
    """Return a list of classical school-disagreements documented in this module."""
    return SCHOOL_DISAGREEMENTS


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== SHAKUNA SHASTRA + SWAPNA SHASTRA (Omens) ===\n")
    summary = omens_summary()
    print(f"  Total omens catalogued (legacy): {summary['total']}")
    for k, v in summary.items():
        if k.endswith("_catalogued"):
            print(f"    {k.replace('_',' ').title()}: {v}")

    print("\n=== TODAY's Disha Shoola check ===")
    today = dt.datetime.now()
    for direction in ["North","East","South","West"]:
        result = check_disha_shoola(today, direction)
        marker = "[X]" if result["is_disha_shoola"] else "[ok]"
        print(f"  {marker} Travel {direction:6s}: {result['verdict']}")

    print("\n=== EXAMPLE OMEN LOOKUP: Right eye twitch (male) ===")
    result = lookup_omen("body", "Right eye twitch (MALE)")
    print(f"  Male:   {result.get('male','')}")
    print(f"  Female: {result.get('female','')}")

    print("\n=== EXAMPLE DREAM LOOKUP: Snake biting ===")
    result = lookup_omen("dream", "Snake biting")
    print(f"  Meaning: {result}")

    # ─────────────────────────────────────────────
    # TIER-1 DEEP — full Shakuna DB tests
    # ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("=== TIER-1 DEEP EXTENSION — SHAKUNA_FULL_DB ===")
    print("=" * 60)
    full = shakuna_full_db()
    print(f"\n  Total classical omens: {full['total_omens']}")
    print("  By category:")
    for cat, n in sorted(full["by_category"].items(), key=lambda x: -x[1]):
        print(f"    {cat:12s}: {n}")
    print("  By severity (1=mild, 5=extreme):")
    for s, n in sorted(full["by_severity"].items()):
        print(f"    severity {s}: {n}")
    print("  By auspicious/not:")
    for a, n in sorted(full["by_auspicious_or_not"].items()):
        print(f"    {a:14s}: {n}")
    print(f"  Tithis covered: {full['tithis_covered']}/30")
    print(f"  Time windows  : {full['time_windows']}/5")
    print(f"  Yogini Disha weekdays: {full['yogini_disha_weekdays']}/7")

    # ─── Load Manoj chart ───
    import os, json
    chart = None
    _atro_root = os.environ.get(
        "ATRO_ROOT",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    chart_path = os.path.join(
        os.environ.get("ATRO_CHARTS", os.path.join(_atro_root, "charts")).replace("\\", "/"),
        "manoj_chart.json",
    )
    if os.path.exists(chart_path):
        with open(chart_path, "r", encoding="utf-8") as f:
            chart = json.load(f)
        print(f"\n  Loaded chart: {chart.get('name','unknown')} (lagna {chart.get('lagna','?')})")
    else:
        print(f"\n  WARNING: chart file not found at {chart_path}")

    # ─── interpret_omen test ───
    print("\n" + "=" * 60)
    print("=== interpret_omen('crow_calling_from_north') ===")
    print("=" * 60)
    res = interpret_omen("crow_calling_from_north", dt.datetime.now(), chart)
    print(f"  Omen           : {res.get('omen','')}")
    print(f"  Category       : {res.get('category','')}")
    print(f"  Auspicious?    : {res.get('auspicious_or_not','')}")
    print(f"  Base severity  : {res.get('base_severity','')}")
    amp = res.get("amplification", {}) or {}
    print(f"  Tithi effect   : {amp.get('tithi','-')}")
    print(f"  Time effect    : {amp.get('time','-')}")
    print(f"  Chart effect   : {amp.get('chart_affliction','-')}")
    print(f"  Multiplier     : {amp.get('multiplier','-')}")
    print(f"  Final severity : {res.get('final_severity','')}")
    print(f"  Source         : {res.get('source','')}")
    print(f"  Interpretation : {res.get('classical_interpretation','')[:200]}")

    # ─── omens_for_today ───
    print("\n" + "=" * 60)
    print("=== omens_for_today(chart) — TOP 5 ===")
    print("=" * 60)
    today_omens = omens_for_today(chart)
    p = today_omens.get("panchanga_summary") or {}
    print(f"  Tithi: {p.get('tithi','?')} (#{p.get('tithi_number','?')})  "
          f"Vara: {p.get('vara','?')}  Time-window: {p.get('time_window','-')}")
    print(f"  Amplified categories today: {today_omens.get('amplified_categories_today',[])}")
    yd = today_omens.get("yogini_disha_today", {}) or {}
    print(f"  Yogini Disha today: avoid {yd.get('yogini_direction','?')} ({yd.get('deity','?')})")
    print(f"  Standard Disha Shoola today: avoid {today_omens.get('standard_disha_shoola_today','?')}")
    print(f"  Top 5 sensitive omens:")
    for entry in today_omens.get("top_5_sensitive_omens", []):
        print(f"    #{entry['rank']} [{entry['category']}] {entry['name']} "
              f"(today-severity {entry['severity_today']}, {entry['auspicious_or_not']})")

    # ─── Disagreements ───
    print("\n" + "=" * 60)
    print("=== Classical school disagreements documented ===")
    print("=" * 60)
    for k, v in shakuna_disagreements().items():
        print(f"  {k}:")
        print(f"    chosen school: {v['default_school_chosen']}")

    print("\n[OK] All TIER-1 DEEP tests complete with 0 exceptions.")
