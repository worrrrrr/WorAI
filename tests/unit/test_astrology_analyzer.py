import pytest
from src.tools.astrology_analyzer import (
    tool_astrology_analyzer,
    _calculate_bazi, _calculate_western, _calculate_vedic,
    _calculate_harmony, _calculate_synastry,
    _zodiac_distance, _element_harmony_text, _harmony_level,
    _calculate_bazi_compatibility, _calculate_western_synastry, _calculate_vedic_synastry,
    _synastry_level,
)


class TestAstrologyAnalyzer:
    """Unit tests for tool_astrology_analyzer."""

    def test_tool_basic_call(self):
        """Basic call with explicit parameters."""
        result = tool_astrology_analyzer(
            birth_date="1987-05-15",
            birth_time="14:30",
            birth_place="Bangkok",
            gender="male",
        )
        assert result["success"] is True
        assert "person1" in result
        assert "bazi" in result["person1"]
        assert "western" in result["person1"]
        assert "vedic" in result["person1"]
        assert "harmony" in result["person1"]
        assert "input" in result
        assert "synastry" not in result  # no partner data = no synastry

    def test_tool_raw_text_parsing(self):
        """Parse date/time from raw Thai text."""
        result = tool_astrology_analyzer(
            raw_text="เกิดวันที่ 15 พฤษภาคม 2530 เวลา 14:30 น. ที่กรุงเทพ",
        )
        assert result["success"] is True
        assert result["input"]["birth_date"] == "1987-05-15"

    def test_tool_buddhist_year(self):
        """Buddhist year should be converted correctly."""
        result = tool_astrology_analyzer(
            birth_date="2530-05-15",
            birth_time="14:30",
        )
        assert result["success"] is True
        assert result["input"]["thai_date"].startswith("15 พฤษภาคม")

    def test_invalid_date_format(self):
        """Invalid date should return error."""
        result = tool_astrology_analyzer(
            birth_date="invalid-date",
            birth_time="14:30",
        )
        assert result["success"] is False
        assert "error" in result

    def test_invalid_time_format(self):
        """Invalid time should return error."""
        result = tool_astrology_analyzer(
            birth_date="1987-05-15",
            birth_time="invalid",
        )
        assert result["success"] is False
        assert "error" in result

    def test_bazi_structure(self):
        """Bazi should contain all four pillars."""
        bazi = _calculate_bazi(1987, 5, 15, 14, 30)
        assert "pillars" in bazi
        assert set(bazi["pillars"].keys()) == {"year", "month", "day", "hour"}
        assert "day_master" in bazi
        assert "element_counts" in bazi
        assert sum(bazi["element_counts"].values()) == 8  # 4 stems + 4 branches
        assert "yinyang_balance" in bazi
        assert bazi["yinyang_balance"]["yin"] + bazi["yinyang_balance"]["yang"] == 8
        assert "luck_cycles" in bazi
        assert len(bazi["luck_cycles"]) >= 8
        assert "hidden_stems" in bazi

    def test_western_structure(self):
        """Western chart should contain key components."""
        western = _calculate_western(1987, 5, 15, 14, 30)
        assert "sun_sign" in western
        assert "moon_sign" in western
        assert "ascendant" in western
        assert "planets" in western
        assert "element_balance" in western
        assert "dominant_element" in western
        assert "houses" in western
        assert len(western["houses"]) == 12
        # Taurus season check
        assert western["sun_sign"]["sign"] == "Taurus"

    def test_vedic_structure(self):
        """Vedic chart should contain key components."""
        vedic = _calculate_vedic(1987, 5, 15, 14, 30)
        assert "sun_rashi" in vedic
        assert "moon_rashi" in vedic
        assert "nakshatra" in vedic
        assert "lagna" in vedic
        assert "dasha" in vedic
        assert "yogas" in vedic
        assert "ayanamsa" in vedic
        assert vedic["ayanamsa"] > 23  # Should be around 24+
        assert 1 <= vedic["nakshatra"]["pada"] <= 4

    def test_harmony_structure(self):
        """Harmony analysis should contain all scores."""
        bazi = _calculate_bazi(1987, 5, 15, 14, 30)
        western = _calculate_western(1987, 5, 15, 14, 30)
        vedic = _calculate_vedic(1987, 5, 15, 14, 30)
        harmony = _calculate_harmony(bazi, western, vedic)
        assert "element_alignment" in harmony
        assert "cross_system_consistency" in harmony
        assert "daymaster_lagna" in harmony
        assert "overall_harmony" in harmony
        overall = harmony["overall_harmony"]["score"]
        assert 0 <= overall <= 100
        assert harmony["overall_harmony"]["level"] in [
            "สูงมาก (Excellent)", "สูง (Good)", "ปานกลาง (Moderate)", "ต่ำ (Challenging)", "ต่ำมาก (Difficult)"
        ]

    def test_zodiac_distance(self):
        """Zodiac distance should be correct."""
        assert _zodiac_distance("Aries", "Taurus") == 11  # Aries(0) - Taurus(1) = -1 -> 11 mod 12
        assert _zodiac_distance("Taurus", "Aries") == 1
        assert _zodiac_distance("Aries", "Aries") == 0

    def test_element_harmony_text(self):
        """Element harmony text should be Thai."""
        assert "สอดคล้อง" in _element_harmony_text(100)
        assert "สนับสนุน" in _element_harmony_text(80)
        assert "ปานกลาง" in _element_harmony_text(50)
        assert "ขัดแย้ง" in _element_harmony_text(30)

    def test_harmony_level(self):
        """Harmony level categories."""
        assert "Excellent" in _harmony_level(85)
        assert "Good" in _harmony_level(70)
        assert "Moderate" in _harmony_level(55)
        assert "Challenging" in _harmony_level(40)
        assert "Difficult" in _harmony_level(20)

    def test_bazi_known_reference(self):
        """Known reference: 1900-01-31 = 甲辰 (stem 0, branch 4)."""
        bazi = _calculate_bazi(1900, 1, 31, 12)
        assert bazi["pillars"]["day"]["stem"] == "甲 Jia"
        assert bazi["pillars"]["day"]["branch"] == "辰 Chen"

    def test_different_locations(self):
        """Different birth places should be accepted."""
        for place in ["Bangkok", "Chiang Mai", "Phuket", "เชียงใหม่", "ภูเก็ต"]:
            result = tool_astrology_analyzer(
                birth_date="1990-01-01",
                birth_time="12:00",
                birth_place=place,
            )
            assert result["success"] is True

    def test_synastry_basic_call(self):
        """Synastry mode with partner data."""
        result = tool_astrology_analyzer(
            birth_date="1987-05-15",
            birth_time="14:30",
            birth_place="Bangkok",
            gender="male",
            partner_date="1990-08-22",
            partner_time="09:00",
            partner_place="Bangkok",
            partner_gender="female",
        )
        assert result["success"] is True
        assert "person1" in result
        assert "person2" in result
        assert "synastry" in result
        syn = result["synastry"]
        assert "overall_score" in syn
        assert "overall_level" in syn
        assert "bazi" in syn
        assert "western" in syn
        assert "vedic" in syn
        assert 0 <= syn["overall_score"] <= 100

    def test_synastry_structure(self):
        """Synastry result should have all sub-scores."""
        bazi1 = _calculate_bazi(1987, 5, 15, 14, 30)
        western1 = _calculate_western(1987, 5, 15, 14, 30)
        vedic1 = _calculate_vedic(1987, 5, 15, 14, 30)
        bazi2 = _calculate_bazi(1990, 8, 22, 9, 0)
        western2 = _calculate_western(1990, 8, 22, 9, 0)
        vedic2 = _calculate_vedic(1990, 8, 22, 9, 0)
        syn = _calculate_synastry(bazi1, western1, vedic1, bazi2, western2, vedic2)
        assert "bazi" in syn
        assert "western" in syn
        assert "vedic" in syn
        assert "overall_score" in syn
        assert "overall_interpretation" in syn
        assert syn["bazi"]["bazi_compatibility_score"] >= 0
        assert syn["western"]["western_compatibility_score"] >= 0
        assert syn["vedic"]["vedic_compatibility_score"] >= 0

    def test_bazi_compatibility_same_element(self):
        """Bazi compat: same element different yin/yang = good."""
        bazi1 = _calculate_bazi(1987, 5, 15, 14, 30)  # 甲 Jia (Yang Wood)
        bazi2 = _calculate_bazi(1987, 5, 16, 10, 0)  # 乙 Yi (Yin Wood)
        compat = _calculate_bazi_compatibility(bazi1, bazi2)
        assert compat["day_master_relation"]["score"] >= 75

    def test_western_synastry_same_element(self):
        """Western synastry: same element sun signs = good."""
        western1 = _calculate_western(1987, 5, 15, 14, 30)  # Taurus (Earth)
        western2 = _calculate_western(1990, 1, 10, 12, 0)   # Capricorn (Earth)
        syn = _calculate_western_synastry(western1, western2)
        assert syn["sun_sun"]["score"] >= 75

    def test_vedic_synastry_structure(self):
        """Vedic synastry should have all components."""
        vedic1 = _calculate_vedic(1987, 5, 15, 14, 30)
        vedic2 = _calculate_vedic(1990, 8, 22, 9, 0)
        syn = _calculate_vedic_synastry(vedic1, vedic2)
        assert "moon_rashi_lords" in syn
        assert "nakshatra_lords" in syn
        assert "lagna_lords" in syn
        assert "dasha_overlap" in syn
        assert syn["vedic_compatibility_score"] >= 0

    def test_synastry_level(self):
        """Synastry level categories."""
        assert "Excellent" in _synastry_level(85)
        assert "Good" in _synastry_level(70)
        assert "Moderate" in _synastry_level(55)
        assert "Challenging" in _synastry_level(40)
        assert "Difficult" in _synastry_level(20)
