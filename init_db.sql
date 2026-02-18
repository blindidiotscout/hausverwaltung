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
);

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
);

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
);

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
);

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
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER,
    property_id INTEGER,
    invoice_number TEXT NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    due_date DATE,
    amount REAL NOT NULL,
    mwst_rate REAL DEFAULT 0.20,
    mwst_amount REAL,
    total_amount REAL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants (id),
    FOREIGN KEY (property_id) REFERENCES properties (id)
);

CREATE TABLE IF NOT EXISTS maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    unit_id INTEGER,
    task_type TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'planned',
    scheduled_date DATE,
    completed_date DATE,
    cost REAL DEFAULT 0,
    contractor_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties (id),
    FOREIGN KEY (unit_id) REFERENCES units (id)
);

CREATE TABLE IF NOT EXISTS contractors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    trade TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
