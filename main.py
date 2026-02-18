#!/usr/bin/env python3
"""
Hausverwaltung Software - Hauptprogramm
Umfassende Lösung für Immobilien-, Mieter-, Rechnungs- und Wartungs-Verwaltung
"""

import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

# Importiere alle Module (mit lokalen Pfaden)
import sys
from pathlib import Path

# Aktueller Pfad zum Python-Path hinzufügen
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import Config
from immo.properties import PropertyManager
from mieter.tenants import TenantManager
from mieter.payments import PaymentManager
from rechnungen.invoice_manager import InvoiceManager
from wartung.maintenance import MaintenanceManager
from reports.dashboard import Dashboard

class HausverwaltungApp:
    def __init__(self):
        current_dir = Path(__file__).parent
        self.config = Config()
        # Einfacher Pfad für Datenbank (relativ zum Projekt)
        self.db_path = Path("hausverwaltung.db")
        # Repository-Struktur für die Dateien erstellen
        self.repo_structure = {
            'database': Path(self.db_path),
            'invoices_pdfs': current_dir / 'rechnungen' / 'pdf',
            'documents': current_dir / 'docs' / 'documents',  
            'reports': current_dir / 'reports' / 'output',
            'backups': current_dir / 'backups'
        }
        
        # Manager-Instanzen erstellen
        self.property_manager = PropertyManager(current_dir / self.db_path)
        self.tenant_manager = TenantManager(current_dir / self.db_path)
        self.payment_manager = PaymentManager(current_dir / self.db_path)
        self.invoice_manager = InvoiceManager(current_dir / self.db_path)
        self.maintenance_manager = MaintenanceManager(current_dir / self.db_path)
        self.dashboard = Dashboard(current_dir / self.db_path)
    
    def init_database(self, force: bool = False):
        """Datenbank initialisieren"""
        if force and self.db_path.exists():
            self.db_path.unlink()
        
        # Verzeichnisse erstellen
        for path in self.repo_structure.values():
            path.mkdir(parents=True, exist_ok=True)
        
        # Datenbank-Schema erstellen
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Property-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                zip_code TEXT,
                property_type TEXT DEFAULT 'residential',
                units INTEGER DEFAULT 1,
                total_area REAL DEFAULT 0,
                purchase_price REAL DEFAULT 0,
                purchase_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Units-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER,
                unit_number TEXT NOT NULL,
                floor INTEGER,
                area REAL DEFAULT 0,
                rent_netto REAL DEFAULT 0,
                rent_brutto REAL DEFAULT 0,
                status TEXT DEFAULT 'vacant',
                tenant_id INTEGER,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)
        
        # Tenants-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                birth_date DATE,
                address TEXT,
                iban TEXT,
                bic TEXT,
                contract_start DATE,
                contract_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contracts-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                unit_id INTEGER,
                contract_start DATE NOT NULL,
                contract_end DATE,
                rent_netto REAL NOT NULL,
                rent_brutto REAL NOT NULL,
                deposit REAL DEFAULT 0,
                terms TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                FOREIGN KEY (unit_id) REFERENCES units (id)
            )
        """)
        
        # Payments-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                payment_method TEXT,
                reference TEXT,
                status TEXT DEFAULT 'received',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)
        
        # Invoices-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                property_id INTEGER,
                unit_id INTEGER,
                invoice_number TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                issue_date DATE NOT NULL,
                status TEXT DEFAULT 'draft',
                pdf_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (unit_id) REFERENCES units (id)
            )
        """)
        
        # Maintenance-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER,
                unit_id INTEGER,
                task_type TEXT NOT NULL,
                description TEXT,
                contractor TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'planned',
                scheduled_date DATE,
                completed_date DATE,
                cost REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (unit_id) REFERENCES units (id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Datenbank erfolgreich initialisiert")
        
    def show_dashboard(self):
        """Dashboard anzeigen"""
        self.dashboard.show_overview()
    
    def list_properties(self):
        """Alle Immobilien auflisten"""
        properties = self.property_manager.get_all_properties()
        print(f"\n🏠 GEFUNDENE IMMOBILIEN ({len(properties)}):")
        print("-" * 60)
        
        for prop in properties:
            print(f"ID: {prop[0]} | {prop[1]} | {prop[2]}, {prop[3]} | {prop[6]} Einheiten")
    
    def add_property_interactive(self):
        """Interaktiv neue Immobilie hinzufügen"""
        print("\n🏠 NEUE IMMOBILIE HINZUFÜGEN")
        print("=" * 40)
        
        name = input("Objektname: ").strip()
        address = input("Adresse: ").strip()
        city = input("Stadt: ").strip()
        zip_code = input("PLZ: ").strip()
        property_type = input("Typ (residential/commercial): ") or "residential"
        units = int(input("Anzahl Einheiten: ") or "1")
        
        property_id = self.property_manager.add_property(
            name=name,
            address=address,
            city=city,
            zip_code=zip_code,
            property_type=property_type,
            units=units
        )
        
        print(f"✅ Immobilie mit ID {property_id} erfolgreich hinzugefügt")
    
    def add_tenant_interactive(self):
        """Interaktiv neuen Mieter hinzufügen"""
        print("\n👥 NEUEN MIETER HINZUFÜGEN")
        print("=" * 35)
        
        first_name = input("Vorname: ").strip()
        last_name = input("Nachname: ").strip()
        email = input("E-Mail: ").strip()
        phone = input("Telefon: ").strip()
        
        tenant_id = self.tenant_manager.add_tenant(
            first_name=first_name,
            last_name=last_name,
            email=email if email else None,
            phone=phone if phone else None
        )
        
        print(f"✅ Mieter mit ID {tenant_id} erfolgreich hinzugefügt")
    
    def generate_invoice_interactive(self):
        """Interaktiv Rechnung generieren"""
        print("\n💰 RECHNUNG GENERIEREN")
        print("=" * 30)
        
        # Tenants auflisten
        tenants = self.tenant_manager.get_all_tenants()
        if not tenants:
            print("Keine Mieter vorhanden!")
            return
            
        print("Verfügbare Mieter:")
        for tenant in tenants:
            print(f"ID: {tenant[0]} | {tenant[1]} {tenant[2]}")
        
        try:
            tenant_id = int(input("Mieter-ID: "))
            
            # Properties auflisten
            properties = self.property_manager.get_all_properties()
            print("Verfügbare Objekte:")
            for prop in properties:
                print(f"ID: {prop[0]} | {prop[1]} | {prop[2]}")
            
            property_id = int(input("Objekt-ID: "))
            amount = float(input("Betrag (€): "))
            description = input("Beschreibung: ").strip()
            
            invoice_id = self.invoice_manager.create_invoice(
                tenant_id=tenant_id,
                property_id=property_id,
                amount=amount,
                description=description
            )
            
            print(f"✅ Rechnung {self.invoice_manager.get_invoice_number(invoice_id)} erstellt")
            
            # PDF erstellen
            pdf_path = self.invoice_manager.generate_pdf(invoice_id)
            print(f"📄 PDF erstellt: {pdf_path}")
            
        except ValueError:
            print("❌ Fehler: Bitte gültige Zahlen eingeben")
    
    def show_upcoming_maintenance(self):
        """Kommende Wartungen anzeigen"""
        maintenance = self.maintenance_manager.get_upcoming_maintenance(days=30)
        
        print(f"\n🔧 KOMMENDE WARTUNGEN (nächste 30 Tage):")
        print("-" * 50)
        
        if not maintenance:
            print("Keine geplanten Wartungen")
        else:
            for entry in maintenance:
                print(f"ID: {entry[0]} | {entry[2]} | {entry[4]} | Fällig: {entry[6] if entry[6] else 'Nicht terminiert'}")
                
    def run(self):
        """Hauptprogramm-Loop"""
        parser = argparse.ArgumentParser(description="Hausverwaltung Software")
        parser.add_argument("--init-db", action="store_true", help="Datenbank initialisieren")
        parser.add_argument("--force-db", action="store_true", help="Bestehende Datenbank überschreiben")
        parser.add_argument("--add-property", action="store_true", help="Neue Immobilie hinzufügen")
        parser.add_argument("--add-tenant", action="store_true", help="Neuen Mieter hinzufügen")
        parser.add_argument("--generate-invoice", action="store_true", help="Rechnung generieren")
        parser.add_argument("--dashboard", action="store_true", help="Dashboard anzeigen")
        parser.add_argument("--list-properties", action="store_true", help="Immobilien auflisten")
        parser.add_argument("--upcoming-maintenance", action="store_true", help="Kommende Wartungen")
        
        args = parser.parse_args()
        
        # Datenbank initialisieren falls gewünscht
        if args.init_db:
            self.init_database(force=args.force_db)
            return
        
        # Prüfe ob Datenbank existiert
        if not self.db_path.exists():
            print("❌ Datenbank nicht gefunden. Führe zuerst aus:")
            print("python main.py --init-db")
            return
        
        if args.dashboard:
            self.show_dashboard()
        elif args.add_property:
            self.add_property_interactive()
        elif args.add_tenant:
            self.add_tenant_interactive()
        elif args.generate_invoice:
            self.generate_invoice_interactive()
        elif args.list_properties:
            self.list_properties()
        elif args.upcoming_maintenance:
            self.show_upcoming_maintenance()
        else:
            # Standard: Dashboard anzeigen
            self.show_dashboard()

def main():
    """Hauptfunktion"""
    try:
        app = HausverwaltungApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Programm beendet")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()