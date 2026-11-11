
CREATE TABLE retail_transactions (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    invoice TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    price NUMERIC(12, 3) NOT NULL,
    customer_id BIGINT,
    country TEXT NOT NULL,
    source_sheet TEXT NOT NULL,

    CONSTRAINT chk_source_sheet
        CHECK (
            source_sheet IN (
                'Year 2009-2010',
                'Year 2010-2011'
            )
        )
);
