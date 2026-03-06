// Nodes and Constraint

CREATE CONSTRAINT user_id_unique
IF NOT EXISTS
FOR(u: User)
REQUIRE u.id IS UNIQUE

// Symptom Node

CREATE CONSTRAINT symptom_name_unique
IF NOT EXISTS
FOR (s:Symptom)
REQUIRE s.name IS UNIQUE;

// medication

CREATE CONSTRAINT medication_name_unique
IF NOT EXISTS
FOR (m:Medication)
REQUIRE m.name IS UNIQUE;

// trigger node - what cause the sympton or health issue

CREATE CONSTRAINT trigger_name_unique
IF NOT EXISTS
FOR (t:Trigger)
REQUIRE t.name IS UNIQUE;

// lifestyle node - which thing has caused it

CREATE CONSTRAINT lifestyle_type_unique
IF NOT EXISTS
FOR (l:Lifestyle)
REQUIRE l.type IS UNIQUE;

// visit node - doctor visit

CREATE CONSTRAINT visit_id_unique
IF NOT EXISTS
FOR (v:Visit)
REQUIRE v.id IS UNIQUE;

// indexing - for fast retrivel

CREATE INDEX symptom_index
IF NOT EXISTS
FOR (s:Symptom)
ON (s.name);

CREATE INDEX medication_index
IF NOT EXISTS
FOR (m:Medication)
ON (m.name);

CREATE INDEX trigger_index
IF NOT EXISTS
FOR (t:Trigger)
ON (t.name);

CREATE INDEX lifestyle_index
IF NOT EXISTS
FOR (l:Lifestyle)
ON (l.type);