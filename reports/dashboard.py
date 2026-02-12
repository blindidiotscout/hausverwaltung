#!/usr/bin/env python3
"""
Dashboard - Übersicht und KPI-Anzeige
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

class Dashboard:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
    
    def _get_connection(self) -> sqlite3.Connection:
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def show_overview(self):
        """Zeigt Dashboard-Übersicht"""
        print("\n🏢 HAUSVERWALTUNG DASHBOARD")
        print("=" * 50)
        
        # Immobilien-Statistiken
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM properties")
        total_properties = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tenants")
        total_tenants = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(amount) as total FROM invoices WHERE status = 'paid'")
        total_revenue = cursor.fetchone()['total'] or 0
        
        print(f"📈 Wichtige Kennzahlen:")
        print(f"  🏠 Immobilien: {total_properties}")
        print(f"  👥 Mieter: {total_tenants}")
        print(f"  💰 Einnahmen: {total_revenue:.2f} €")
        
        # Offene Rechnungen
        cursor.execute("SELECT COUNT(*) as count, SUM(amount) as total FROM invoices WHERE status = 'sent'")
        open_invoices = cursor.fetchone()
        print(f"  📄 Offene Rechnungen: {open_invoices['count']} ({open_invoices['total'] or 0:.2f} €)")
    
    def show_upcoming_maintenance(self):
        """Zeigt kommende Wartungen"""
        print("\n🔧 Kommende Wartungen:")
        print("-" * 30)
        
        maintenance = self.get_upcoming_maintenance(30)
        if not maintenance:
            print("Keine geplanten Wartungen")
            return
        
        for entry in maintenance:
            print(f"  {entry['scheduled_date']}: {entry['task_type']} - {entry['property_name']}")
    
    def get_upcoming_maintenance(self, days: int = 30) -> List[Dict]:
        """Kommende Wartungen abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        from datetime import timedelta
        cutoff_date = (date.today() + timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT m.*, p.name as property_name
            FROM maintenance m
            JOIN properties p ON m.property_id = p.id
            WHERE m.scheduled_date <= ?
              AND m.status IN ('planned', 'scheduled')
            ORDER BY m.scheduled_date
        """, (cutoff_date,))
        
        return [dict(row) for row in cursor.fetchall()]