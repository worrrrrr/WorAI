"""
Thai Personal Income Tax Calculator Tool for WorAI Engine.
Calculates tax based on annual income and standard deductions.
"""

import re
from typing import Any, Dict, List, Tuple

def tool_tax_calculator(raw_text: str = "", **kwargs: Any) -> Dict[str, Any]:
    """Calculate Thai Personal Income Tax from raw text or parameters."""
    
    # 1. Extract income from text
    # Look for numbers, handle 'k', 'm', 'หมื่น', 'แสน', 'ล้าน'
    income = _extract_income(raw_text)
    if income is None:
        return {
            "status": "error",
            "message": "กรุณาระบุรายได้ต่อปี (เช่น 'รายได้ 500,000 บาท') เพื่อให้ผมช่วยคำนวณภาษีให้ครับ"
        }

    # 2. Basic Tax Calculation Logic (Thailand 2024-2025)
    # Deductions: 
    # - Expense: 50% max 100,000
    # - Personal: 60,000
    expense_deduction = min(income * 0.5, 100000)
    personal_deduction = 60000
    net_income = max(0, income - expense_deduction - personal_deduction)
    
    tax_brackets = [
        (150000, 0.00),
        (300000, 0.05),
        (500000, 0.10),
        (750000, 0.15),
        (1000000, 0.20),
        (2000000, 0.25),
        (5000000, 0.30),
        (float('inf'), 0.35)
    ]
    
    total_tax = 0
    remaining_income = net_income
    previous_limit = 0
    breakdown = []
    
    for limit, rate in tax_brackets:
        range_size = limit - previous_limit
        if remaining_income <= 0:
            break
            
        taxable_in_this_bracket = min(remaining_income, range_size)
        tax_in_this_bracket = taxable_in_this_bracket * rate
        
        if tax_in_this_bracket > 0 or rate == 0:
            bracket_desc = f"{int(previous_limit):,d} - {f'{int(limit):,d}' if limit != float('inf') else 'ขึ้นไป'}"
            breakdown.append({
                "bracket": bracket_desc,
                "rate": f"{int(rate * 100)}%",
                "taxable": f"{int(taxable_in_this_bracket):,d}",
                "tax": f"{int(tax_in_this_bracket):,d}"
            })
            
        total_tax += tax_in_this_bracket
        remaining_income -= taxable_in_this_bracket
        previous_limit = limit

    return {
        "success": True,
        "income": f"{int(income):,d} บาท",
        "net_income": f"{int(net_income):,d} บาท",
        "tax_payable": f"{int(total_tax):,d} บาท",
        "breakdown": breakdown,
        "summary": f"รายได้ต่อปี {int(income):,d} บาท หักค่าใช้จ่ายและลดหย่อนส่วนตัวแล้ว เหลือรายได้สุทธิ {int(net_income):,d} บาท ต้องเสียภาษีทั้งหมด {int(total_tax):,d} บาท"
    }

def _extract_income(text: str) -> float:
    """Helper to extract salary/income from Thai/English text."""
    # Clean up commas and spaces
    clean_text = text.replace(",", "")
    
    # Match numbers with units
    # 1.5 ล้าน -> 1,500,000
    # 5 แสน -> 500,000
    # 3 หมื่น -> 30,000
    
    patterns = [
        (r'(\d+\.?\d*)\s*(ล้าน|m)', 1000000),
        (r'(\d+\.?\d*)\s*(แสน)', 100000),
        (r'(\d+\.?\d*)\s*(หมื่น)', 10000),
        (r'(\d+\.?\d*)\s*(พัน|k)', 1000),
        (r'(\d+\.?\d*)', 1)
    ]
    
    # Try monthly vs annual
    is_monthly = any(k in text for k in ["ต่อเดือน", "เดือนละ", "เงินเดือน"])
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, clean_text)
        if match:
            value = float(match.group(1)) * multiplier
            if is_monthly and multiplier <= 100000: # Probably monthly if not millions
                return value * 12
            return value
            
    return None
