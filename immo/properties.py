#!/usr/bin/env python3
"""
Immobilien-Verwaltung - Property Manager
Verwaltung von Immobilien-Objekten und Wohneinheiten
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Property:
    """Immobilien-Objekt"""
    id: int
    name: str
    address: str
    city: str
    zip_code: str
    property_type: str
    units: int
    total_area: float
    purchase_price: float
    purchase_date: Optional[str]
    created_at: str
    updated_at: str

class PropertyManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Datenbank-Verbindung erstellen"""
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def add_property(self, name: str, address: str, city: str, zip_code: str = "",
                    property_type: str = "residential", units: int = 1, 
                    total_area: float = 0, purchase_price: float = 0, 
                    purchase_date: str = None) -> int:
        """
        Neue Immobilie hinzufügen
        
        Args:
            name: Objektname
            address: Adresse
            city: Stadt
            zip_code: PLZ
            property_type: 'residential' oder 'commercial'
            units: Anzahl Wohneinheiten
            total_area: Gesamtfläche in m²
            purchase_price: Kaufpreis
            purchase_date: Kaufdatum (YYYY-MM-DD)
        
        Returns:
            ID der neuen Immobilie
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO properties (
                name, address, city, zip_code, property_type, 
                units, total_area, purchase_price, purchase_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, address, city, zip_code, property_type,
            units, total_area, purchase_price, purchase_date
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Immobilie '{name}' mit ID {property_id} hinzugefügt")
        return property_id
    
    def get_property(self, property_id: int) -> Optional[Dict]:
        """Einzelne Immobilie abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def get_all_properties(self) -> List[Tuple]:
        """Alle Immobilien abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, address, city, zip_code, property_type, units
            FROM properties 
            ORDER BY name
        """)
        
        return cursor.fetchall()
    
    def update_property(self, property_id: int, **kwargs) -> bool:
        """Immobilie aktualisieren"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Validiere Updates
        allowed_fields = ['name', 'address', 'city', 'zip_code', 'property_type',
                         'units', 'total_area', 'purchase_price', 'purchase_date']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            print("⚠️  Keine gültigen Felder für Update gefunden")
            return False
        
        values.append(property_id)
        
        cursor.execute(f"""
            UPDATE properties 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_property(self, property_id: int) -> bool:
        """Immobilie löschen (mit CASCADE auf Einheiten)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prüfe zuerst ob noch aktive Verträge vorhanden sind
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM units u
            JOIN contracts c ON u.id = c.unit_id
            WHERE u.property_id = ? AND c.status = 'active'
        """, (property_id,))
        
        active_contracts = cursor.fetchone()['count']
        if active_contracts > 0:
            print(f"❌ Kann Immobilie nicht löschen - {active_contracts} aktive Verträge vorhanden")
            return False
        
        cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    def get_properties_summary(self) -> Dict:
        """Zusammenfassung aller Immobilien"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_properties,
                SUM(units) as total_units,
                SUM(Purchase_price * units) as total_investment,
                AVG(units) as avg_units_per_property
            FROM properties
        """)
        
        row = cursor.fetchone()
        summary = dict(row) if row else {}
        
        # Füge weitere Statistiken hinzu
        cursor.execute("""
            SELECT property_type, COUNT(*) as count
            FROM properties
            GROUP BY property_type
        """)
        
        summary['by_type'] = [dict(row) for row in cursor.fetchall()]
        
        return summary
    
    def search_properties(self, query: str) -> List[Tuple]:
        """Immobilien nach Name oder Adresse suchen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        like_query = f"%{query}%"
        cursor.execute("""
            SELECT id, name, address, city, property_type, units
            FROM properties 
            WHERE name LIKE ? OR address LIKE ? OR city LIKE ?
            ORDER BY name
        """, (like_query, like_query, like_query))
        
        return cursor.fetchall()
    
    def get_occupancy_rate(self, property_id: int) -> float:
        """Auslastung der Immobilie berechnen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total units
        cursor.execute("SELECT units FROM properties WHERE id = ?", (property_id,))
        total_units = cursor.fetchone()['units']
        
        # Occupied units
        cursor.execute("""
            SELECT COUNT(*) as occupied
            FROM units 
            WHERE property_id = ? AND status = 'occupied' 
              AND tenant_id IN (SELECT id FROM tenants WHERE contract_end IS NULL 
                               OR contract_end > date('now'))
        """, (property_id,))
        
        occupied_units = cursor.fetchone()['occupied']
        
        return (occupied_units / total_units * 100) if total_units > 0 else 0.0
    
    def add_unit(self, property_id: int, unit_number: str, floor: int = None,
                 area: float = 0, rent_netto: float = 0, rent_brutto: float = 0,
                 tenant_id: int = None) -> int:
        """
        Neue Wohneinheit hinzufügen
        
        Args:
            property_id: ID der Immobilie
            unit_number: Wohnungsnummer (z.B. "Top 1", "Wohnung 1A")
            floor: Stockwerk
            area: Wohnfläche in m²
            rent_netto: Nettomiete
            rent_brutto: Bruttomiete  
            tenant_id: Mieter-ID (optional)
        
        Returns:
            ID der neuen Einheit
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prüfe ob Immobilie existiert und Einheit noch nicht vorhanden
        cursor.execute("SELECT id FROM properties WHERE id = ?", (property_id,))
        if not cursor.fetchone():
            raise ValueError(f"Immobilie mit ID {property_id} nicht gefunden")
        
        cursor.execute("""
            SELECT id FROM units 
            WHERE property_id = ? AND unit_number = ?
        """, (property_id, unit_number))
        
        if cursor.fetchone():
            raise ValueError(f"Einheit {unit_number} existiert bereits in dieser Immobilie")
        
        cursor.execute("""
            INSERT INTO units (
                property_id, unit_number, floor, area, 
                rent_netto, rent_brutto, tenant_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (property_id, unit_number, floor, area, rent_netto, rent_brutto, tenant_id))
        
        unit_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Einheit '{unit_number}' mit ID {unit_id} zur Immobilie {property_id} hinzugefügt")
        return unit_id
    
    def get_units_for_property(self, property_id: int) -> List[Tuple]:
        """Alle Einheiten einer Immobilie abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.*, t.first_name, t.last_name, t.email as tenant_email
            FROM units u
            LEFT JOIN tenants t ON u.tenant_id = t.id
            WHERE u.property_id = ?
            ORDER BY u.unit_number
        """, (property_id,))
        
        return cursor.fetchall()
    
    def get_unit_occupancy_stats(self) -> Dict[str, int]:
        """Statistiken zur Auslastung aller Einheiten"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM units
            GROUP BY status
        """)
        
        stats = {'total': 0}
        for row in cursor.fetchall():
            stats[row['status']] = row['count']
            stats['total'] += row['count']
        
        if stats['total'] > 0:
            stats['occupancy_rate'] = (stats.get('occupied', 0) / stats['total']) * 100
        else:
            stats['occupancy_rate'] = 0.0
        
        return stats
    
    def close_connection(self):
        """Datenbank-Verbindung schließen"""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None