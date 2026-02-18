#!/usr/bin/env python3
"""
Hausverwaltung Web Frontend - FastAPI
"""

from fastapi import FastAPI, Request, Form, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
from datetime import datetime
from typing import Optional
import shutil
import uuid
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "hausverwaltung.db"
DOCS_DIR = BASE_DIR / "documents"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure directories exist
DOCS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Hausverwaltung", description="Web Frontend für Immobilienverwaltung")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Database helper
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== DASHBOARD ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = get_db()
    
    # KPIs
    properties_count = conn.execute("SELECT COUNT(*) as cnt FROM properties").fetchone()["cnt"]
    tenants_count = conn.execute("SELECT COUNT(*) as cnt FROM tenants").fetchone()["cnt"]
    units_vacant = conn.execute("SELECT COUNT(*) as cnt FROM units WHERE status = 'vacant'").fetchone()["cnt"]
    units_occupied = conn.execute("SELECT COUNT(*) as cnt FROM units WHERE status = 'occupied'").fetchone()["cnt"]
    
    # Offene Rechnungen
    open_invoices = conn.execute("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total 
        FROM invoices WHERE status = 'open'
    """).fetchone()
    
    # Upcoming Maintenance
    maintenance_upcoming = conn.execute("""
        SELECT m.*, p.name as property_name, p.address
        FROM maintenance m
        LEFT JOIN properties p ON m.property_id = p.id
        WHERE m.status IN ('planned', 'scheduled')
        ORDER BY m.scheduled_date ASC
        LIMIT 5
    """).fetchall()
    
    # Recent Payments
    recent_payments = conn.execute("""
        SELECT p.*, t.first_name, t.last_name
        FROM payments p
        LEFT JOIN tenants t ON p.tenant_id = t.id
        ORDER BY p.payment_date DESC
        LIMIT 5
    """).fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "properties_count": properties_count,
        "tenants_count": tenants_count,
        "units_vacant": units_vacant,
        "units_occupied": units_occupied,
        "open_invoices_count": open_invoices["cnt"],
        "open_invoices_total": open_invoices["total"],
        "maintenance_upcoming": maintenance_upcoming,
        "recent_payments": recent_payments,
    })

# ==================== PROPERTIES ====================

@app.get("/properties", response_class=HTMLResponse)
async def properties_list(request: Request):
    conn = get_db()
    properties = conn.execute("""
        SELECT p.*, 
               (SELECT COUNT(*) FROM units WHERE property_id = p.id) as unit_count,
               (SELECT COUNT(*) FROM units WHERE property_id = p.id AND status = 'occupied') as occupied_count
        FROM properties p
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return templates.TemplateResponse("properties/list.html", {"request": request, "properties": properties})

@app.get("/properties/new", response_class=HTMLResponse)
async def property_new_form(request: Request):
    return templates.TemplateResponse("properties/form.html", {"request": request, "property": None, "is_edit": False})

@app.post("/properties/new")
async def property_create(
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    zip_code: str = Form(""),
    property_type: str = Form("residential"),
    units: int = Form(1),
    total_area: float = Form(0),
    purchase_price: float = Form(0),
):
    conn = get_db()
    conn.execute("""
        INSERT INTO properties (name, address, city, zip_code, property_type, units, total_area, purchase_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, address, city, zip_code, property_type, units, total_area, purchase_price))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/properties", status_code=303)

@app.get("/properties/{property_id}", response_class=HTMLResponse)
async def property_detail(request: Request, property_id: int):
    conn = get_db()
    property = conn.execute("SELECT * FROM properties WHERE id = ?", (property_id,)).fetchone()
    if not property:
        raise HTTPException(404, "Property not found")
    
    units = conn.execute("""
        SELECT u.*, t.first_name, t.last_name, t.id as tenant_id
        FROM units u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.property_id = ?
        ORDER BY u.unit_number
    """, (property_id,)).fetchall()
    
    # Available tenants (not assigned to any unit)
    available_tenants = conn.execute("""
        SELECT id, first_name, last_name 
        FROM tenants 
        WHERE id NOT IN (SELECT tenant_id FROM units WHERE tenant_id IS NOT NULL)
        ORDER BY last_name, first_name
    """).fetchall()
    
    conn.close()
    return templates.TemplateResponse("properties/detail.html", {
        "request": request, 
        "property": property, 
        "units": units,
        "available_tenants": available_tenants
    })

# ==================== UNITS ====================

@app.get("/properties/{property_id}/units/new", response_class=HTMLResponse)
async def unit_new_form(request: Request, property_id: int):
    conn = get_db()
    property = conn.execute("SELECT id, name FROM properties WHERE id = ?", (property_id,)).fetchone()
    conn.close()
    if not property:
        raise HTTPException(404, "Property not found")
    return templates.TemplateResponse("units/form.html", {
        "request": request, 
        "property": property, 
        "unit": None, 
        "is_edit": False
    })

@app.post("/properties/{property_id}/units/new")
async def unit_create(
    property_id: int,
    unit_number: str = Form(...),
    floor: int = Form(None),
    area: float = Form(0),
    rent_netto: float = Form(0),
    rent_brutto: float = Form(0),
    status: str = Form("vacant"),
):
    conn = get_db()
    conn.execute("""
        INSERT INTO units (property_id, unit_number, floor, area, rent_netto, rent_brutto, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (property_id, unit_number, floor, area, rent_netto, rent_brutto, status))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.get("/properties/{property_id}/units/{unit_id}/edit", response_class=HTMLResponse)
async def unit_edit_form(request: Request, property_id: int, unit_id: int):
    conn = get_db()
    property = conn.execute("SELECT id, name FROM properties WHERE id = ?", (property_id,)).fetchone()
    unit = conn.execute("SELECT * FROM units WHERE id = ? AND property_id = ?", (unit_id, property_id)).fetchone()
    conn.close()
    if not property or not unit:
        raise HTTPException(404, "Not found")
    return templates.TemplateResponse("units/form.html", {
        "request": request, 
        "property": property, 
        "unit": unit, 
        "is_edit": True
    })

@app.post("/properties/{property_id}/units/{unit_id}/edit")
async def unit_update(
    property_id: int,
    unit_id: int,
    unit_number: str = Form(...),
    floor: int = Form(None),
    area: float = Form(0),
    rent_netto: float = Form(0),
    rent_brutto: float = Form(0),
    status: str = Form("vacant"),
):
    conn = get_db()
    conn.execute("""
        UPDATE units SET unit_number=?, floor=?, area=?, rent_netto=?, rent_brutto=?, status=?
        WHERE id=? AND property_id=?
    """, (unit_number, floor, area, rent_netto, rent_brutto, status, unit_id, property_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.post("/properties/{property_id}/units/{unit_id}/delete")
async def unit_delete(property_id: int, unit_id: int):
    conn = get_db()
    conn.execute("DELETE FROM units WHERE id = ? AND property_id = ?", (unit_id, property_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.post("/properties/{property_id}/units/{unit_id}/assign-tenant")
async def unit_assign_tenant(
    property_id: int,
    unit_id: int,
    tenant_id: int = Form(None),
):
    conn = get_db()
    if tenant_id:
        conn.execute("""
            UPDATE units SET tenant_id = ?, status = 'occupied' 
            WHERE id = ? AND property_id = ?
        """, (tenant_id, unit_id, property_id))
    else:
        conn.execute("""
            UPDATE units SET tenant_id = NULL, status = 'vacant' 
            WHERE id = ? AND property_id = ?
        """, (unit_id, property_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.post("/properties/{property_id}/units/{unit_id}/remove-tenant")
async def unit_remove_tenant(property_id: int, unit_id: int):
    conn = get_db()
    conn.execute("""
        UPDATE units SET tenant_id = NULL, status = 'vacant' 
        WHERE id = ? AND property_id = ?
    """, (unit_id, property_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.get("/properties/{property_id}/edit", response_class=HTMLResponse)
async def property_edit_form(request: Request, property_id: int):
    conn = get_db()
    property = conn.execute("SELECT * FROM properties WHERE id = ?", (property_id,)).fetchone()
    conn.close()
    if not property:
        raise HTTPException(404, "Property not found")
    return templates.TemplateResponse("properties/form.html", {"request": request, "property": property, "is_edit": True})

@app.post("/properties/{property_id}/edit")
async def property_update(
    property_id: int,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    zip_code: str = Form(""),
    property_type: str = Form("residential"),
    units: int = Form(1),
    total_area: float = Form(0),
    purchase_price: float = Form(0),
):
    conn = get_db()
    conn.execute("""
        UPDATE properties SET name=?, address=?, city=?, zip_code=?, property_type=?, units=?, total_area=?, purchase_price=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (name, address, city, zip_code, property_type, units, total_area, purchase_price, property_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/properties/{property_id}", status_code=303)

@app.post("/properties/{property_id}/delete")
async def property_delete(property_id: int):
    conn = get_db()
    conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/properties", status_code=303)

# ==================== TENANTS ====================

@app.get("/tenants", response_class=HTMLResponse)
async def tenants_list(request: Request):
    conn = get_db()
    tenants = conn.execute("""
        SELECT t.*, u.unit_number, p.name as property_name
        FROM tenants t
        LEFT JOIN units u ON t.id = u.tenant_id
        LEFT JOIN properties p ON u.property_id = p.id
        ORDER BY t.last_name, t.first_name
    """).fetchall()
    conn.close()
    return templates.TemplateResponse("tenants/list.html", {"request": request, "tenants": tenants})

@app.get("/tenants/new", response_class=HTMLResponse)
async def tenant_new_form(request: Request):
    return templates.TemplateResponse("tenants/form.html", {"request": request, "tenant": None, "is_edit": False})

@app.post("/tenants/new")
async def tenant_create(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    birth_date: str = Form(""),
    address: str = Form(""),
    iban: str = Form(""),
    bic: str = Form(""),
):
    conn = get_db()
    conn.execute("""
        INSERT INTO tenants (first_name, last_name, email, phone, birth_date, address, iban, bic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, email, phone, birth_date or None, address, iban, bic))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tenants", status_code=303)

@app.get("/tenants/{tenant_id}/edit", response_class=HTMLResponse)
async def tenant_edit_form(request: Request, tenant_id: int):
    conn = get_db()
    tenant = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
    conn.close()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    return templates.TemplateResponse("tenants/form.html", {"request": request, "tenant": tenant, "is_edit": True})

@app.post("/tenants/{tenant_id}/edit")
async def tenant_update(
    tenant_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    birth_date: str = Form(""),
    address: str = Form(""),
    iban: str = Form(""),
    bic: str = Form(""),
):
    conn = get_db()
    conn.execute("""
        UPDATE tenants SET first_name=?, last_name=?, email=?, phone=?, birth_date=?, address=?, iban=?, bic=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (first_name, last_name, email, phone, birth_date or None, address, iban, bic, tenant_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tenants", status_code=303)

@app.post("/tenants/{tenant_id}/delete")
async def tenant_delete(tenant_id: int):
    conn = get_db()
    conn.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tenants", status_code=303)

# ==================== INVOICES ====================

@app.get("/invoices", response_class=HTMLResponse)
async def invoices_list(request: Request, status: str = Query(None)):
    conn = get_db()
    query = """
        SELECT i.*, t.first_name, t.last_name, p.name as property_name
        FROM invoices i
        LEFT JOIN tenants t ON i.tenant_id = t.id
        LEFT JOIN properties p ON i.property_id = p.id
    """
    params = []
    if status and status != "all":
        query += " WHERE i.status = ?"
        params.append(status)
    query += " ORDER BY i.invoice_date DESC"
    
    invoices = conn.execute(query, params).fetchall()
    conn.close()
    return templates.TemplateResponse("invoices/list.html", {"request": request, "invoices": invoices, "filter_status": status})

@app.get("/invoices/new", response_class=HTMLResponse)
async def invoice_new_form(request: Request):
    conn = get_db()
    tenants = conn.execute("SELECT id, first_name, last_name FROM tenants ORDER BY last_name").fetchall()
    properties = conn.execute("SELECT id, name, address FROM properties ORDER BY name").fetchall()
    conn.close()
    return templates.TemplateResponse("invoices/form.html", {
        "request": request, 
        "invoice": None, 
        "is_edit": False,
        "tenants": tenants,
        "properties": properties
    })

@app.post("/invoices/new")
async def invoice_create(
    tenant_id: int = Form(None),
    property_id: int = Form(None),
    invoice_number: str = Form(...),
    invoice_date: str = Form(...),
    due_date: str = Form(""),
    amount: float = Form(...),
    mwst_rate: float = Form(0.20),
    description: str = Form(""),
):
    mwst_amount = amount * mwst_rate
    total_amount = amount + mwst_amount
    
    conn = get_db()
    conn.execute("""
        INSERT INTO invoices (tenant_id, property_id, invoice_number, invoice_date, due_date, amount, mwst_rate, mwst_amount, total_amount, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tenant_id, property_id, invoice_number, invoice_date, due_date or None, amount, mwst_rate, mwst_amount, total_amount, description))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/invoices", status_code=303)

@app.post("/invoices/{invoice_id}/status")
async def invoice_update_status(invoice_id: int, status: str = Form(...)):
    conn = get_db()
    conn.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, invoice_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/invoices", status_code=303)

# ==================== MAINTENANCE ====================

@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance_list(request: Request, status: str = Query(None)):
    conn = get_db()
    query = """
        SELECT m.*, p.name as property_name, p.address, c.name as contractor_name
        FROM maintenance m
        LEFT JOIN properties p ON m.property_id = p.id
        LEFT JOIN contractors c ON m.contractor_id = c.id
    """
    params = []
    if status and status != "all":
        query += " WHERE m.status = ?"
        params.append(status)
    query += " ORDER BY m.scheduled_date ASC, m.priority DESC"
    
    maintenance = conn.execute(query, params).fetchall()
    conn.close()
    return templates.TemplateResponse("maintenance/list.html", {"request": request, "maintenance": maintenance, "filter_status": status})

@app.get("/maintenance/new", response_class=HTMLResponse)
async def maintenance_new_form(request: Request):
    conn = get_db()
    properties = conn.execute("SELECT id, name, address FROM properties ORDER BY name").fetchall()
    contractors = conn.execute("SELECT id, name, trade FROM contractors ORDER BY name").fetchall()
    conn.close()
    return templates.TemplateResponse("maintenance/form.html", {
        "request": request, 
        "maintenance": None, 
        "is_edit": False,
        "properties": properties,
        "contractors": contractors
    })

@app.post("/maintenance/new")
async def maintenance_create(
    property_id: int = Form(None),
    unit_id: int = Form(None),
    task_type: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    scheduled_date: str = Form(""),
    contractor_id: int = Form(None),
    notes: str = Form(""),
):
    conn = get_db()
    conn.execute("""
        INSERT INTO maintenance (property_id, unit_id, task_type, description, priority, scheduled_date, contractor_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (property_id, unit_id, task_type, description, priority, scheduled_date or None, contractor_id, notes))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/maintenance", status_code=303)

@app.post("/maintenance/{maintenance_id}/status")
async def maintenance_update_status(maintenance_id: int, status: str = Form(...)):
    conn = get_db()
    if status == "completed":
        conn.execute("UPDATE maintenance SET status = ?, completed_date = CURRENT_DATE WHERE id = ?", (status, maintenance_id))
    else:
        conn.execute("UPDATE maintenance SET status = ? WHERE id = ?", (status, maintenance_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/maintenance", status_code=303)

# ==================== CONTRACTORS ====================

@app.get("/contractors", response_class=HTMLResponse)
async def contractors_list(request: Request):
    conn = get_db()
    contractors = conn.execute("SELECT * FROM contractors ORDER BY name").fetchall()
    conn.close()
    return templates.TemplateResponse("contractors/list.html", {"request": request, "contractors": contractors})

@app.get("/contractors/new", response_class=HTMLResponse)
async def contractor_new_form(request: Request):
    return templates.TemplateResponse("contractors/form.html", {"request": request, "contractor": None, "is_edit": False})

@app.post("/contractors/new")
async def contractor_create(
    name: str = Form(...),
    company: str = Form(""),
    trade: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    notes: str = Form(""),
):
    conn = get_db()
    conn.execute("""
        INSERT INTO contractors (name, company, trade, email, phone, address, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, company, trade, email, phone, address, notes))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/contractors", status_code=303)

@app.post("/contractors/{contractor_id}/delete")
async def contractor_delete(contractor_id: int):
    conn = get_db()
    conn.execute("DELETE FROM contractors WHERE id = ?", (contractor_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/contractors", status_code=303)

# ==================== TENANT DETAIL & DOCUMENTS ====================

@app.get("/tenants/{tenant_id}", response_class=HTMLResponse)
async def tenant_detail(request: Request, tenant_id: int):
    conn = get_db()
    tenant = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    # Documents for this tenant
    documents = conn.execute("""
        SELECT d.*, p.name as property_name
        FROM documents d
        LEFT JOIN properties p ON d.property_id = p.id
        WHERE d.tenant_id = ?
        ORDER BY d.created_at DESC
    """, (tenant_id,)).fetchall()
    
    # Assigned unit/property
    unit = conn.execute("""
        SELECT u.*, p.name as property_name, p.address as property_address
        FROM units u
        LEFT JOIN properties p ON u.property_id = p.id
        WHERE u.tenant_id = ?
    """, (tenant_id,)).fetchone()
    
    # Available properties for document assignment
    properties = conn.execute("SELECT id, name FROM properties ORDER BY name").fetchall()
    
    conn.close()
    return templates.TemplateResponse("tenants/detail.html", {
        "request": request, 
        "tenant": tenant, 
        "documents": documents,
        "unit": unit,
        "properties": properties
    })

@app.post("/tenants/{tenant_id}/documents/upload")
async def document_upload(
    tenant_id: int,
    document_type: str = Form(...),
    title: str = Form(""),
    property_id: int = Form(None),
    notes: str = Form(""),
    file: UploadFile = File(...),
):
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    unique_filename = f"{tenant_id}_{document_type}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = UPLOADS_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = file_path.stat().st_size
    
    conn = get_db()
    conn.execute("""
        INSERT INTO documents (tenant_id, property_id, document_type, title, filename, file_path, file_size, mime_type, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tenant_id, property_id, document_type, title or file.filename, file.filename, str(file_path), file_size, file.content_type, notes))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=f"/tenants/{tenant_id}", status_code=303)

@app.get("/documents/{document_id}/download")
async def document_download(document_id: int):
    conn = get_db()
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.close()
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    file_path = Path(doc["file_path"])
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        path=file_path,
        filename=doc["filename"],
        media_type=doc["mime_type"] or "application/octet-stream"
    )

@app.post("/documents/{document_id}/delete")
async def document_delete(document_id: int):
    conn = get_db()
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    if doc:
        # Delete file
        file_path = Path(doc["file_path"])
        if file_path.exists():
            file_path.unlink()
        tenant_id = doc["tenant_id"]
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
        conn.close()
        return RedirectResponse(url=f"/tenants/{tenant_id}", status_code=303)
    conn.close()
    raise HTTPException(404, "Document not found")

# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)