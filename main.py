"""
Pharmacy Management System - [Q07: Improve Data Accuracy]
BBAT104: Fundamentals of Total Quality Management (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Main Application Launcher
"""

import sys
import os

# Ensure project root is in system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import PharmacyApp

if __name__ == "__main__":
    app = PharmacyApp()
    app.mainloop()
