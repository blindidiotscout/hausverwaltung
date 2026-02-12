# 🏢 Hausverwaltung Software

**Umfassende Software-Lösung für professionelle Hausverwaltung**

## 📋 Überblick

Diese Software ermöglicht die vollständige Verwaltung von Immobilien, Mietern, Rechnungen und Wartungsarbeiten.

## 🏗️ Projekt-Struktur

```
hausverwaltung/
├── README.md                    # Diese Datei
├── main.py                      # Hauptprogramm
├── config.py                    # Konfiguration
├── requirements.txt             # Python-Dependencies
├── .gitignore                   # Git-Ausschlüsse
├── immo/                        # 🏠 Immobilien-Verwaltung
│   ├── properties.py           # Objekt-Verwaltung
│   ├── einheiten.py            # Wohneinheiten
│   ├── __init__.py
│   └── README.md
├── mieter/                      # 👥 Mieter-Verwaltung
│   ├── tenants.py              # Mieter-Verwaltung
│   ├── contracts.py            # Mietverträge
│   ├── payments.py             # Zahlungsverwaltung
│   ├── __init__.py
│   └── README.md
├── rechnungen/                  # 💰 Rechnungs-Verwaltung
│   ├── invoice_manager.py      # Rechnungs-Erstellung/-Verwaltung
│   ├── accounting.py           # Buchhaltung
│   ├── bank_integration.py     # Bank-Integration
│   ├── __init__.py
│   └── README.md
├── wartung/                     # 🔧 Wartungs-Management
│   ├── maintenance.py          # Wartungs-Aufgaben
│   ├── contractors.py          # Handwerker-Verwaltung
│   ├── calendars.py            # Wartungs-Kalender
│   ├── __init__.py
│   └── README.md
├── docs/                        # 📄 Dokumenten-Verwaltung
│   ├── contracts.py            # Vertrags-Verwaltung
│   ├── certificates.py         # Zertifikate (Energie-Ausweise)
│   ├── __init__.py
│   └── README.md
└── reports/                     # 📊 Berichte & Auswertungen
    ├── dashboard.py            # Dashboard mit KPIs
    ├── statements.py           # Abrechnungen
    ├── annual_reports.py       # Jahresabrechnungen
    ├── __init__.py
    └── README.md
```

## 🚀 Schnellstart

### Installation

```bash
# Repository klonen
git clone https://github.com/blindidiotscout/hausverwaltung.git
cd hausverwaltung

# Python-Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### Erstes Setup

```python
# Konfigurationsdatei anpassen
cp config.example.py config.py
# config.py nach Bedarf anpassen

# Datenbank initialisieren
python main.py --init-db

# Erstes Immobilienobjekt hinzufügen
python main.py --add-property
```

## 🏠 Module-Übersicht

### 🏘️ Immobilien-Verwaltung (immo/)
```python
from immo.properties import PropertyManager

# Neue Immobilie hinzufügen
manager = PropertyManager()
property_id = manager.add_property(
    address="Musterstraße 123",
    city="Wien",
    units=10,
    property_type="Wohnhaus"
)
```

### 👥 Mieter-Verwaltung (mieter/)
```python
from mieter.tenants import TenantManager

# Neuen Mieter hinzufügen
tenant_manager = TenantManager()
tenant_id = tenant_manager.add_tenant(
    name="Max Mustermann",
    email="max@example.com",
    phone="+43123456789"
)
```

### 💰 Rechnungs-Verwaltung (rechnungen/)
```python
from rechnungen.invoice_manager import InvoiceManager

# Rechnung erstellen
invoice_manager = InvoiceManager()
invoice_id = invoice_manager.create_invoice(
    tenant_id=tenant_id,
    property_id=property_id,
    amount=850.00,
    description="Nettokaltmiete Januar 2026"
)
```

### 🔧 Wartungs-Management (wartung/)
```python
from wartung.maintenance import MaintenanceManager

# Wartungstermin planen
maintenance_manager = MaintenanceManager()
maintenance_id = maintenance_manager.schedule_maintenance(
    property_id=property_id,
    task_type="Heizung",
    priority="high",
    contractor="Heizung GmbH"
)
```

## 📊 Dashboard

```python
from reports.dashboard import Dashboard

# Dashboard mit KPI-Anzeige
dashboard = Dashboard()
dashboard.show_kpis()
dashboard.show_upcoming_maintenance()
dashboard.show_payment_overview()
```

## 🏷️ Datenbank-Schema

| Tabelle | Beschreibung |
|---------|-------------|
| `properties` | Immobilien-Objekte |
| `units` | Wohneinheiten/Wohnungen |
| `tenants` | Mieter-Informationen |
| `contracts` | Mietverträge |
| `payments` | Zahlungen |
| `invoices` | Rechnungen |
| `maintenance` | Wartungsarbeiten |
| `contractors` | Handwerker/Firmen |

## 🔧 Konfiguration

```python
# config.py anpassen
DATABASE_URL = "sqlite:///hausverwaltung.db"
BANK_INTEGRATION = True
INVOICE_TEMPLATE = "modern"
MAINTENANCE_REMINDER_DAYS = 7
```

## 📈 Features

### ✅ Automatische Features
- **Automatische Mahnungen** bei Zahlungsrückstand
- **Wartungs-Erinnerungen** basierend auf Zeitplänen  
- **Jahresabrechnungen** mit Heizkosten-Verteilung
- **Bank-Integration** für Zahlungseingänge
- **PDF-Rechnungserstellung** mit automatischen Vorlagen

### 🏆 Reporting
- **Dashboard** mit wichtigen KPIs
- **Mieten-Auswertung** pro Objekt
- **Wartungs-Kosten** Anaylse
- **Zahlungs-Statistiken** 

## 🗓️ Roadmap

- [ ] **Web-Dashboard** (Flask/FastAPI)
- [ ] **Mobile App** für Wartungs-Meldungen
- [ ] **E-Mail-Integration** für automatische Mails
- [ ] **Kalender-Integration** (Google Calendar, Outlook)
- [ ] **Banking-API** für autom. Zahlungserfassung
- [ ] **Multi-Language** Support (Deutsch/Englisch)

## 👨‍💻 Entwicklungs-Setup

```bash
# Entwicklungsumgebung
git checkout -b feature/new-feature
python main.py --test-mode
# Nach Entwicklung:
git commit -m "feat: Add new feature"
git push origin feature/new-feature
```

## 📄 Lizenz

MIT License - frei für nicht-kommerzielle und kommerzielle Nutzung.

## 🤝 Beitragen

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen commiten (`git commit -m 'feat: Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request öffnen

---

*Effiziente Hausverwaltung für die moderne Ära* 🏢⚡