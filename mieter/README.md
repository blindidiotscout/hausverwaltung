# Mieter-Verwaltung (mieter)

## TenantManager

Umfassende Verwaltung von Mietern, Verträgen und Zahlungsdaten.

### Features

- ✅ **Mieter-Management**: Registrieren, bearbeiten, deaktivieren
- ✅ **Vertrags-Verwaltung**: Mietverträge mit Automatik-Ablauf
- ✅ **Zahlungs-Tracking**: Zahlungen und Rückstände überwachen
- ✅ **Validierung**: E-Mail, Telefon, IBAN-Prüfung
- ✅ **Suche**: Mieter nach Name oder Kontaktdaten finden
- ✅ **Automatik**: Vertragsende bei Kündigung

### Verwendung

```python
from mieter.tenants import TenantManager

# Tenant Manager initialisieren
tenant_manager = TenantManager("/path/to/database.db")

# Neuen Mieter hinzufügen
tenant_id = tenant_manager.add_tenant(
    first_name="Max",
    last_name="Mustermann",
    email="max@example.com",
    phone="+43123456789",
    iban="AT611904300234573201"
)

# Mieter-Vertrag beenden
tenant_manager.terminate_contract(tenant_id, "2026-03-31")
```

### Datenbank-Schema

#### tenants
- `id` - Primärschlüssel
- `first_name`, `last_name` - Name
- `email`, `phone` - Kontaktdaten
- `birth_date` - Geburtsdatum
- `address` - Adresse
- `iban`, `bic` - Bankdaten
- `contract_start`, `contract_end` - Vertragsdaten

#### contracts
- `id` - Primärschlüssel
- `tenant_id`, `unit_id` - Zuordnungen
- `contract_start`, `contract_end` - Laufzeit
- `rent_netto`, `rent_brutto` - Mietpreise  
- `deposit` - Kaution
- `terms` - Vertragskonditionen
- `status` - 'active', 'ended', 'pending'

#### payments
- `id` - Primärschlüssel
- `tenant_id` - Mieter-Zuordnung
- `amount` - Betrag
- `payment_date` - Zahlungsdatum
- `payment_method` - Zahlungsart
- `status` - 'completed', 'pending', 'failed'

### Validierung

#### E-Mail
```python
email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
```

#### Telefon
```python
phone_regex = r"^\+?[1-9]\d{1,14}$"
```

#### IBAN
- Längenprüfung (15-34 Zeichen)
- Länderkode-Validierung
- Ziffern-Pattern-Prüfung

### Methoden

#### Mieter-Verwaltung
- `add_tenant()` - Neuen Mieter registrieren
- `get_tenant()` - Einzelner Mieter abrufen  
- `get_all_tenants()` - Alle Mieter (oder nur aktive)
- `update_tenant()` - Mieterdaten bearbeiten
- `search_tenants()` - Volltext-Suche

#### Vertrags-Management
- `terminate_contract()` - Vertrag beenden
- `get_active_tenants_by_property()` - Aktive Mieter je Objekt
- `calculate_total_rent_for_property()` - Gesamtrendite

#### Analytics
- `get_tenants_summary()` - Statistische Übersicht
- Mieter-Statistiken nach Status, mit/ohne Kontaktdaten

### Validierungs-Features

#### Datenqualität
- ✅ **Pflichtfelder**: Vorname, Nachname erforderlich
- ✅ **Eindeutige E-Mails**: Warnung bei Duplikaten
- ✅ **Flexible Kontakte**: Telefon/E-Mail optional
- ✅ **Bankdaten**: IBAN/BIC für SEPA-Lastschriften

#### Geschäfts-Logik
- ✅ **Vertragshistorie**: Automatische Status-Verwaltung
- ✅ **Zeitstempel**: created_at, updated_at
- ✅ **Cascade-Deletes**: Bereinigungen bei Mieter-Löschung
- ✅ **Active-Filter**: Nur aktive Verträge standardmäßig

### Best Practices

#### Mieter-Registration
```python
# Vollständige Registrierung
tenant_id = manager.add_tenant(
    first_name="Max",
    last_name="Mustermann", 
    email="max@example.com",     # Für Mahnungen
    phone="+43123456789",       # Kontaktaufnahme
    address="Musterstraße 123", # Für Dokumente
    iban="AT611904300234573201",  # SEPA-Lastschriften
    contract_start="2026-01-01"  # Vertragsbeginn
)
```

#### Vertrag-Management
```python
# Aktive Mieter eines Objekts
active_tenants = manager.get_active_tenants_by_property(property_id)

# Gesamteinnahmen pro Objekt (monatlich)
monthly_rent = manager.calculate_total_rent_for_property(property_id)
```

#### Suche und Filter
```python
# Mieter nach Namen finden
results = manager.search_tenants("Mustermann")

# Statistische Übersicht
summary = manager.get_tenants_summary()
print(f"Mieter: {summary['total_tenants']} | Mit E-Mail: {summary['with_email']}")
```