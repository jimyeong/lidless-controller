CREATE TABLE public.raven_reports (
    id serial NOT NULL,
    area varchar(50) NOT NULL,
    payload JSONB NOT NULL,
    created_at timestampwithTimeZone Default CURRENT_TIMESTAMP
    CONSTRAINT raven_reports_pk PRIMARY KEY (id)
);