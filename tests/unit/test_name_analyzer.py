"""
Unit tests for name_analyzer tool.
"""
import pytest
from src.tools.name_analyzer import tool_name_analyzer, _get_char_value, _reduce_number


class TestNameAnalyzer:
    def test_single_consonant(self):
        result = tool_name_analyzer(name="ก")
        assert result["success"] is True
        assert result["grand_total"] == 1
        assert result["grand_reduction"]["final"] == 1

    def test_single_part_name(self):
        result = tool_name_analyzer(name="สุนทร")
        assert result["success"] is True
        # ส=7, ุ=1, น=5, ท=1, ร=4 → 18
        assert result["grand_total"] == 18
        assert result["grand_reduction"]["final"] == 9  # 1+8=9

    def test_full_name_two_parts(self):
        result = tool_name_analyzer(name="วรกฤช สุนทรธรรมนิติ")
        assert result["success"] is True
        # วร = ว(6)+ร(4) = 10 → 1
        # กฤช = ก(1)+ฤ(1)+ช(2) = 4 → 4
        # สุนทร = ส(7)+ุ(1)+น(5)+ท(1)+ร(4) = 18 → 9
        # ธรรม = ธ(4)+ร(4)+ร(4)+ม(5) = 17 → 8
        # นิติ = น(5)+ิ(4)+ต(3)+ิ(4) = 16 → 7
        assert result["grand_total"] == 65  # 10+4+18+17+16
        assert result["grand_reduction"]["final"] == 2  # 6+5=11→1+1=2

    def test_name_reduction_steps(self):
        reduction = _reduce_number(65)
        assert reduction["original"] == 65
        assert reduction["steps"] == [65, 11, 2]
        assert reduction["final"] == 2

    def test_empty_input(self):
        result = tool_name_analyzer(name="")
        assert result["success"] is False
        assert "ไม่พบชื่อ" in result["error"]

    def test_raw_text_param(self):
        result = tool_name_analyzer(raw_text="สุนทร")
        assert result["success"] is True
        assert result["grand_total"] == 18

    def test_part_breakdown(self):
        result = tool_name_analyzer(name="สุนทร ธรรม")
        parts = result["parts"]
        assert len(parts) == 2
        assert parts[0]["sum"] == 18
        assert parts[1]["sum"] == 17

    def test_english_letters(self):
        result = tool_name_analyzer(name="AB")
        # A=1, B=2
        assert result["grand_total"] == 3

    def test_mixed_thai_english(self):
        result = tool_name_analyzer(name="A ก")
        # A=1, ก=1
        assert result["grand_total"] == 2

    def test_tone_marks(self):
        result = tool_name_analyzer(name="ก่")
        # ก=1, ่=1 → total 2
        assert result["grand_total"] == 2
        assert result["parts"][0]["characters"] == [
            {"char": "ก", "value": 1},
            {"char": "่", "value": 1},
        ]

    def test_unmapped_characters(self):
        result = tool_name_analyzer(name="ก#")
        # ก=1, # is unmapped
        assert result["grand_total"] == 1
        assert "warnings" in result
        assert "#" in result["warnings"]
        assert result["parts"][0]["unmapped_chars"] == ["#"]

    def test_prefix_stripping(self):
        result = tool_name_analyzer(raw_text="วิเคราะห์ วรกฤช")
        assert result["success"] is True
        assert result["full_name"] == "วรกฤช"
        assert result["grand_total"] == 14

    def test_suffix_stripping(self):
        result = tool_name_analyzer(raw_text="วรกฤช หน่อย")
        assert result["success"] is True
        assert result["full_name"] == "วรกฤช"
        assert result["grand_total"] == 14
