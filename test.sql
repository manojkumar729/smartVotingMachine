--     postgres://cwwudhhqqxpoeo:8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2@ec2-54-159-113-254.compute-1.amazonaws.com:5432/d1grhha61ks3og

-- DROP TABLE electoral_roll;

-- CREATE TABLE electoral_roll(
-- 	aadhar_uid VARCHAR PRIMARY KEY,
-- 	voter_id_num VARCHAR NOT NULL,
-- 	name VARCHAR NOT NULL,
-- 	age INTEGER NOT NULL,
-- 	gender INTEGER NOT NULL,
-- 	address VARCHAR NOT NULL,
-- 	fingerprint_index INTEGER NOT NULL,
-- 	vote INTEGER DEFAULT 0,
-- 	CHECK(
-- 		gender = 0 OR gender = 1
-- 	)
-- );

-- CREATE TABLE vote_counting(
-- 	id SERIAL PRIMARY KEY,
-- 	party_name VARCHAR NOT NULL,
-- 	candidate_name VARCHAR NOT NULL,
-- 	age INTEGER NOT NULL,
-- 	gender INTEGER NOT NULL,
-- 	vote_count INTEGER DEFAULT 0,
-- 	CHECK (
-- 		gender = 0 OR gender = 1
-- 	)
-- );

UPDATE vote_counting SET vote_count = 340 WHERE candidate_name = 'M.K.Stalin';
UPDATE vote_counting SET vote_count = 280 WHERE candidate_name = 'Edappadi K. Palaniswami';
UPDATE vote_counting SET vote_count = 30 WHERE candidate_name = 'Seeman';
UPDATE vote_counting SET vote_count = 40 WHERE candidate_name = 'Kamal Hassan';
UPDATE vote_counting SET vote_count = 940 WHERE candidate_name = 'Vijayakanth';
UPDATE vote_counting SET vote_count = 1040 WHERE candidate_name = 'ManojKumar';

