#!/usr/bin/env python3
"""
Mieter-Verwaltung - Tenant Manager
Verwaltung von Mietern, Verträgen und Zahlungen
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

@dataclass
class Tenant:
    """Mieter-Objekt"""
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    birth_date: Optional[str]
    address: Optional[str]
    iban: Optional[str]
    bic: Optional[str]
    contract_start: Optional[str]
    contract_end: Optional[str]
    created_at: str
    updated_at: str

class TenantManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
        self.email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        self.phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")
        
    def _get_connection(self) -> sqlite3.Connection:
        """Datenbank-Verbindung erstellen"""
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def validate_email(self, email: str) -> bool:
        """E-Mail-Adresse validieren"""
        return bool(email and self.email_regex.match(email))
    
    def validate_phone(self, phone: str) -> bool:
        """Telefonnummer validieren"""
        if not phone:
            return True
        return bool(self.phone_regex.match(phone.replace(" ", "").replace("-", "")))
    
    def validate_iban(self, iban: str) -> bool:
        """IBAN validieren (vereinfacht)"""
        if not iban:
            return True
        # Entferne Leerzeichen und mache Upper Case
        iban = iban.replace(" ", "").upper()
        
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Erste zwei Buchstaben sind Länderkode
        if not iban[:2].isalpha():
            return False
            
        # Zahlen folgen nach Ländercode
        return iban[2:].isdigit()
    
    def add_tenant(self, first_name: str, last_name: str, email: str = None,
                  phone: str = None, birth_date: str = None, address: str = None,
                  iban: str = None, bic: str = None, 
                  contract_start: str = None, contract_end: str = None) -> int:
        """
        Neuen Mieter hinzufügen
        
        Args:
            first_name: Vorname
            last_name: Nachname
            email: E-Mail-Adresse
            phone: Telefonnummer
            birth_date: Geburtsdatum (YYYY-MM-DD)
            address: Adresse
            iban: IBAN-Nummer
            bic: BIC-Code
            contract_start: Vertragsbeginn (YYYY-MM-DD)
            contract_end: Vertragsende (YYYY-MM-DD)
        
        Returns:
            ID des neuen Mieters
        """
        # Validierung
        if not first_name or not first_name.strip():
            raise ValueError("Vorname ist erforderlich")
        if not last_name or not last_name.strip():
            raise ValueError("Nachname ist erforderlich")
        
        if email and not self.validate_email(email):
            raise ValueError("Ungültige E-Mail-Adresse")
        if phone and not self.validate_phone(phone):
            raise ValueError("Ungültige Telefonnummer")
        if iban and not self.validate_iban(iban):
            raise ValueError("Ungültige IBAN")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prüfe ob E-Mail bereits existiert
        if email:
            cursor.execute("SELECT id FROM tenants WHERE email = ?", (email,))
            if cursor.fetchone():
                print(f"⚠️  Warnung: E-Mail {email} bereits vergeben")
        
        cursor.execute("""
            INSERT INTO tenants (
                first_name, last_name, email, phone, birth_date, 
                address, iban, bic, contract_start, contract_end
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name.strip(), last_name.strip(), email, phone, birth_date,
            address, iban, bic, contract_start, contract_end
        ))
        
        tenant_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Mieter '{first_name} {last_name}' mit ID {tenant_id} hinzugefügt")
        return tenant_id
    
    def get_tenant(self, tenant_id: int) -> Optional[Dict]:
        """Einzelnen Mieter abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def get_all_tenants(self, only_active: bool = True) -> List[Tuple]:
        """Alle Mieter abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if only_active:
            cursor.execute("""
                SELECT t.*, c.status as contract_status
                FROM tenants t
                LEFT JOIN contracts c ON t.id = c.tenant_id
                WHERE c.status = 'active' OR c.status IS NULL
                ORDER BY t.last_name, t.first_name
            """)
        else:
            cursor.execute("""
                SELECT t.*, c.status as contract_status
                FROM tenants t
                LEFT JOIN contracts c ON t.id = c.tenant_id
                ORDER BY t.last_name, t.first_name
            """)
        
        return cursor.fetchall()
    
    def update_tenant(self, tenant_id: int, **kwargs) -> bool:
        """Mieter aktualisieren"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Validiere Updates
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date',
                         'address', 'iban', 'bic', 'contract_start', 'contract_end']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
                
            # Spezielle Validierung für kritische Felder
            if field == 'email' and value and not self.validate_email(value):
                print(f"⚠️  Warnung: Ungültige E-Mail für {field}=>{value}")
                continue
            if field == 'phone' and value and not self.validate_phone(value):
                print(f"⚠️  Warnung: Ungültige Telefonnummer für {field}=>{value}")
                continue
            if field == 'iban' and value and not self.validate_iban(value):
                print(f"⚠️  Warnung: Ungültige IBAN für {field}=>{value}")
                continue
            
            update_fields.append(f"{field} = ?")
            values.append(value)
        
        if not update_fields:
            print("⚠️  Keine gültigen Felder für Update gefunden")
            return False
        
        values.append(tenant_id)
        
        cursor.execute(f"""
            UPDATE tenants 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        
        conn.commit()
        return cursor.rowcount > 0
    
    def search_tenants(self, query: str) -> List[Tuple]:
        """Mieter nach Name oder E-Mail suchen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        like_query = f"%{query}%"
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone, contract_start
            FROM tenants 
            WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)
            ORDER BY last_name, first_name
        """, (like_query, like_query, like_query))
        
        return cursor.fetchall()
    
    def get_tenants_summary(self) -> Dict:
        """Zusammenfassung aller Mieter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Gesamtstatistiken
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tenants,
                COUNT(CASE WHEN contract_start IS NOT NULL THEN 1 END) as with_contracts,
                COUNT(CASE WHEN email IS NOT NULL THEN 1 END) as with_email,
                COUNT(CASE WHEN phone IS NOT NULL THEN 1 END) as with_phone
            FROM tenants
        """)
        
        row = cursor.fetchone()
        summary = dict(row) if row else {}
        
        # Vertragsstatistiken
        cursor.execute("""
            SELECT c.status, COUNT(*) as count
            FROM contracts c
            WHERE c.tenant_id IN (SELECT id FROM tenants)
            GROUP BY c.status
        """)
        
        summary['contract_stats'] = [dict(row) for row in cursor.fetchall()]
        
        return summary
    
    def terminate_contract(self, tenant_id: int, end_date: str = None) -> bool:
        """
        Mieter-Vertrag beenden
        
        Args:
            tenant_id: ID des Mieters
            end_date: Vertragsendesdatum (heute als Standard)
        
        Returns:
            True wenn erfolgreich
        """
        if not end_date:
            end_date = date.today().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Aktiven Vertrag beenden
        cursor.execute("""
            UPDATE contracts 
            SET contract_end = ?, status = 'ended', updated_at = CURRENT_TIMESTAMP
            WHERE tenant_id = ? AND status = 'active'
        """, (end_date, tenant_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            # Mieter-Status aktualisieren
            cursor.execute("""
                UPDATE tenants 
                SET contract_end = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (end_date, tenant_id))
            conn.commit()
            
            print(f"✅ Vertrag für Mieter ID {tenant_id} beendet (Ende: {end_date})")
            return True
        else:
            print(f"⚠️  Kein aktiver Vertrag für Mieter ID {tenant_id} gefunden")
            return False
    
    def get_active_tenants_by_property(self, property_id: int) -> List[Dict]:
        """Aktive Mieter für eine Immobilie abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, u.unit_number, u.area, u.rent_netto, u.rent_brutto
            FROM tenants t
            JOIN contracts c ON t.id = c.tenant_id
            JOIN units u ON c.unit_id = u.id
            JOIN properties p ON u.property_id = p.id
            WHERE p.id = ? AND c.status = 'active'
            ORDER BY u.unit_number
        """, (property_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def calculate_total_rent_for_property(self, property_id: int) -> float:
        """Gesamte Jahresmiete für eine Immobilie berechnen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(u.rent_netto) as total_monthly_rent
            FROM units u
            JOIN contracts c ON u.id = c.unit_id
            WHERE u.property_id = ? AND c.status = 'active'
        """, (property_id,))
        
        result = cursor.fetchone()
        return result['total_monthly_rent'] if result and result['total_monthly_rent'] else 0.0
    
    def close_connection(self):
        """Datenbank-Verbindung schließen"""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None