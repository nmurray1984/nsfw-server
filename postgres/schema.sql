create table ContributedImage
(
    ID INT GENERATED ALWAYS AS IDENTITY,
    url TEXT,
    created_date timestamptz not null default now()
)

