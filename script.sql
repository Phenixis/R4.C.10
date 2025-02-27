COPY gamenn
FROM '/home/etudiant/Documents/design_tp_games.csv'
WITH (
  FORMAT csv,
  HEADER true,
  DELIMITER ';'
);
