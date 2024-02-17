/*
 Navicat Premium Data Transfer

 Source Server         : rsinfo
 Source Server Type    : SQLite
 Source Server Version : 3036000 (3.36.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3036000 (3.36.0)
 File Encoding         : 65001

 Date: 14/01/2024 16:44:01
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for rsinfo
-- ----------------------------
DROP TABLE IF EXISTS "rsinfo";
CREATE TABLE rsinfo
(id TEXT PRIMARY KEY, url TEXT,  name TEXT,  city TEXT,  address TEXT,  guide TEXT,  scale TEXT,  update_date TEXT,  salary TEXT,  experience TEXT,  degree TEXT,  company TEXT,  industry TEXT,  fund TEXT,  res TEXT,  boss TEXT,  boss_title TEXT,  active TEXT,  description TEXT,  communicate TEXT,  datetime TEXT);

PRAGMA foreign_keys = true;


CREATE TABLE JD (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    url VARCHAR(255),
    name VARCHAR(255),
    city VARCHAR(100),
    address VARCHAR(255),
    guide VARCHAR(255),
    scale VARCHAR(50),
    update_date DATE,
    salary VARCHAR(100),
    experience VARCHAR(100),
    degree VARCHAR(50),
    company VARCHAR(255),
    industry VARCHAR(255),
    fund VARCHAR(255),
    res DATE,
    boss VARCHAR(100),
    boss_title VARCHAR(100),
    active VARCHAR(50),
    description TEXT,
    communicated TINYINT(1),
    checked_date DATETIME
);