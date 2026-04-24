-- ============================================================
-- TicketVault — Seed Data
-- Run AFTER schema.sql
-- ============================================================

INSERT INTO cities (name, slug) VALUES
  ('Mumbai',     'mumbai'),
  ('Delhi',      'delhi'),
  ('Bangalore',  'bangalore'),
  ('Hyderabad',  'hyderabad'),
  ('Chennai',    'chennai'),
  ('Kolkata',    'kolkata'),
  ('Pune',       'pune'),
  ('Ahmedabad',  'ahmedabad'),
  ('Jaipur',     'jaipur'),
  ('Lucknow',    'lucknow'),
  ('Kochi',      'kochi'),
  ('Chandigarh', 'chandigarh'),
  ('Goa',        'goa'),
  ('Surat',      'surat'),
  ('Indore',     'indore')
ON CONFLICT (name) DO NOTHING;
