from typing import Dict, Any, List
from datetime import datetime, timedelta
from math import sin, cos, tan, radians, degrees, atan2, sqrt, floor
import re

# =============================================================================
# Thai Astrology Analyzer — Bazi + Western + Vedic + Harmony
# =============================================================================

# --- Heavenly Stems (天干) ---
HEAVENLY_STEMS = [
    "甲 Jia", "乙 Yi", "丙 Bing", "丁 Ding", "戊 Wu",
    "己 Ji", "庚 Geng", "辛 Xin", "壬 Ren", "癸 Gui",
]
STEM_ELEMENTS = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
STEM_YINYANG = ["Yang", "Yin", "Yang", "Yin", "Yang", "Yin", "Yang", "Yin", "Yang", "Yin"]

# --- Earthly Branches (地支) ---
EARTHLY_BRANCHES = [
    "子 Zi", "丑 Chou", "寅 Yin", "卯 Mao", "辰 Chen", "巳 Si",
    "午 Wu", "未 Wei", "申 Shen", "酉 You", "戌 Xu", "亥 Hai",
]
BRANCH_ELEMENTS = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire", "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]
BRANCH_ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

# --- 10 Gods (十神) relative to Day Master ---
# Order: same element+same yin/yang, same element+opposite, produce me, drain me, overcome me, I overcome, I produce
# Simplified mapping based on stem relation to Day Master
TEN_GOD_PATTERNS = {
    "same_same": "比肩 Bi Jian (Friend)",
    "same_opp": "劫財 Jie Cai (Rob Wealth)",
    "produce_me": "印綬 Yin Shou (Resource)",
    "drain_me": "食傷 Shi Shang (Output)",
    "overcome_me": "官殺 Guan Sha (Influence)",
    "i_overcome": "財星 Cai Xing (Wealth)",
    "i_produce": "食神 Shi Shen (Food God)",
}

# --- Western Zodiac ---
WESTERN_SIGNS = [
    ("Aries", 3, 21, 4, 19, "Fire", "Mars"),
    ("Taurus", 4, 20, 5, 20, "Earth", "Venus"),
    ("Gemini", 5, 21, 6, 20, "Air", "Mercury"),
    ("Cancer", 6, 21, 7, 22, "Water", "Moon"),
    ("Leo", 7, 23, 8, 22, "Fire", "Sun"),
    ("Virgo", 8, 23, 9, 22, "Earth", "Mercury"),
    ("Libra", 9, 23, 10, 22, "Air", "Venus"),
    ("Scorpio", 10, 23, 11, 21, "Water", "Pluto"),
    ("Sagittarius", 11, 22, 12, 21, "Fire", "Jupiter"),
    ("Capricorn", 12, 22, 1, 19, "Earth", "Saturn"),
    ("Aquarius", 1, 20, 2, 18, "Air", "Uranus"),
    ("Pisces", 2, 19, 3, 20, "Water", "Neptune"),
]

# --- Vedic Nakshatras (27) ---
VEDIC_NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]
NAKSHATRA_RULER = [
    "Mars", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

# --- Vedic Rashis (Sidereal) ---
VEDIC_RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]
VEDIC_RASHI_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# --- 5 Elements cycle ---
ELEMENT_CYCLE = ["Wood", "Fire", "Earth", "Metal", "Water"]
ELEMENT_PRODUCES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
ELEMENT_OVERCOMES = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}

# --- Thai solar month mapping for Bazi month pillar (approximate) ---
# Bazi month branch changes at solar terms (节气), simplified here to ~4-5th of each month
MONTH_BRANCH_START = [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6]  # Jan=子, Feb=丑... wait Bazi month starts at 寅
# Correct: Bazi month branches start at 寅 (Tiger) for 正月 (approx Feb)
MONTH_BRANCH_MAP = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]  # Jan->寅, Feb->卯...


def _solar_longitude(year: int, month: int, day: int) -> float:
    """Approximate solar longitude in degrees (simplified)."""
    # Day of year
    doy = (datetime(year, month, day) - datetime(year, 1, 1)).days
    # Approximate longitude: 0 at vernal equinox (~Mar 20), but we simplify to Jan 1 = 280°
    L = (280.46 + 0.9856474 * doy) % 360
    return L


def _calculate_bazi(year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, Any]:
    """Calculate Four Pillars of Destiny (Bazi / 八字)."""
    # Year pillar: based on Chinese lunar year, approximated by solar year
    # Stem index: (year - 4) % 10
    year_stem_idx = (year - 4) % 10
    year_branch_idx = (year - 4) % 12

    # Month pillar: simplified using solar month approximation
    # Adjust month for solar terms (simplified: if before ~5th, use previous month branch)
    adjusted_month = month - 1  # 0-indexed
    if day < 5:
        adjusted_month -= 1
    if adjusted_month < 0:
        adjusted_month = 11
    month_branch_idx = MONTH_BRANCH_MAP[adjusted_month]
    # Month stem is derived from year stem: formula varies by tradition
    # Simplified: year_stem_idx * 2 + month (1-based), mod 10
    month_stem_idx = (year_stem_idx * 2 + adjusted_month + 1) % 10

    # Day pillar: using simplified algorithm
    # Base date: 1900-01-31 = 甲辰 (stem=0, branch=4) - known reference
    base = datetime(1900, 1, 31)
    target = datetime(year, month, day)
    diff_days = (target - base).days
    day_stem_idx = (0 + diff_days) % 10
    day_branch_idx = (4 + diff_days) % 12

    # Hour pillar: based on day stem and hour (Chinese double-hour)
    # 23:00-01:00 = 子 (0), 01:00-03:00 = 丑 (1), ...
    chinese_hour = ((hour + 1) // 2) % 12
    # Hour stem derived from day stem
    hour_stem_base = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]  # varies by day stem
    hour_stem_idx = (hour_stem_base[day_stem_idx] + chinese_hour) % 10
    hour_branch_idx = chinese_hour

    pillars = {
        "year": {
            "stem": HEAVENLY_STEMS[year_stem_idx],
            "stem_element": STEM_ELEMENTS[year_stem_idx],
            "stem_yinyang": STEM_YINYANG[year_stem_idx],
            "branch": EARTHLY_BRANCHES[year_branch_idx],
            "branch_element": BRANCH_ELEMENTS[year_branch_idx],
            "animal": BRANCH_ANIMALS[year_branch_idx],
        },
        "month": {
            "stem": HEAVENLY_STEMS[month_stem_idx],
            "stem_element": STEM_ELEMENTS[month_stem_idx],
            "stem_yinyang": STEM_YINYANG[month_stem_idx],
            "branch": EARTHLY_BRANCHES[month_branch_idx],
            "branch_element": BRANCH_ELEMENTS[month_branch_idx],
            "animal": BRANCH_ANIMALS[month_branch_idx],
        },
        "day": {
            "stem": HEAVENLY_STEMS[day_stem_idx],
            "stem_element": STEM_ELEMENTS[day_stem_idx],
            "stem_yinyang": STEM_YINYANG[day_stem_idx],
            "branch": EARTHLY_BRANCHES[day_branch_idx],
            "branch_element": BRANCH_ELEMENTS[day_branch_idx],
            "animal": BRANCH_ANIMALS[day_branch_idx],
        },
        "hour": {
            "stem": HEAVENLY_STEMS[hour_stem_idx],
            "stem_element": STEM_ELEMENTS[hour_stem_idx],
            "stem_yinyang": STEM_YINYANG[hour_stem_idx],
            "branch": EARTHLY_BRANCHES[hour_branch_idx],
            "branch_element": BRANCH_ELEMENTS[hour_branch_idx],
            "animal": BRANCH_ANIMALS[hour_branch_idx],
        },
    }

    # Day Master = day stem
    day_master = {
        "stem": HEAVENLY_STEMS[day_stem_idx],
        "element": STEM_ELEMENTS[day_stem_idx],
        "yinyang": STEM_YINYANG[day_stem_idx],
    }

    # Count 5 elements in full chart
    element_counts = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    for p in pillars.values():
        element_counts[p["stem_element"]] += 1
        element_counts[p["branch_element"]] += 1

    # Yin/Yang balance
    yin_count = sum(1 for p in pillars.values() if p["stem_yinyang"] == "Yin") + \
                sum(1 for p in pillars.values() if p["branch_element"] in ["Earth", "Water"])  # simplified
    yang_count = 8 - yin_count  # 8 characters total

    # Luck cycle (大运) - simplified: each 10-year period
    luck_cycles = []
    for i in range(1, 9):
        luck_stem = (year_stem_idx + i) % 10
        luck_branch = (year_branch_idx + i) % 12
        luck_cycles.append({
            "age_range": f"{i*10}-{(i+1)*10}",
            "stem": HEAVENLY_STEMS[luck_stem],
            "branch": EARTHLY_BRANCHES[luck_branch],
            "element": STEM_ELEMENTS[luck_stem],
        })

    return {
        "pillars": pillars,
        "day_master": day_master,
        "element_counts": element_counts,
        "yinyang_balance": {"yin": yin_count, "yang": yang_count},
        "luck_cycles": luck_cycles,
        "hidden_stems": _get_hidden_stems(day_branch_idx),
    }


def _get_hidden_stems(branch_idx: int) -> List[str]:
    """Hidden stems inside earthly branches (simplified mapping)."""
    hidden = {
        0: ["癸 Gui"],    # 子
        1: ["己 Ji", "癸 Gui", "辛 Xin"],  # 丑
        2: ["甲 Jia", "丙 Bing", "戊 Wu"],  # 寅
        3: ["乙 Yi"],    # 卯
        4: ["戊 Wu", "乙 Yi", "癸 Gui"],  # 辰
        5: ["丙 Bing", "庚 Geng", "戊 Wu"],  # 巳
        6: ["丁 Ding", "己 Ji"],  # 午
        7: ["己 Ji", "丁 Ding", "乙 Yi"],  # 未
        8: ["庚 Geng", "壬 Ren", "戊 Wu"],  # 申
        9: ["辛 Xin"],   # 酉
        10: ["戊 Wu", "辛 Xin", "丁 Ding"], # 戌
        11: ["壬 Ren", "甲 Jia"],  # 亥
    }
    return hidden.get(branch_idx, [])


def _calculate_western(year: int, month: int, day: int, hour: int, minute: int, lat: float = 13.7563, lon: float = 100.5018) -> Dict[str, Any]:
    """Calculate Western astrology chart (simplified)."""
    # Sun sign
    sun_sign = None
    for name, sm, sd, em, ed, elem, ruler in WESTERN_SIGNS:
        if (month == sm and day >= sd) or (month == em and day <= ed):
            sun_sign = {"sign": name, "element": elem, "ruler": ruler}
            break
        if sm > em:  # crosses year boundary (Capricorn/Aquarius)
            if (month == sm and day >= sd) or (month == em and day <= ed) or month > sm or month < em:
                sun_sign = {"sign": name, "element": elem, "ruler": ruler}
                break
    if not sun_sign:
        sun_sign = {"sign": "Capricorn", "element": "Earth", "ruler": "Saturn"}

    # Moon sign approximation (simplified: moon moves ~13°/day, ~2.5 days per sign)
    # Known: new moon ~month start varies; we approximate based on day of month
    moon_day = (day % 28) / 2.33  # ~2.33 days per sign
    moon_sign_idx = int(moon_day) % 12
    moon_sign_name = WESTERN_SIGNS[moon_sign_idx][0]
    moon_elem = WESTERN_SIGNS[moon_sign_idx][5]
    moon_sign = {"sign": moon_sign_name, "element": moon_elem}

    # Ascendant approximation based on time
    # Rough: ascendant moves ~1 sign per 2 hours
    # 6 AM = rising near sun sign, each 2 hours shifts by one sign backward
    time_offset = ((hour + minute / 60) - 6) / 2
    ascendant_idx = (WESTERN_SIGNS.index(next(s for s in WESTERN_SIGNS if s[0] == sun_sign["sign"])) - int(time_offset)) % 12
    ascendant = {"sign": WESTERN_SIGNS[ascendant_idx][0], "element": WESTERN_SIGNS[ascendant_idx][5]}

    # Planetary positions (simplified)
    doy = (datetime(year, month, day) - datetime(year, 1, 1)).days + hour / 24
    planets = {
        "Sun": {"sign": sun_sign["sign"], "degree": (doy / 365.25 * 360) % 30},
        "Moon": {"sign": moon_sign["sign"], "degree": (doy / 27.32 * 360) % 30},
        "Mercury": {"sign": WESTERN_SIGNS[(int(doy / 88 * 12)) % 12][0], "degree": 0},
        "Venus": {"sign": WESTERN_SIGNS[(int(doy / 225 * 12)) % 12][0], "degree": 0},
        "Mars": {"sign": WESTERN_SIGNS[(int(doy / 687 * 12)) % 12][0], "degree": 0},
        "Jupiter": {"sign": WESTERN_SIGNS[(int(doy / 4333 * 12)) % 12][0], "degree": 0},
        "Saturn": {"sign": WESTERN_SIGNS[(int(doy / 10759 * 12)) % 12][0], "degree": 0},
    }

    # Element balance
    element_balance = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    element_balance[sun_sign["element"]] += 3
    element_balance[moon_sign["element"]] += 2
    element_balance[ascendant["element"]] += 2

    # Houses (simplified - 12 houses with ascendant as House 1)
    houses = []
    for i in range(12):
        house_sign_idx = (ascendant_idx + i) % 12
        houses.append({
            "house": i + 1,
            "sign": WESTERN_SIGNS[house_sign_idx][0],
            "element": WESTERN_SIGNS[house_sign_idx][5],
            "area": _house_meaning(i + 1),
        })

    return {
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "ascendant": ascendant,
        "planets": planets,
        "element_balance": element_balance,
        "houses": houses,
        "dominant_element": max(element_balance, key=element_balance.get),
    }


def _house_meaning(house_num: int) -> str:
    meanings = {
        1: "Self, personality, appearance",
        2: "Values, money, possessions",
        3: "Communication, siblings, short trips",
        4: "Home, family, roots",
        5: "Creativity, romance, children",
        6: "Health, work, daily routines",
        7: "Partnerships, marriage, contracts",
        8: "Transformation, shared resources, death",
        9: "Higher learning, travel, philosophy",
        10: "Career, public image, authority",
        11: "Friends, groups, hopes",
        12: "Subconscious, secrets, spirituality",
    }
    return meanings.get(house_num, "")


def _calculate_vedic(year: int, month: int, day: int, hour: int, minute: int, lat: float = 13.7563, lon: float = 100.5018) -> Dict[str, Any]:
    """Calculate Vedic astrology chart (simplified sidereal positions)."""
    # Ayanamsa approximation (Lahiri): ~24° in 2024, increases ~1° per 72 years
    ayanamsa = 24.0 + (year - 2024) / 72.0

    # Sidereal sun position = tropical - ayanamsa
    doy = (datetime(year, month, day) - datetime(year, 1, 1)).days + hour / 24
    tropical_sun_deg = (doy / 365.25 * 360) % 360
    sidereal_sun_deg = (tropical_sun_deg - ayanamsa) % 360

    # Sun sign in Vedic (Rashi)
    sun_rashi_idx = int(sidereal_sun_deg / 30) % 12
    sun_rashi = VEDIC_RASHIS[sun_rashi_idx]
    sun_rashi_lord = VEDIC_RASHI_LORDS[sun_rashi_idx]

    # Moon sign (most important in Vedic) - approximate
    tropical_moon_deg = (doy / 27.32 * 360) % 360
    sidereal_moon_deg = (tropical_moon_deg - ayanamsa) % 360
    moon_rashi_idx = int(sidereal_moon_deg / 30) % 12
    moon_rashi = VEDIC_RASHIS[moon_rashi_idx]
    moon_rashi_lord = VEDIC_RASHI_LORDS[moon_rashi_idx]

    # Nakshatra: 27 nakshatras, each 13°20' (13.333°)
    nakshatra_idx = int(sidereal_moon_deg / (360 / 27)) % 27
    nakshatra = VEDIC_NAKSHATRAS[nakshatra_idx]
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_idx]
    nakshatra_ruler = NAKSHATRA_RULER[nakshatra_idx]

    # Pada (quarter of nakshatra): 4 padas per nakshatra
    pada = int((sidereal_moon_deg % (360 / 27)) / (360 / 27 / 4)) + 1

    # Ascendant (Lagna) in sidereal
    time_offset = ((hour + minute / 60) - 6) / 2
    tropical_asc = (tropical_sun_deg - time_offset * 30) % 360
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    lagna_idx = int(sidereal_asc / 30) % 12
    lagna = VEDIC_RASHIS[lagna_idx]
    lagna_lord = VEDIC_RASHI_LORDS[lagna_idx]

    # Dasha (Vimshottari): based on Moon nakshatra lord
    dasha_lord = nakshatra_lord
    dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    current_dasha_years = dasha_years.get(dasha_lord, 10)

    # Yogas (combinations) - simplified checks
    yogas = []
    if sun_rashi_idx == moon_rashi_idx:
        yogas.append("Budha-Aditya Yoga (Sun-Moon conjunction)")
    if abs(sun_rashi_idx - moon_rashi_idx) == 6:
        yogas.append("Opposition Yoga (Sun-Moon 180°)")
    if sun_rashi_lord == moon_rashi_lord:
        yogas.append("Rashi Parivartana (Sign exchange potential)")

    return {
        "sun_rashi": {"sign": sun_rashi, "lord": sun_rashi_lord, "degree": round(sidereal_sun_deg % 30, 2)},
        "moon_rashi": {"sign": moon_rashi, "lord": moon_rashi_lord, "degree": round(sidereal_moon_deg % 30, 2)},
        "nakshatra": {"name": nakshatra, "lord": nakshatra_lord, "ruler": nakshatra_ruler, "pada": pada},
        "lagna": {"sign": lagna, "lord": lagna_lord},
        "dasha": {"lord": dasha_lord, "years": current_dasha_years},
        "yogas": yogas,
        "ayanamsa": round(ayanamsa, 2),
    }


def _calculate_harmony(bazi: Dict, western: Dict, vedic: Dict) -> Dict[str, Any]:
    """Calculate harmony/consistency between the 3 systems."""
    harmony = {}

    # 1. Element harmony: map 4 Western elements to 5 Chinese elements
    # Fire=Fire, Earth=Earth, Metal~Air (both structural), Water=Water, Wood~Air (growth)
    western_to_wuxing = {"Fire": "Fire", "Earth": "Earth", "Air": "Metal", "Water": "Water"}
    # For Wood: if western has strong Air or Fire, map partially to Wood

    bazi_dominant = max(bazi["element_counts"], key=bazi["element_counts"].get)
    western_dominant = western["dominant_element"]
    mapped_western = western_to_wuxing.get(western_dominant, "Earth")

    element_match = 0
    if bazi_dominant == mapped_western:
        element_match = 100
    elif ELEMENT_PRODUCES.get(bazi_dominant) == mapped_western or ELEMENT_PRODUCES.get(mapped_western) == bazi_dominant:
        element_match = 75
    elif bazi_dominant in ["Wood", "Fire", "Earth", "Metal", "Water"] and mapped_western in ["Wood", "Fire", "Earth", "Metal", "Water"]:
        element_match = 60

    harmony["element_alignment"] = {
        "bazi_dominant": bazi_dominant,
        "western_dominant": western_dominant,
        "mapped_western_to_wuxing": mapped_western,
        "score": element_match,
        "interpretation": _element_harmony_text(element_match),
    }

    # 2. Sun/Moon harmony between Western and Vedic
    western_sun = western["sun_sign"]["sign"]
    vedic_sun = vedic["sun_rashi"]["sign"]
    western_moon = western["moon_sign"]["sign"]
    vedic_moon = vedic["moon_rashi"]["sign"]

    # Vedic moon sign is usually ~1 sign before western due to ayanamsa
    sun_shift = _zodiac_distance(western_sun, vedic_sun)
    moon_shift = _zodiac_distance(western_moon, vedic_moon)

    cross_system_match = 0
    if sun_shift == moon_shift:
        cross_system_match = 90
    elif abs(sun_shift - moon_shift) <= 1:
        cross_system_match = 70
    else:
        cross_system_match = 50

    harmony["cross_system_consistency"] = {
        "western_sun": western_sun,
        "vedic_sun": vedic_sun,
        "western_moon": western_moon,
        "vedic_moon": vedic_moon,
        "sun_shift_signs": sun_shift,
        "moon_shift_signs": moon_shift,
        "score": cross_system_match,
        "interpretation": _consistency_text(cross_system_match),
    }

    # 3. Day Master vs Vedic Lagna
    bazi_day_master_element = bazi["day_master"]["element"]
    vedic_lagna = vedic["lagna"]["sign"]
    vedic_lagna_lord = vedic["lagna"]["lord"]
    vedic_lagna_elem = _vedic_sign_element(vedic_lagna)

    daymaster_lagna_match = 0
    if bazi_day_master_element == vedic_lagna_elem:
        daymaster_lagna_match = 95
    elif ELEMENT_PRODUCES.get(bazi_day_master_element) == vedic_lagna_elem:
        daymaster_lagna_match = 80
    else:
        daymaster_lagna_match = 60

    harmony["daymaster_lagna"] = {
        "bazi_day_master": bazi["day_master"]["stem"],
        "bazi_day_master_element": bazi_day_master_element,
        "vedic_lagna": vedic_lagna,
        "vedic_lagna_lord": vedic_lagna_lord,
        "vedic_lagna_element": vedic_lagna_elem,
        "score": daymaster_lagna_match,
        "interpretation": _daymaster_text(daymaster_lagna_match),
    }

    # 4. Overall harmony score
    overall = round((element_match + cross_system_match + daymaster_lagna_match) / 3)
    harmony["overall_harmony"] = {
        "score": overall,
        "level": _harmony_level(overall),
        "summary": _overall_summary(overall, bazi_dominant, western_dominant, vedic_moon),
    }

    return harmony


def _zodiac_distance(sign_a: str, sign_b: str) -> int:
    """Return distance in zodiac signs between two signs."""
    names = [s[0] for s in WESTERN_SIGNS]
    try:
        idx_a = names.index(sign_a)
        idx_b = names.index(sign_b)
    except ValueError:
        return 0
    return ((idx_a - idx_b) % 12)


def _vedic_sign_element(sign: str) -> str:
    """Map Vedic sign to Chinese 5-element."""
    # Fire signs: Mesha, Simha, Dhanu
    # Earth: Vrishabha, Kanya, Makara
    # Air: Mithuna, Tula, Kumbha
    # Water: Karka, Vrishchika, Meena
    fire = ["Mesha", "Simha", "Dhanu"]
    earth = ["Vrishabha", "Kanya", "Makara"]
    air = ["Mithuna", "Tula", "Kumbha"]
    water = ["Karka", "Vrishchika", "Meena"]
    if sign in fire:
        return "Fire"
    if sign in earth:
        return "Earth"
    if sign in air:
        return "Metal"  # Air ~ Metal in Chinese mapping
    if sign in water:
        return "Water"
    return "Earth"


def _element_harmony_text(score: int) -> str:
    if score >= 90:
        return "ธาตุหลักของ Bazi และ Western สอดคล้องกันอย่างมาก — พลังงานสอดประสาน"
    if score >= 75:
        return "ธาตุหลักสนับสนุนกัน (สร้าง/ให้กำเนิด) — แนวโน้มดี"
    if score >= 50:
        return "ธาตุหลักปานกลาง ไม่ช่วยไม่ขัด — ต้องพึงปัจจัยอื่นเสริม"
    return "ธาตุหลักขัดแย้งกัน — อาจมีความขัดแย้งภายใน"


def _consistency_text(score: int) -> str:
    if score >= 90:
        return "Western และ Vedic มีความสอดคล้องสูง — การคำนวณและอิทธิพลดวงชะตาแนวโน้มเดียวกัน"
    if score >= 70:
        return "ระบบสากลและอินเดียมีแนวโน้มคล้ายกัน — ลักษณะเด่นตรงกันโดยมาก"
    return "มีความแตกต่างระหว่างระบบสากลและอินเดีย — ต้องพิจารณาบริบทแยกตามแต่ละระบบ"


def _daymaster_text(score: int) -> str:
    if score >= 90:
        return "Day Master (Bazi) และ Lagna (Vedic) สอดคล้องกันมาก — อัตลักษณ์แก่นจริงชัดเจน"
    if score >= 75:
        return "Day Master ได้รับการสนับสนุนจาก Lagna — ศักยภาพพัฒนาได้"
    return "Day Master และ Lagna มีแนวโน้มต่างกัน — อาจมีความสับสนในการเลือกเส้นทาง"


def _harmony_level(score: int) -> str:
    if score >= 80:
        return "สูงมาก (Excellent)"
    if score >= 65:
        return "สูง (Good)"
    if score >= 50:
        return "ปานกลาง (Moderate)"
    if score >= 35:
        return "ต่ำ (Challenging)"
    return "ต่ำมาก (Difficult)"


# --- Thai Term Mappings ---
ELEMENT_TH = {"Wood": "ไม้", "Fire": "ไฟ", "Earth": "ดิน", "Metal": "ทอง", "Water": "น้ำ"}
ZODIAC_TH = {
    "Aries": "เมษ", "Taurus": "พฤษภ", "Gemini": "เมถุน", "Cancer": "กรกฎ",
    "Leo": "สิงห์", "Virgo": "กันย์", "Libra": "ตุล", "Scorpio": "พิจิก",
    "Sagittarius": "ธนู", "Capricorn": "มังกร", "Aquarius": "กุมภ์", "Pisces": "มีน",
    "Mesha": "เมษ", "Vrishabha": "พฤษภ", "Mithuna": "เมถุน", "Karka": "กรกฎ",
    "Simha": "สิงห์", "Kanya": "กันย์", "Tula": "ตุล", "Vrishchika": "พิจิก",
    "Dhanu": "ธนู", "Makara": "มังกร", "Kumbha": "กุมภ์", "Meena": "มีน"
}

def _overall_summary(score: int, bazi_elem: str, western_elem: str, vedic_moon: str) -> str:
    b_th = ELEMENT_TH.get(bazi_elem, bazi_elem)
    w_th = ELEMENT_TH.get(western_elem, western_elem)
    
    analysis = ""
    if bazi_elem == western_elem:
        analysis = f"พลังของธาตุ{b_th}หนุนเสริมกันทั้งภายในและภายนอก ทำให้เป็นคนที่มีจุดยืนชัดเจนและมีพลังขับเคลื่อนสูง"
    elif score >= 80:
        analysis = f"ธาตุภายใน ({b_th}) ส่งเสริมธาตุภายนอก ({w_th}) เปรียบเหมือนมีแรงผลักดันจากพรสวรรค์ดั้งเดิมสู่ความสำเร็จ"
    else:
        analysis = f"แม้ธาตุหลัก ({b_th} และ {w_th}) จะต่างกัน แต่ก็นำมาซึ่งความหลากหลายในทักษะและการรับมือกับอุปสรรค"

    if score >= 80:
        return f"ดวงชะตา 3 ระบบสอดคล้องกันดีเยี่ยม — {analysis} ส่งผลให้ชีวิตมีแนวโน้มราบรื่นและมีศักยภาพที่โดดเด่นชัดเจน"
    if score >= 65:
        return f"ดวงชะตา 3 ระบบมีจุดร่วมที่ดี — {analysis} หากพึ่งพาความพยายามและความรอบคอบจะประสบความสำเร็จได้มั่นคง"
    return f"ดวงชะตา 3 ระบบมีความซับซ้อน — พลังงานที่แตกต่างกันทำให้มักมีความลังเลหรือต้องใช้เวลาค้นหาตัวเองนานกว่าปกติ แต่หากสมดุลได้จะเป็นผู้ที่มีมิติทางความคิดลึกซึ้ง"


# =============================================================================
# Synastry / Couple Compatibility Analysis
# =============================================================================

# --- Chinese Zodiac compatibility (六合 Liu He / 三合 San He) ---
# 6 harmonies: Rat-Ox, Tiger-Pig, Rabbit-Dog, Dragon-Rooster, Snake-Monkey, Horse-Goat
# 3 harmonies: Monkey-Rat-Dragon, Ox-Snake-Rooster, Tiger-Horse-Dog, Rabbit-Goat-Pig
LIU_HE_PAIRS = {
    0: 1, 1: 0,   # Rat <-> Ox
    2: 11, 11: 2, # Tiger <-> Pig
    3: 10, 10: 3, # Rabbit <-> Dog
    4: 9, 9: 4,   # Dragon <-> Rooster
    5: 8, 8: 5,   # Snake <-> Monkey
    6: 7, 7: 6,   # Horse <-> Goat
}
SAN_HE_GROUPS = [
    [0, 4, 8],    # Monkey-Rat-Dragon
    [1, 5, 9],    # Ox-Snake-Rooster
    [2, 6, 10],   # Tiger-Horse-Dog
    [3, 7, 11],   # Rabbit-Goat-Pig
]

# --- Western sign element affinity ---
WESTERN_ELEMENT_AFFINITY = {
    "Fire": {"Fire": 90, "Air": 85, "Earth": 60, "Water": 50},
    "Earth": {"Earth": 90, "Water": 85, "Fire": 60, "Air": 50},
    "Air": {"Air": 90, "Fire": 85, "Water": 60, "Earth": 50},
    "Water": {"Water": 90, "Earth": 85, "Air": 60, "Fire": 50},
}

# --- Vedic Kuta scoring (simplified) ---
# Based on Moon Rashi lord compatibility
VEDIC_RASHI_AFFINITY = {
    "Mars": {"Mars": 70, "Sun": 75, "Moon": 60, "Mercury": 50, "Jupiter": 80, "Venus": 65, "Saturn": 45},
    "Venus": {"Venus": 75, "Saturn": 70, "Mercury": 80, "Jupiter": 65, "Mars": 55, "Sun": 60, "Moon": 70},
    "Mercury": {"Mercury": 80, "Venus": 80, "Sun": 75, "Moon": 65, "Mars": 50, "Jupiter": 70, "Saturn": 60},
    "Moon": {"Moon": 80, "Sun": 85, "Jupiter": 75, "Mars": 55, "Venus": 70, "Mercury": 65, "Saturn": 50},
    "Sun": {"Sun": 80, "Jupiter": 85, "Mars": 70, "Mercury": 75, "Venus": 60, "Saturn": 50, "Moon": 65},
    "Jupiter": {"Jupiter": 85, "Sun": 85, "Moon": 75, "Venus": 65, "Mercury": 70, "Mars": 60, "Saturn": 55},
    "Saturn": {"Saturn": 65, "Mercury": 60, "Venus": 70, "Jupiter": 55, "Sun": 50, "Mars": 45, "Moon": 50},
}

# --- Nakshatra compatibility (simplified: same lord = good, complementary = better) ---
NAKSHATRA_COMPAT = {
    "Ketu": {"Ketu": 70, "Venus": 60, "Sun": 55, "Moon": 65, "Mars": 75, "Rahu": 50, "Jupiter": 60, "Saturn": 55, "Mercury": 65},
    "Venus": {"Venus": 80, "Sun": 75, "Moon": 70, "Mars": 60, "Rahu": 55, "Jupiter": 65, "Saturn": 70, "Mercury": 75, "Ketu": 60},
    "Sun": {"Sun": 75, "Moon": 85, "Mars": 70, "Mercury": 80, "Jupiter": 85, "Venus": 75, "Saturn": 50, "Rahu": 45, "Ketu": 55},
    "Moon": {"Moon": 80, "Sun": 85, "Mercury": 70, "Jupiter": 75, "Venus": 70, "Mars": 60, "Saturn": 55, "Rahu": 50, "Ketu": 65},
    "Mars": {"Mars": 75, "Sun": 70, "Moon": 60, "Mercury": 55, "Jupiter": 65, "Venus": 60, "Saturn": 45, "Rahu": 70, "Ketu": 75},
    "Rahu": {"Rahu": 55, "Sun": 45, "Moon": 50, "Mercury": 60, "Jupiter": 65, "Venus": 55, "Mars": 70, "Saturn": 50, "Ketu": 50},
    "Jupiter": {"Jupiter": 85, "Sun": 85, "Moon": 75, "Mercury": 70, "Venus": 65, "Mars": 65, "Saturn": 55, "Rahu": 65, "Ketu": 60},
    "Saturn": {"Saturn": 65, "Sun": 50, "Moon": 55, "Mercury": 60, "Jupiter": 55, "Venus": 70, "Mars": 45, "Rahu": 50, "Ketu": 55},
    "Mercury": {"Mercury": 80, "Sun": 75, "Moon": 65, "Venus": 75, "Jupiter": 70, "Mars": 55, "Saturn": 60, "Rahu": 60, "Ketu": 65},
}


def _calculate_bazi_compatibility(bazi1: Dict, bazi2: Dict) -> Dict[str, Any]:
    """Compare two Bazi charts for couple compatibility."""
    # 1. Day Master element relation
    dm1_elem = bazi1["day_master"]["element"]
    dm2_elem = bazi2["day_master"]["element"]
    dm1_yinyang = bazi1["day_master"]["yinyang"]
    dm2_yinyang = bazi2["day_master"]["yinyang"]

    dm_relation = 50
    relation_text = "ปานกลาง"
    if dm1_elem == dm2_elem:
        if dm1_yinyang != dm2_yinyang:
            dm_relation = 85
            relation_text = "สนับสนุน (Yin-Yang คู่กันในธาตุเดียวกัน)"
        else:
            dm_relation = 60
            relation_text = "เหมือนกัน (อาจแข่งกันหรือเข้าใจกันลึก)"
    elif ELEMENT_PRODUCES.get(dm1_elem) == dm2_elem:
        dm_relation = 90
        relation_text = f"{dm1_elem} ให้กำเนิด {dm2_elem} — ผู้หนึ่งสนับสนุนอีกผู้หนึ่ง"
    elif ELEMENT_PRODUCES.get(dm2_elem) == dm1_elem:
        dm_relation = 90
        relation_text = f"{dm2_elem} ให้กำเนิด {dm1_elem} — ผู้หนึ่งสนับสนุนอีกผู้หนึ่ง"
    elif ELEMENT_OVERCOMES.get(dm1_elem) == dm2_elem:
        dm_relation = 40
        relation_text = f"{dm1_elem} ควบคุม {dm2_elem} — อาจมีอำนาจเหนือกัน"
    elif ELEMENT_OVERCOMES.get(dm2_elem) == dm1_elem:
        dm_relation = 40
        relation_text = f"{dm2_elem} ควบคุม {dm1_elem} — อาจมีอำนาจเหนือกัน"

    # 2. Year branch (animal) compatibility
    year1_idx = BRANCH_ANIMALS.index(bazi1["pillars"]["year"]["animal"])
    year2_idx = BRANCH_ANIMALS.index(bazi2["pillars"]["year"]["animal"])
    year_compat = 50
    year_text = "ปานกลาง"
    if LIU_HE_PAIRS.get(year1_idx) == year2_idx:
        year_compat = 95
        year_text = "六合 (หลิวเฮอ) — คู่กันมาก"
    elif any(year1_idx in g and year2_idx in g for g in SAN_HE_GROUPS):
        year_compat = 85
        year_text = "三合 (ซานเฮอ) — กลุ่มมิตรที่เข้ากันได้"
    elif abs(year1_idx - year2_idx) == 6:
        year_compat = 35
        year_text = "冲 (ชง) — ขัดแย้ง ต้องปรับตัวมาก"

    # 3. Overall element balance between charts
    combined_elements = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    for elem, count in bazi1["element_counts"].items():
        combined_elements[elem] += count
    for elem, count in bazi2["element_counts"].items():
        combined_elements[elem] += count
    total = sum(combined_elements.values())
    max_elem = max(combined_elements, key=combined_elements.get)
    min_elem = min(combined_elements, key=combined_elements.get)
    balance_score = 100 - (combined_elements[max_elem] - combined_elements[min_elem]) * 5
    balance_score = max(0, min(100, balance_score))

    overall = round((dm_relation * 0.5) + (year_compat * 0.3) + (balance_score * 0.2))

    return {
        "day_master_relation": {
            "person1": f"{bazi1['day_master']['stem']} ({dm1_elem}/{dm1_yinyang})",
            "person2": f"{bazi2['day_master']['stem']} ({dm2_elem}/{dm2_yinyang})",
            "score": dm_relation,
            "interpretation": relation_text,
        },
        "year_animal_compatibility": {
            "person1": bazi1["pillars"]["year"]["animal"],
            "person2": bazi2["pillars"]["year"]["animal"],
            "score": year_compat,
            "interpretation": year_text,
        },
        "combined_element_balance": {
            "counts": combined_elements,
            "score": balance_score,
            "interpretation": f"ธาตุรวมเด่นที่ {max_elem} ({combined_elements[max_elem]}/{total}) — {'สมดุลดี' if balance_score >= 70 else 'ต้องเสริมธาตุอื่น'}",
        },
        "bazi_compatibility_score": overall,
        "bazi_level": _synastry_level(overall),
    }


def _calculate_western_synastry(western1: Dict, western2: Dict) -> Dict[str, Any]:
    """Compare two Western charts for couple compatibility."""
    # 1. Sun-Sun compatibility (core identity)
    sun1 = western1["sun_sign"]["element"]
    sun2 = western2["sun_sign"]["element"]
    sun_sun = WESTERN_ELEMENT_AFFINITY.get(sun1, {}).get(sun2, 50)

    # 2. Sun-Moon cross (emotional understanding)
    sun1_moon2 = WESTERN_ELEMENT_AFFINITY.get(sun1, {}).get(western2["moon_sign"]["element"], 50)
    sun2_moon1 = WESTERN_ELEMENT_AFFINITY.get(sun2, {}).get(western1["moon_sign"]["element"], 50)
    sun_moon = round((sun1_moon2 + sun2_moon1) / 2)

    # 3. Moon-Moon (emotional harmony)
    moon1 = western1["moon_sign"]["element"]
    moon2 = western2["moon_sign"]["element"]
    moon_moon = WESTERN_ELEMENT_AFFINITY.get(moon1, {}).get(moon2, 50)

    # 4. Ascendant-Ascendant (outer personality)
    asc1 = western1["ascendant"]["element"]
    asc2 = western2["ascendant"]["element"]
    asc_asc = WESTERN_ELEMENT_AFFINITY.get(asc1, {}).get(asc2, 50)

    # 5. Dominant element harmony
    dom1 = western1["dominant_element"]
    dom2 = western2["dominant_element"]
    dom_dom = WESTERN_ELEMENT_AFFINITY.get(dom1, {}).get(dom2, 50)

    overall = round((sun_sun * 0.25) + (sun_moon * 0.25) + (moon_moon * 0.20) + (asc_asc * 0.15) + (dom_dom * 0.15))

    return {
        "sun_sun": {"score": sun_sun, "text": f"{western1['sun_sign']['sign']} + {western2['sun_sign']['sign']}"},
        "sun_moon_cross": {"score": sun_moon, "text": f"Sun-Moon สลับกัน"},
        "moon_moon": {"score": moon_moon, "text": f"{western1['moon_sign']['sign']} + {western2['moon_sign']['sign']}"},
        "ascendant_ascendant": {"score": asc_asc, "text": f"{western1['ascendant']['sign']} + {western2['ascendant']['sign']}"},
        "dominant_dominant": {"score": dom_dom, "text": f"ธาตุหลัก {dom1} + {dom2}"},
        "western_compatibility_score": overall,
        "western_level": _synastry_level(overall),
    }


def _calculate_vedic_synastry(vedic1: Dict, vedic2: Dict) -> Dict[str, Any]:
    """Compare two Vedic charts for couple compatibility (Kuta simplified)."""
    # 1. Moon Rashi lord compatibility
    lord1 = vedic1["moon_rashi"]["lord"]
    lord2 = vedic2["moon_rashi"]["lord"]
    rashi_compat = VEDIC_RASHI_AFFINITY.get(lord1, {}).get(lord2, 50)

    # 2. Nakshatra lord compatibility
    nak_lord1 = vedic1["nakshatra"]["lord"]
    nak_lord2 = vedic2["nakshatra"]["lord"]
    nak_compat = NAKSHATRA_COMPAT.get(nak_lord1, {}).get(nak_lord2, 50)

    # 3. Lagna lord compatibility
    lagna_lord1 = vedic1["lagna"]["lord"]
    lagna_lord2 = vedic2["lagna"]["lord"]
    lagna_compat = VEDIC_RASHI_AFFINITY.get(lagna_lord1, {}).get(lagna_lord2, 50)

    # 4. Dasha lord overlap (if same period lord = challenges, complementary = good)
    dasha1 = vedic1["dasha"]["lord"]
    dasha2 = vedic2["dasha"]["lord"]
    if dasha1 == dasha2:
        dasha_compat = 55
        dasha_text = f"Dasha เหมือนกัน ({dasha1}) — อาจเผชิญช่วงเวลาคล้ายกัน"
    else:
        dasha_compat = 75
        dasha_text = f"Dasha ต่างกัน ({dasha1} vs {dasha2}) — เสริมกัน"

    overall = round((rashi_compat * 0.35) + (nak_compat * 0.35) + (lagna_compat * 0.20) + (dasha_compat * 0.10))

    return {
        "moon_rashi_lords": {"score": rashi_compat, "text": f"{vedic1['moon_rashi']['sign']} ({lord1}) + {vedic2['moon_rashi']['sign']} ({lord2})"},
        "nakshatra_lords": {"score": nak_compat, "text": f"{vedic1['nakshatra']['name']} ({nak_lord1}) + {vedic2['nakshatra']['name']} ({nak_lord2})"},
        "lagna_lords": {"score": lagna_compat, "text": f"{vedic1['lagna']['sign']} ({lagna_lord1}) + {vedic2['lagna']['sign']} ({lagna_lord2})"},
        "dasha_overlap": {"score": dasha_compat, "text": dasha_text},
        "vedic_compatibility_score": overall,
        "vedic_level": _synastry_level(overall),
    }


def _calculate_synastry(bazi1, western1, vedic1, bazi2, western2, vedic2):
    """Calculate overall synastry between two people across 3 systems."""
    bazi_compat = _calculate_bazi_compatibility(bazi1, bazi2)
    western_compat = _calculate_western_synastry(western1, western2)
    vedic_compat = _calculate_vedic_synastry(vedic1, vedic2)

    # Weighted overall: Bazi 40%, Western 30%, Vedic 30%
    overall_score = round(
        bazi_compat["bazi_compatibility_score"] * 0.40 +
        western_compat["western_compatibility_score"] * 0.30 +
        vedic_compat["vedic_compatibility_score"] * 0.30
    )

    return {
        "bazi": bazi_compat,
        "western": western_compat,
        "vedic": vedic_compat,
        "overall_score": overall_score,
        "overall_level": _synastry_level(overall_score),
        "overall_interpretation": _synastry_summary(overall_score, bazi_compat, western_compat, vedic_compat),
    }


def _synastry_level(score: int) -> str:
    if score >= 80:
        return "สูงมาก (Excellent Match)"
    if score >= 65:
        return "สูง (Good Match)"
    if score >= 50:
        return "ปานกลาง (Moderate)"
    if score >= 35:
        return "ต่ำ (Challenging)"
    return "ต่ำมาก (Difficult)"


def _synastry_summary(score: int, bazi: Dict, western: Dict, vedic: Dict) -> str:
    bazi_dm = bazi["day_master_relation"]["interpretation"]
    western_core = western["sun_sun"]["text"]
    vedic_nak = vedic["nakshatra_lords"]["text"]

    if score >= 80:
        return f"ดวงคู่สอดคล้องกันดีมาก — Bazi: {bazi_dm} | Western Sun: {western_core} | Vedic Nakshatra: {vedic_nak} — ความสัมพันธ์มีแนวโน้มยาวนานและสนับสนุนกัน"
    if score >= 65:
        return f"ดวงคู่มีแนวโน้มเข้ากันได้ — Bazi: {bazi_dm} | Western: {western_core} | Vedic: {vedic_nak} — ต้องใช้ความเข้าใจและการปรับตัวบ้าง แต่มีพื้นฐานที่ดี"
    if score >= 50:
        return f"ดวงคู่ปานกลาง — Bazi: {bazi_dm} | Western: {western_core} | Vedic: {vedic_nak} — มีทั้งจุดเด่นและจุดท้าทาย ต้องเรียนรู้กันและกัน"
    return f"ดวงคู่มีความท้าทาย — Bazi: {bazi_dm} | Western: {western_core} | Vedic: {vedic_nak} — อาจต้องใช้ความพยายามและความอดทนสูง แต่หากผ่านไปได้จะเข้าใจกันลึกซึ้ง"


# --- Thai date helpers ---
THAI_MONTHS = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]


def _thai_date_str(dt: datetime) -> str:
    return f"{dt.day} {THAI_MONTHS[dt.month - 1]} {dt.year + 543}"


from src.tools.fact_retriever import tool_fact_retriever as rag_call

def _get_sinsae_meaning(query: str) -> str:
    res = rag_call(query=query)
    if res.get("success"):
        return res.get("answer", "")
    return ""

def _generate_sinsae_reading(summary: Dict) -> str:
    """Combine all data into a cohesive professional Sin-sae consultation."""
    p1 = summary.get("person1", {})
    bazi = p1.get("bazi", {})
    western = p1.get("western", {})
    vedic = p1.get("vedic", {})
    harmony = p1.get("harmony", {}).get("overall_harmony", {})
    
    dm = bazi.get("day_master", {}).get("stem", "")
    dm_elem = bazi.get("day_master", {}).get("element", "")
    sun = western.get("sun_sign", {}).get("sign", "")
    nak = vedic.get("nakshatra", {}).get("name", "")
    
    # Fetch meanings from KB
    dm_meaning = _get_sinsae_meaning(f"Day Master {dm}")
    sun_meaning = _get_sinsae_meaning(f"ราศี {sun}")
    nak_meaning = _get_sinsae_meaning(f"Nakshatra {nak}")
    
    reading = f"--- 📜 บทวิเคราะห์ดวงชะตาโดยซินแซ WorAI ---\n\n"
    reading += f"✨ วิเคราะห์พื้นฐานดวงชะตา: {summary['input']['thai_date']}\n"
    reading += f"ระดับความสอดคล้องของชีวิต (Harmony): {harmony.get('level', 'ปานกลาง')} ({harmony.get('score', 0)}%)\n\n"
    
    reading += f"☯️ [ภาคจีน - โป๊ยหยี่สี่เถียว]\n"
    reading += f"ตัวตนหลัก (Day Master) คือ {dm} (ธาตุ{ELEMENT_TH.get(dm_elem)}หยาง)\n"
    if dm_meaning: 
        reading += f"วิเคราะห์ลึก: {dm_meaning}\n"
    
    # Analyze Element Balance
    e_counts = bazi['element_counts']
    reading += f"สมดุลธาตุในดวง: ทอง({e_counts.get('Metal',0)}) ไฟ({e_counts.get('Fire',0)}) ดิน({e_counts.get('Earth',0)}) น้ำ({e_counts.get('Water',0)}) ไม้({e_counts.get('Wood',0)})\n"
    if e_counts.get('Wood', 0) == 0:
        reading += f"⚠️ ข้อสังเกต: ในดวงขาด 'ธาตุไม้' (ความคิดสร้างสรรค์/ความเมตตา) ควรเสริมด้วยการปลูกต้นไม้หรือทำงานศิลปะ\n"
    reading += "\n"
    
    reading += f"☀️ [ภาคสากล - Western Astrology]\n"
    reading += f"ชาวราศี {ZODIAC_TH.get(sun)} (ธาตุ {ELEMENT_TH.get(western['sun_sign']['element'])})\n"
    if sun_meaning: 
        reading += f"บุคลิกภาพ: {sun_meaning}\n"
    reading += f"ลัคนา (ตัวตนภายนอก): {ZODIAC_TH.get(western['ascendant']['sign'], western['ascendant']['sign'])}\n\n"
    
    reading += f"🌙 [ภาคอินเดีย - Vedic / Nakshatra]\n"
    reading += f"ดวงจันทร์สถิตนักษัตร {nak} (Nakshatra)\n"
    if nak_meaning: 
        reading += f"อิทธิพลจิตใต้สำนึก: {nak_meaning}\n"
    reading += f"ดวงเมืองเกิด (Lagna): {ZODIAC_TH.get(vedic['lagna']['sign'], vedic['lagna']['sign'])}\n\n"
    
    reading += f"💡 [บทสรุปและคำแนะนำจากซินแซ]\n"
    reading += f"{harmony.get('summary', 'ชีวิตมีทางเดินที่หลากหลาย จงใช้สติเป็นที่ตั้ง')}\n"
    reading += f"\n--- ขอให้โชคดีและรุ่งเรืองครับ ---"
    
    return reading

def _parse_birth_input(birth_date: str, birth_time: str, birth_place: str) -> tuple:
    """Helper to parse birth date/time and geocode. Returns (dt, hour, minute, lat, lon)."""
    try:
        dt = datetime.strptime(birth_date, "%Y-%m-%d")
        if dt.year > 2500:
            dt = dt.replace(year=dt.year - 543)
    except ValueError:
        raise ValueError("Invalid birth_date format. Use YYYY-MM-DD or Buddhist year (e.g. 2530-05-15)")

    try:
        t = datetime.strptime(birth_time, "%H:%M")
        hour, minute = t.hour, t.minute
    except ValueError:
        raise ValueError("Invalid birth_time format. Use HH:MM (24-hour)")

    lat, lon = 13.7563, 100.5018
    if "เชียงใหม่" in birth_place or "Chiang Mai" in birth_place:
        lat, lon = 18.7883, 98.9853
    elif "ภูเก็ต" in birth_place or "Phuket" in birth_place:
        lat, lon = 7.8804, 98.3923

    return dt, hour, minute, lat, lon


def tool_astrology_analyzer(
    birth_date: str = "",
    birth_time: str = "",
    birth_place: str = "กรุงเทพมหานคร",
    gender: str = "",
    raw_text: str = "",
    partner_date: str = "",
    partner_time: str = "",
    partner_place: str = "กรุงเทพมหานคร",
    partner_gender: str = "",
    partner_raw_text: str = "",
    **kwargs
) -> Dict[str, Any]:
    """Analyze birth chart using Bazi, Western, and Vedic astrology."""
    
    # 1. Parsing with priority: raw_text extraction if parameters look like junk
    # If parameters were assigned the whole sentence, reset them
    if birth_date and len(birth_date) > 15: birth_date = ""
    if birth_time and len(birth_time) > 15: birth_time = ""

    if raw_text and not birth_date:
        date_match = re.search(r'(\d{1,4})[-/](\d{1,2})[-/](\d{1,4})', raw_text)
        if date_match:
            g1, g2, g3 = date_match.groups()
            if len(g1) == 4: y, m, d = int(g1), int(g2), int(g3)
            else: d, m, y = int(g1), int(g2), int(g3)
            if y > 2400: y -= 543
            birth_date = f"{y:04d}-{m:02d}-{d:02d}"

    if raw_text and not birth_time:
        time_match = re.search(r'(\d{1,2})[:.](\d{2})', raw_text)
        if time_match:
            birth_time = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"

    # 2. Validation
    if not birth_date or not re.match(r'^\d{4}-\d{2}-\d{2}$', birth_date):
        return {"success": False, "error": "กรุณาระบุวันเดือนปีเกิด (เช่น 15/05/2530) เพื่อเริ่มการวิเคราะห์ครับ"}
    if not birth_time:
        birth_time = "12:00"

    # 3. Calculate person 1
    try:
        dt1, hour1, minute1, lat1, lon1 = _parse_birth_input(birth_date, birth_time, birth_place)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    bazi1 = _calculate_bazi(dt1.year, dt1.month, dt1.day, hour1, minute1)
    western1 = _calculate_western(dt1.year, dt1.month, dt1.day, hour1, minute1, lat1, lon1)
    vedic1 = _calculate_vedic(dt1.year, dt1.month, dt1.day, hour1, minute1, lat1, lon1)
    harmony1 = _calculate_harmony(bazi1, western1, vedic1)

    summary = {
        "person1": {
            "bazi": {
                "title": "八字 Bazi (จีน)",
                "day_master": bazi1["day_master"],
                "pillars": bazi1["pillars"],
                "element_counts": bazi1["element_counts"],
                "yinyang_balance": bazi1["yinyang_balance"],
                "luck_cycles": bazi1["luck_cycles"][:3],
                "hidden_stems": bazi1["hidden_stems"],
            },
            "western": {
                "title": "Western Astrology (สากล)",
                "sun_sign": western1["sun_sign"],
                "moon_sign": western1["moon_sign"],
                "ascendant": western1["ascendant"],
                "dominant_element": western1["dominant_element"],
                "element_balance": western1["element_balance"],
                "houses": western1["houses"][:4],
            },
            "vedic": {
                "title": "Vedic Astrology / Jyotish (อินเดีย)",
                "moon_rashi": vedic1["moon_rashi"],
                "sun_rashi": vedic1["sun_rashi"],
                "nakshatra": vedic1["nakshatra"],
                "lagna": vedic1["lagna"],
                "dasha": vedic1["dasha"],
                "yogas": vedic1["yogas"],
            },
            "harmony": harmony1,
        },
        "input": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_place": birth_place,
            "gender": gender,
            "thai_date": _thai_date_str(dt1),
        },
    }

    # 4. Synastry mode
    if partner_date or partner_raw_text:
        # (Synastry logic remains same but ensuring correct params)
        p_date = partner_date
        p_time = partner_time
        if partner_raw_text and not p_date:
            date_match = re.search(r'(\d{4})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{1,2})', partner_raw_text)
            if date_match:
                y, m, d = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                if y > 2400: y -= 543
                p_date = f"{y:04d}-{m:02d}-{d:02d}"
            time_match = re.search(r'(\d{1,2})[:.](\d{2})', partner_raw_text)
            if time_match:
                p_time = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"

        if p_date and re.match(r'^\d{4}-\d{2}-\d{2}$', p_date):
            if not p_time: p_time = "12:00"
            try:
                dt2, hour2, minute2, lat2, lon2 = _parse_birth_input(p_date, p_time, partner_place)
                bazi2 = _calculate_bazi(dt2.year, dt2.month, dt2.day, hour2, minute2)
                western2 = _calculate_western(dt2.year, dt2.month, dt2.day, hour2, minute2, lat2, lon2)
                vedic2 = _calculate_vedic(dt2.year, dt2.month, dt2.day, hour2, minute2, lat2, lon2)
                synastry = _calculate_synastry(bazi1, western1, vedic1, bazi2, western2, vedic2)
                
                summary["person2"] = {
                    "bazi": bazi2["day_master"], # Simplified for person2
                    "western": western2["sun_sign"],
                    "vedic": vedic2["moon_rashi"],
                }
                summary["synastry"] = synastry
            except: pass

    # 5. Generate Sinsae Reading (NEW!)
    summary["sinsae_reading"] = _generate_sinsae_reading(summary)

    return {"success": True, **summary}
