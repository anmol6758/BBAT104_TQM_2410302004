"""
Digital Defect Checksheet Module
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Quality Goal [Q07: Improve Data Accuracy]
"""

import os
import sys
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_connection
from src.defect_logger import DefectLogger


class DefectChecksheet:
    """Standardized TQM Data Collection Checksheet for Quality Audit."""

    @staticmethod
    def generate_shift_checksheet():
        """Aggregates logged defect events across operational shifts."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT 
                defect_code,
                defect_category,
                COUNT(*) as total_count,
                SUM(CASE WHEN strftime('%H', timestamp) BETWEEN '08' AND '15' THEN 1 ELSE 0 END) as morning_shift,
                SUM(CASE WHEN strftime('%H', timestamp) BETWEEN '16' AND '23' THEN 1 ELSE 0 END) as evening_shift,
                MAX(severity) as max_severity
            FROM defect_logs
            GROUP BY defect_code, defect_category
            ORDER BY total_count DESC
        """).fetchall()
        conn.close()

        checksheet_data = []
        grand_total = 0
        morning_total = 0
        evening_total = 0

        for r in rows:
            tot = r["total_count"]
            m_cnt = r["morning_shift"] or 0
            e_cnt = r["evening_shift"] or 0
            grand_total += tot
            morning_total += m_cnt
            evening_total += e_cnt

            checksheet_data.append({
                "code": r["defect_code"],
                "category": r["defect_category"],
                "morning": m_cnt,
                "evening": e_cnt,
                "total": tot,
                "severity": r["max_severity"]
            })

        return {
            "title": "BBAT104 TQM DIGITAL DEFECT CHECKSHEET",
            "auditor": "Anmol Joshi (2410302004)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "items": checksheet_data,
            "morning_total": morning_total,
            "evening_total": evening_total,
            "grand_total": grand_total
        }

    @staticmethod
    def export_text_report():
        sheet = DefectChecksheet.generate_shift_checksheet()
        lines = [
            "=" * 78,
            f"          {sheet['title']}",
            f"  Auditor: {sheet['auditor']} | Date: {sheet['date']} | Goal: Q07",
            "=" * 78,
            f"{'Code':<8} {'Defect Category':<30} {'Morning':<10} {'Evening':<10} {'Total':<8} {'Severity'}",
            "-" * 78,
        ]

        for it in sheet["items"]:
            lines.append(
                f"{it['code']:<8} {it['category']:<30} {it['morning']:<10} {it['evening']:<10} {it['total']:<8} {it['severity']}/5"
            )

        lines.extend([
            "-" * 78,
            f"{'TOTALS':<39} {sheet['morning_total']:<10} {sheet['evening_total']:<10} {sheet['grand_total']:<8}",
            "=" * 78,
        ])
        return "\n".join(lines)


if __name__ == "__main__":
    DefectLogger.seed_empirical_checksheet_data()
    print(DefectChecksheet.export_text_report())
