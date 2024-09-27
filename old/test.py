"""-- Check the data type and length of the ident column in the airport table
SHOW COLUMNS FROM airport LIKE 'ident';

-- Check the data type and length of the airport_ident column in the game_airports table
SHOW COLUMNS FROM game_airports LIKE 'airport_ident';

-- If they do not match, you can modify the airport_ident column to match the ident column
ALTER TABLE game_airports MODIFY airport_ident VARCHAR(40); -- Adjust the data type and length as needed


"""