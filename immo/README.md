# Immobilien-Verwaltung (immo)

## PropertyManager

Hauptklasse für die Verwaltung von Immobilien-Objekten und Wohneinheiten.

### Features

- ✅ **Property-Verwaltung**: Immobilien hinzufügen, bearbeiten, löschen
- ✅ **Unit-Management**: Wohneinheiten pro Immobilie verwalten
- ✅ **Auslastung-Tracking**: Automatische Berechnung der Vollvermietung
- ✅ **Suche**: Immobilien nach Name/Adresse/Standort suchen
- ✅ **Statistiken**: Umfassende Übersichten und KPIs

### Verwendung

```python
from immo.properties import PropertyManager

# Property Manager Initialisierung
manager = PropertyManager("/path/to/database.db")

# Neue Immobilie
property_id = manager.add_property(
    name="Wohnhaus Musterstraße",
    address="Musterstraße 123",
    city="Wien",
    zip_code="1010",
    property_type="residential",
    units=20,
    total_area=1500.0,
    purchase_price=1200000.00
)

# Wohneinheit hinzufügen
unit_id = manager.add_unit(
    property_id=property_id,
    unit_number="Top 7",
    floor=3,
    area=75.0,
    rent_netto=900.00,
    rent_brutto=1080.00
)

# Auslastung berechnen
occupancy_rate = manager.get_occupancy_rate(property_id)
print(f"Auslastung: {occupancy_rate:.1f}%")
```

### Datenbank-Schema

#### properties
- `id` - Primärschlüssel
- `name` - Objektname
- `address`, `city`, `zip_code` - Adresse
- `property_type` - 'residential' oder 'commercial'
- `units` - Anzahl Wohneinheiten
- `total_area` - Gesamtfläche in m²
- `purchase_price`, `purchase_date` - Kaufdaten

#### units
- `id` - Primärschlüssel
- `property_id` - Fremdschlüssel zu properties
- `unit_number` - Wohnungsnummer
- `floor`, `area` - Stockwerk und Größe
- `rent_netto`, `rent_brutto` - Mietpreise
- `status` - 'vacant', 'occupied', 'maintenance'
- `tenant_id` - Mieter-Zuordnung

### Methoden

#### Property-Management
- `add_property()` - Neue Immobilie hinzufügen
- `get_property()` - Einzelne Immobilie abrufen
- `get_all_properties()` - Alle Immobilien
- `update_property()` - Aktualisieren
- `delete_property()` - Löschen (nur ohne aktive Verträge)
- `search_properties()` - Suche nach Name/Adresse

#### Unit-Management  
- `add_unit()` - Neue Wohneinheit hinzufügen
- `get_units_for_property()` - Einheiten einer Immobilie
- `get_unit_occupancy_stats()` - Übersicht der Status

#### Analytics
- `get_properties_summary()` - Statistische Übersicht
- `get_occupancy_rate()` - Auslastung einer Immobilie

### Validierung

- ✅ **Eindeutige Unit-Nummern** pro Immobilie
- ✅ **Cascade-Deletes** für verwaiste Einheiten
- ✅ **Aktive Verträge** verhindern Property-Löschung
- ✅ **Datenintegrität** durch Foreign Keys