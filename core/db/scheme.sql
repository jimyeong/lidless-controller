CREATE TABLE public.raven_reports (
    report_id serial NOT NULL,
    area TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at timestampwithTimeZone Default CURRENT_TIMESTAMP
    CONSTRAINT raven_reports_pk PRIMARY KEY (report_id)
);