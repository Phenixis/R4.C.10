CREATE TABLE pays_continent (
    country VARCHAR(50) PRIMARY KEY,
    continent VARCHAR(50)
);


COPY pays_continent(continent, country)
FROM '/home/etudiant/Documents/Cours/R4.C.10/Countries-Continents.csv'
WITH (
  FORMAT csv,
  HEADER true,
  DELIMITER ','
);

SELECT continent, COUNT(country) from pays_continent GROUP BY continent;

SELECT country from pays_continent WHERE LENGTH(country) < 5;

