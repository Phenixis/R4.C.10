DROP SCHEMA IF EXISTS traitement_publication CASCADE;
CREATE SCHEMA traitement_publication;
SET SCHEMA 'traitement_publication';

CREATE TABLE pays_continent (
    pays VARCHAR(50) PRIMARY KEY,
    continent VARCHAR(50)
);


COPY pays_continent(continent, pays)
FROM '/home/etudiant/Documents/Cours/R4.C.10/Countries-Continents.csv'
WITH (
  FORMAT csv,
  HEADER true,
  DELIMITER ','
);

SELECT continent, COUNT(pays) as nbpays from pays_continent GROUP BY continent; -- Nombre de pays par continent

SELECT continent, COUNT(pays) as nbpays from pays_continent GROUP BY continent ORDER BY nbpays DESC LIMIT 1; -- Nombre de pays par continent

CREATE TABLE ville (
    id integer PRIMARY KEY,
    ville VARCHAR(50),
    ville_ascii VARCHAR(50),
    latitude float,
    longitude float,
    pays VARCHAR(50),
    iso2 char(2),
    iso3 char(3),
    nom_region VARCHAR(100),
    capital VARCHAR(7),
    pop FLOAT
);

ALTER TABLE ville ALTER COLUMN pop DROP NOT NULL;

COPY ville(ville, ville_ascii, latitude, longitude, pays, iso2, iso3, nom_region, capital, pop, id)
FROM '/home/etudiant/Documents/Cours/R4.C.10/simplemaps_worldcities_basicv1.77/worldcities.csv'
WITH (
  FORMAT csv,
  HEADER true,
  DELIMITER ',',
  NULL "NULL"
);

CREATE VIEW ville_pays_continent AS SELECT ville, nom_region, pays_continent.pays, continent FROM ville INNER JOIN pays_continent ON ville.pays = pays_continent.pays;

SELECT pays, COUNT(ville) as nbville FROM ville_pays_continent GROUP BY pays ORDER BY pays ASC; -- Nombre de ville par pays

SELECT pays, COUNT(ville) as nbville FROM ville_pays_continent GROUP BY pays ORDER BY nbville DESC LIMIT 1; -- Pays avec le plus de villes

SELECT continent, COUNT(ville) as nbville FROM ville_pays_continent GROUP BY continent ORDER BY continent ASC; -- Nombre de ville par continent

CREATE VIEW nbville_continent AS SELECT continent, COUNT(ville) as nbville FROM ville_pays_continent GROUP BY continent ORDER BY continent ASC;

SELECT AVG(nbville) as avgville FROM nbville_continent;
