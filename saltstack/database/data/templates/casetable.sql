CREATE TABLE public.cases
(
    case_nr character varying NOT NULL,
    "Event" text,
    "Description" text,
    "Status" character varying,
    created timestamp without time zone,
    last_updated timestamp without time zone,
    technician character varying,
    "Sender_Device" character varying,
    "Solution" text[],
    PRIMARY KEY (last_updated)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.cases
    OWNER to netbox;

