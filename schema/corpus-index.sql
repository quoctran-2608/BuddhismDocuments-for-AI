PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_state (
    corpus TEXT PRIMARY KEY,
    repo_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    indexed_at TEXT NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0,
    relation_count INTEGER NOT NULL DEFAULT 0,
    variant_count INTEGER NOT NULL DEFAULT 0,
    lemma_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS search_index_state (
    component TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    rebuilt_at TEXT NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS works (
    corpus TEXT NOT NULL,
    work_id TEXT NOT NULL,
    language TEXT,
    collection_name TEXT,
    title TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    source_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    PRIMARY KEY (corpus, work_id, source_path)
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    corpus TEXT NOT NULL,
    language TEXT,
    collection_name TEXT,
    work_id TEXT,
    segment_id TEXT,
    title TEXT,
    raw_text TEXT NOT NULL,
    norm_text TEXT NOT NULL,
    folded_text TEXT NOT NULL,
    compact_text TEXT NOT NULL,
    lemma_text TEXT NOT NULL DEFAULT '',
    source_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    witness TEXT,
    relation_ids TEXT NOT NULL DEFAULT '[]',
    sequence_no INTEGER NOT NULL DEFAULT 0,
    UNIQUE (corpus, source_path, segment_id, language, witness)
);

CREATE INDEX IF NOT EXISTS records_lookup
ON records(corpus, work_id, segment_id, language);

CREATE INDEX IF NOT EXISTS records_context
ON records(corpus, work_id, source_path, sequence_no);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY,
    corpus TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    source_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    UNIQUE(corpus, relation_type, from_id, to_id, source_path)
);

CREATE INDEX IF NOT EXISTS relations_from ON relations(from_id);
CREATE INDEX IF NOT EXISTS relations_to ON relations(to_id);

CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY,
    corpus TEXT NOT NULL,
    work_id TEXT,
    segment_id TEXT,
    lemma TEXT,
    reading TEXT NOT NULL,
    witnesses TEXT,
    variant_type TEXT,
    confidence REAL,
    notes TEXT,
    source_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    evidence_class TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS variants_segment
ON variants(work_id, segment_id);

CREATE TABLE IF NOT EXISTS lemmas (
    id INTEGER PRIMARY KEY,
    corpus TEXT NOT NULL,
    language TEXT NOT NULL,
    work_id TEXT,
    segment_id TEXT,
    surface TEXT NOT NULL,
    lemma TEXT NOT NULL,
    pos TEXT,
    morphology_json TEXT NOT NULL DEFAULT '{}',
    source_path TEXT NOT NULL,
    source_sha TEXT NOT NULL,
    evidence_class TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS lemmas_surface ON lemmas(surface);
CREATE INDEX IF NOT EXISTS lemmas_lemma ON lemmas(lemma);

CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
    raw_text,
    norm_text,
    folded_text,
    compact_text,
    lemma_text,
    title,
    content='records',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 0'
);

CREATE VIRTUAL TABLE IF NOT EXISTS records_cjk_fts USING fts5(
    search_text,
    content='',
    tokenize='trigram'
);
