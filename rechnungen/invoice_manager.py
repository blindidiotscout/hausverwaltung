#!/usr/bin/env python3
"""
Rechnungs-Verwaltung - Invoice Manager
Erstellung und Verwaltung von Rechnungen
"""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import uuid
import os
from fpdf import FPDF

@dataclass
class Invoice:
    """Rechnungs-Objekt"""
    id: int
    tenant_id: int
    property_id: int
    unit_id: int
    invoice_number: str
    amount: float
    description: str
    due_date: str
    issue_date: str
    status: str
    pdf_path: Optional[str]
    created_at: str

class InvoiceManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_connection = None
        
        # Pfade für PDFs
        self.pdf_dir = db_path.parent / "rechnungen" / "pdf"
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Datenbank-Verbindung erstellen"""
        if self.db_connection is None:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
        return self.db_connection
    
    def generate_invoice_number(self, year: int, month: int, prefix: str = "INV") -> str:
        """
        Fortlaufende Rechnungsnummer erstellen
        
        Args:
            year: Jahr
            month: Monat (1-12)
            prefix: Präfix für Rechnungsnummer
        
        Returns:
            Format: INV-YYYY-MM-XXX
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Zähle bestehende Rechnungen für diesen Monat
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM invoices 
            WHERE invoice_number LIKE ?
        """, (f"{prefix}-{year}-{month:02d}-%",))
        
        count = cursor.fetchone()['count'] + 1
        
        return f"{prefix}-{year}-{month:02d}-{count:03d}"
    
    def create_invoice(self, tenant_id: int, property_id: int, unit_id: int = None,
                     amount: float = 0.0, description: str = "", 
                     due_date: str = None) -> int:
        """
        Neue Rechnung erstellen
        
        Args:
            tenant_id: ID des Mieters
            property_id: ID der Immobilie
            unit_id: ID der Einheit (optional)
            amount: Betrag
            description: Beschreibung
            due_date: Fälligkeitsdatum (14 Tage默认为)
        
        Returns:
            ID der neuen Rechnung
        """
        # Standard-Fälligkeitsdatum: 14 Tage nach Ausstellungsdatum
        if not due_date:
            due_date = (date.today() + timedelta(days=14)).isoformat()
        
        issue_date = date.today().isoformat()
        
        # Rechnungsnummer generieren
        today = date.today()
        invoice_number = self.generate_invoice_number(today.year, today.month)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO invoices (
                tenant_id, property_id, unit_id, invoice_number,
                amount, description, due_date, issue_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tenant_id, property_id, unit_id, invoice_number,
            amount, description, due_date, issue_date
        ))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Rechnung {invoice_number} mit ID {invoice_id} erstellt")
        return invoice_id
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """Einzelne Rechnung abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.*, t.first_name, t.last_name, t.email, 
                   t.iban, t.bic, p.name as property_name, 
                   u.unit_number
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.id
            JOIN properties p ON i.property_id = p.id
            LEFT JOIN units u ON i.unit_id = u.id
            WHERE i.id = ?
        """, (invoice_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """Rechnung über Rechnungsnummer abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.*, t.first_name, t.last_name, t.email, 
                   p.name as property_name, u.unit_number
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.id
            JOIN properties p ON i.property_id = p.id
            LEFT JOIN units u ON i.unit_id = u.id
            WHERE i.invoice_number = ?
        """, (invoice_number,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_invoice_number(self, invoice_id: int) -> str:
        """Rechnungsnummer für ID abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT invoice_number FROM invoices WHERE id = ?", (invoice_id,))
        result = cursor.fetchone()
        
        return result['invoice_number'] if result else ""
    
    def update_invoice_status(self, invoice_id: int, status: str) -> bool:
        """Rechnungsstatus aktualisieren"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        allowed_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
        if status not in allowed_status:
            print(f"⚠️  Ungültiger Status: {status}")
            return False
        
        cursor.execute("""
            UPDATE invoices SET status = ?
            WHERE id = ?
        """, (status, invoice_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def mark_invoice_as_paid(self, invoice_id: int, payment_date: str = None) -> bool:
        """Rechnung als bezahlt markieren"""
        if not payment_date:
            payment_date = date.today().isoformat()
        
        # Status aktualisieren
        if not self.update_invoice_status(invoice_id, 'paid'):
            return False
        
        # Bezahlung in separate Tabelle eintragen (falls erweitert)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Lade Rechnungsdaten
        invoice_data = self.get_invoice(invoice_id)
        if not invoice_data:
            return False
        
        # Bezahlung eintragen
        cursor.execute("""
            INSERT INTO payments (
                tenant_id, amount, payment_date, payment_method, 
                reference, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            invoice_data['tenant_id'], invoice_data['amount'],
            payment_date, 'bank_transfer', 
            f"Rechnung {invoice_data['invoice_number']}", 'completed'
        ))
        
        conn.commit()
        print(f"✅ Rechnung {invoice_data['invoice_number']} als bezahlt markiert")
        return True
    
    def get_pending_invoices(self, days_overdue: int = 0) -> List[Dict]:
        """Ausstehende Rechnungen abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if days_overdue > 0:
            # Überfällige Rechnungen
            overdue_date = date.today() - timedelta(days=days_overdue)
            cursor.execute("""
                SELECT i.*, t.first_name, t.last_name, 
                       p.name as property_name, u.unit_number
                FROM invoices i
                JOIN tenants t ON i.tenant_id = t.id
                JOIN properties p ON i.property_id = p.id
                LEFT JOIN units u ON i.unit_id = u.id
                WHERE i.status IN ('sent', 'overdue')
                  AND i.due_date < ?
                ORDER BY i.due_date
            """, (overdue_date.isoformat(),))
        else:
            # Alle ausstehenden Rechnungen
            cursor.execute("""
                SELECT i.*, t.first_name, t.last_name, 
                       p.name as property_name, u.unit_number
                FROM invoices i
                JOIN tenants t ON i.tenant_id = t.id
                JOIN properties p ON i.property_id = p.id
                LEFT JOIN units u ON i.unit_id = u.id
                WHERE i.status IN ('draft', 'sent')
                ORDER BY i.due_date
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_total_outstanding(self, property_id: int = None) -> float:
        """Gesamtbetrag offener Rechnungen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if property_id:
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM invoices
                WHERE property_id = ? AND status IN ('draft', 'sent', 'overdue')
            """, (property_id,))
        else:
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM invoices
                WHERE status IN ('draft', 'sent', 'overdue')
            """)
        
        result = cursor.fetchone()
        return result['total'] if result and result['total'] else 0.0
    
    def generate_pdf(self, invoice_id: int) -> Path:
        """PDF-Datei für Rechnung generieren"""
        invoice_data = self.get_invoice(invoice_id)
        if not invoice_data:
            raise ValueError(f"Rechnung ID {invoice_id} nicht gefunden")
        
        # PDF erstellen
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Header
        pdf.cell(0, 10, 'RECHNUNG', 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        # Rechnungsdetails
        pdf.cell(50, 8, f'Rechnungsnummer: {invoice_data["invoice_number"]}', 0, 1)
        pdf.cell(50, 8, f'Ausstellungsdatum: {invoice_data["issue_date"]}', 0, 1)
        pdf.cell(50, 8, f'Fälligkeitsdatum: {invoice_data["due_date"]}', 0, 1)
        pdf.ln(10)
        
        # Empfänger
        pdf.cell(50, 8, 'Rechnung an:', 0, 1)
        pdf.cell(50, 8, f'{invoice_data["first_name"]} {invoice_data["last_name"]}', 0, 1)
        pdf.cell(50, 8, f'{invoice_data["property_name"]}', 0, 1)
        if invoice_data['unit_number']:
            pdf.cell(50, 8, f'Einheit: {invoice_data["unit_number"]}', 0, 1)
        pdf.ln(10)
        
        # Positionen
        pdf.cell(0, 8, 'Positionen:', 0, 1)
        pdf.cell(0, 6, f'{invoice_data["description"]}', 0, 1)
        pdf.ln(5)
        
        # Gesamt
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Gesamtbetrag: {invoice_data["amount"]:.2f} €', 0, 1, 'R')
        
        # PDF speichern
        filename = f"{invoice_data['invoice_number']}.pdf"
        pdf_path = self.pdf_dir / filename
        pdf.output(str(pdf_path))
        
        # Pfad in Datenbank eintragen
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE invoices SET pdf_path = ?
            WHERE id = ?
        """, (str(pdf_path), invoice_id))
        conn.commit()
        
        print(f"📄 PDF generiert: {pdf_path}")
        return pdf_path
    
    def get_monthly_revenue(self, year: int, month: int = None) -> Dict:
        """Monatliche Umsätzte abrufen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if month:
            # Für spezifischen Monat
            cursor.execute("""
                SELECT SUM(amount) as total_paid, COUNT(*) as invoice_count
                FROM invoices
                WHERE YEAR(issue_date) = ? AND MONTH(issue_date) = ?
                  AND status = 'paid'
            """, (year, month))
            
            result = cursor.fetchone()
            return {
                'year': year,
                'month': month,
                'total_paid': result['total_paid'] if result and result['total_paid'] else 0.0,
                'invoice_count': result['invoice_count'] if result else 0
            }
        else:
            # Für gesamtes Jahr
            cursor.execute("""
                SELECT 
                    MONTH(issue_date) as month,
                    SUM(amount) as total_paid,
                    COUNT(*) as invoice_count
                FROM invoices
                WHERE YEAR(issue_date) = ? AND status = 'paid'
                GROUP BY MONTH(issue_date)
                ORDER BY month
            """, (year,))
            
            results = [dict(row) for row in cursor.fetchall()]
            return {
                'year': year,
                'monthly_data': results,
                'total_year': sum(r['total_paid'] for r in results) if results else 0.0,
                'total_invoices': sum(r['invoice_count'] for r in results) if results else 0
            }
    
    def close_connection(self):
        """Datenbank-Verbindung schließen"""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None