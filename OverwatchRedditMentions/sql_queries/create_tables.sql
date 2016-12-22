-- Drop hero, post, and comment tables.
-- DROP TABLE RedditComment;
-- DROP TABLE RedditPost;
-- DROP TABLE Hero;

-- Create hero table
-- CREATE TABLE Hero(
--  id INT NOT NULL AUTO_INCREMENT,
--  name VARCHAR(150) NOT NULL,
--  role VARCHAR(20) NOT NULL,
--   PRIMARY KEY (id)
-- );

-- Create Reddit Post Table
-- CREATE TABLE RedditPost(
--   id INT NOT NULL AUTO_INCREMENT,
--   hero_ref_id INT,
--   post VARCHAR(500),
--   author VARCHAR(150),
--   enddate DATETIME,
--   upvotes INT,
--  FOREIGN KEY (hero_ref_id) REFERENCES Hero(id),
--  PRIMARY KEY (id)
-- );

-- Create Reddit Comment Table
-- CREATE TABLE RedditComment(
--  id INT NOT NULL AUTO_INCREMENT,
--  comment VARCHAR(500),
--  author VARCHAR(150),
--  enddate DATETIME,
--  upvotes INT,
--  post_id INT,
--  hero_ref_id INT,
--  FOREIGN KEY (post_id) REFERENCES RedditPost(id),
--  FOREIGN KEY (hero_ref_id) REFERENCES Hero(id),
--  PRIMARY KEY (id));


-- CREATE TABLE SentimentWord (
--   id INT NOT NULL AUTO_INCREMENT
-- word VARCHAR(100),
-- sentiment VARCHAR(15),
-- PRIMARY KEY (id));
