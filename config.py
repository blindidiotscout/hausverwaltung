#!/usr/bin/env python3
"""
Hausverwaltung Software - Konfiguration
"""

from pathlib import Path

class Config:
    """Konfiguration für die Hausverwaltung Software."""
    
    # Basis-Pfad
    BASE_DIR = Path(__file__).parent
    
    # Datenbank-Konfiguration
    DATABASE_URL = f"sqlite:///{BASE_DIR}/hausverwaltung.db"
    DATABASE_PATH = BASE_DIR / "hausverwaltung.db"
    
    # Bank-Integration
    BANK_INTEGRATION = False
    BANK_API_URL = ""
    BANK_API_KEY = ""
    
    # Rechnungs-Einstellungen
    INVOICE_TEMPLATE = "modern"
    INVOICE_PREFIX = "RE"
    INVOICE_COMPANY_NAME = "Hausverwaltung"
    INVOICE_COMPANY_ADDRESS = ""
    INVOICE_COMPANY_CITY = ""
    INVOICE_COMPANY_ZIP = ""
    INVOICE_COMPANY_COUNTRY = "Austria"
    
    # Wartungs-Einstellungen
    MAINTENANCE_REMINDER_DAYS = 7
    MAINTENANCE_AUTO_ASSIGN = True
    
    # E-Mail-Einstellungen
    EMAIL_ENABLED = False
    EMAIL_SMTP_SERVER = ""
    EMAIL_SMTP_PORT = 587
    EMAIL_SMTP_USER = ""
    EMAIL_SMTP_PASSWORD = ""
    EMAIL_FROM = ""
    
    # Kalender-Integration
    CALENDAR_ENABLED = False
    CALENDAR_TYPE = "google"  # google, outlook, ical
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "logs" / "hausverwaltung.log"
    
    # Upload-Pfade
    UPLOAD_PATH = BASE_DIR / "uploads"
    
    # PDF-Ausgabe
    PDF_OUTPUT_PATH = BASE_DIR / "rechnungen" / "pdf"
    
    # Sprache
    LANGUAGE = "de"
    
    # Währung
    CURRENCY = "EUR"
    
    def __init__(self):
        """Initialisierung der Konfiguration."""
        # Verzeichnisse erstellen falls nicht vorhanden
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
        self.PDF_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)