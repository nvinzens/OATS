CREATE TABLE public.cases
(
    case_nr character varying NOT NULL,
    event text,
    description text,
    status character varying,
    created timestamp without time zone,
    last_updated timestamp without time zone,
    technician character varying,
    sender_Device character varying,
    solution text[],
    PRIMARY KEY (last_updated)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.cases
    OWNER to netbox;

