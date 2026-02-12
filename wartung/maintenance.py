#!/usr/bin/env python3
"""
Maintenance Manager - Wartungs-Management
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

class MaintenanceManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
    
    def _get_connection(self) -> sqlite3.Connection:
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def get_upcoming_maintenance(self, days: int = 30) -> List[Dict]:
        """Kommende Wartungen abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        from datetime import timedelta
        cutoff_date = (date.today() + timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT m.*, p.name as property_name, u.unit_number
            FROM maintenance m
            JOIN properties p ON m.property_id = p.id
            LEFT JOIN units u ON m.unit_id = u.id
            WHERE m.scheduled_date <= ?
              AND m.status IN ('planned', 'scheduled')
            ORDER BY m.scheduled_date
        """, (cutoff_date,))
        
        return [dict(row) for row in cursor.fetchall()]