CREATE TABLE IF NOT EXISTS sales_leads (
    id SERIAL PRIMARY KEY,
    lead_id TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    service TEXT NOT NULL,
    message TEXT NOT NULL,
    summary TEXT NOT NULL,
    service_category TEXT NOT NULL,
    urgency TEXT NOT NULL CHECK (urgency IN ('Low', 'Medium', 'High')),
    next_action TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
