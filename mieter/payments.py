#!/usr/bin/env python3
"""
Payment Manager - Zahlungsverwaltung
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PaymentManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
    
    def _get_connection(self) -> sqlite3.Connection:
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def get_recent_payments(self, limit: int = 50) -> List[Dict]:
        """Letzte X Zahlungen abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, t.first_name, t.last_name
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            ORDER BY p.payment_date DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]