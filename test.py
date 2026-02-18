#!/usr/bin/env python3
"""
Test-Script für Hausverwaltung Software
"""

import sys
from pathlib import Path

# Pfad zum lokalen Verzeichnis hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

# Test ohne externe Dependencies
import sqlite3
import os
from datetime import datetime, date

def test_database():
    """Test Database Creation"""
    db_path = "test_hausverwaltung.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print("🔧 Erstelle Test-Datenbank...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Properties Table
    cursor.execute("""
        CREATE TABLE properties (
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
    
    # Test Property hinzufügen
    cursor.execute("""
        INSERT INTO properties (
            name, address, city, property_type, units
        ) VALUES (?, ?, ?, ?, ?)
    """, ("Testwohnhaus Wien", "Musterstraße 123", "Wien", "residential", 5))
    
    property_id = cursor.lastrowid
    
    print(f"✅ Property mit ID {property_id} erstellt")
    
    # Tenants Table
    cursor.execute("""
        CREATE TABLE tenants (
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
    
    # Test Tenant hinzufügen
    cursor.execute("""
        INSERT INTO tenants (
            first_name, last_name, email, phone
        ) VALUES (?, ?, ?, ?)
    """, ("Max", "Mustermann", "max@test.com", "+43123456789"))
    
    tenant_id = cursor.lastrowid
    
    print(f"✅ Tenant mit ID {tenant_id} erstellt")
    
    # Invoices Table
    cursor.execute("""
        CREATE TABLE invoices (
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
            FOREIGN KEY (property_id) REFERENCES properties (id)
        )
    """)
    
    # Test Invoice hinzufügen
    invoice_number = f"TEST-2026-02-001"
    cursor.execute("""
        INSERT INTO invoices (
            tenant_id, property_id, invoice_number, amount, 
            description, due_date, issue_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tenant_id, property_id, invoice_number, 850.00, 
          "Nettokaltmiete Februar 2026", 
          date.today().isoformat(), date.today().isoformat()))
    
    invoice_id = cursor.lastrowid
    
    print(f"✅ Invoice {invoice_number} mit ID {invoice_id} erstellt")
    
    conn.commit()
    conn.close()
    
    print(f"📄 Test-Datenbank erstellt: {db_path}")
    
    # Teste Abfragen
    print("\n📊 Test-Datenbank Abfragen:")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM properties")
    properties_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tenants")
    tenants_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoices_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT p.name, p.city, t.first_name, t.last_name, i.invoice_number, i.amount
        FROM properties p
        JOIN invoices i ON p.id = i.property_id
        JOIN tenants t ON i.tenant_id = t.id
    """)
    
    rows = cursor.fetchall()
    
    print(f"🏠 Properties: {properties_count}")
    print(f"👥 Tenants: {tenants_count}")
    print(f"💰 Invoices: {invoices_count}")
    
    if rows:
        print("\n📈 Zusammenfassung:")
        for row in rows:
            print(f"  {row[1]}: {row[3]}, {row[4]} - €{row[5]:.2f}")
    
    conn.close()
    print("\n✅ Alle Tests erfolgreich!")
    
    # Aufräumen
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🧹 Test-Datenbank bereinigt: {db_path}")

if __name__ == "__main__":
    test_database()