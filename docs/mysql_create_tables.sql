# MySQL create table script for importing ChEBI database.
# Creation date: 01/17/2005
# Last modified: 01/10/2019
# Comment: Christian Ebeling; download [15.05.2024] from ftp://ftp.ebi.ac.uk/pub/databases/chebi/generic_dumps/mysql_create_tables.sql
# --------------------------------------------------

SET FOREIGN_KEY_CHECKS = 0;

#
# Table structure for table 'chemical_data'
#

DROP TABLE IF EXISTS `chemical_data`;
CREATE TABLE `chemical_data` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `chemical_data` TEXT NOT NULL,
  `source` TEXT NOT NULL,
  `type` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'comments'
#

DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `text` TEXT NOT NULL,
  `created_on` DATETIME NOT NULL,
  `datatype` VARCHAR(80),
  `datatype_id` INT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'compounds'
#

DROP TABLE IF EXISTS `compounds`;
CREATE TABLE `compounds` (
  `id` INT NOT NULL,
  `name` TEXT,
  `source` VARCHAR(32) NOT NULL,
  `parent_id` INT,
  `chebi_accession` VARCHAR(30) NOT NULL,
  `status` VARCHAR(1) NOT NULL,
  `definition` TEXT,
  `star` INT NOT NULL,
  `modified_on` TEXT,
  `created_by` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'database_accession'
#

DROP TABLE IF EXISTS `database_accession`;
CREATE TABLE `database_accession` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `accession_number` VARCHAR(255) NOT NULL,
  `type` TEXT NOT NULL,
  `source` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'names'
#

DROP TABLE IF EXISTS `names`;
CREATE TABLE `names` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `name` TEXT NOT NULL,
  `type` TEXT NOT NULL,
  `source` TEXT NOT NULL,
  `adapted` TEXT NOT NULL,
  `language` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'reference'
#

DROP TABLE IF EXISTS `reference`;
CREATE TABLE `reference` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `reference_id` VARCHAR(60) NOT NULL,
  `reference_db_name` VARCHAR(60) NOT NULL,
  `location_in_ref` VARCHAR(90),
  `reference_name` VARCHAR(1024),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'relation'
#

DROP TABLE IF EXISTS `relation`;
CREATE TABLE `relation` (
  `id` INT NOT NULL,
  `type` TEXT NOT NULL,
  `init_id` INT NOT NULL,
  `final_id` INT NOT NULL,
  `status` VARCHAR(1) NOT NULL, 
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'structures'
#

DROP TABLE IF EXISTS `structures`;
CREATE TABLE `structures` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `structure` TEXT NOT NULL,
  `type` TEXT NOT NULL,
  `dimension` TEXT NOT NULL,
  `default_structure` VARCHAR(1) NOT NULL,
  `autogen_structure` VARCHAR(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


#
# Table structure for table 'compound_origins'
#

DROP TABLE IF EXISTS `compound_origins`;
CREATE TABLE `compound_origins` (
  `id` INT NOT NULL,
  `compound_id` INT NOT NULL,
  `species_text` TEXT NOT NULL,
  `species_accession` TEXT,
  `component_text` TEXT,
  `component_accession` TEXT,
  `strain_text` TEXT,
  `source_type` TEXT NOT NULL,
  `source_accession` TEXT NOT NULL,
  `comments` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;


ALTER TABLE `chemical_data` ADD INDEX (`compound_id`);
ALTER TABLE `chemical_data` ADD FOREIGN KEY `FK_CHEMICAL_DATA_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `comments` ADD INDEX (`compound_id`);
ALTER TABLE `comments` ADD FOREIGN KEY `FK_COMMENTS_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `compound_origins` ADD INDEX (`compound_id`);
ALTER TABLE `compound_origins` ADD FOREIGN KEY `FK_COMPOUND_ORIGINS_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `database_accession` ADD INDEX (`compound_id`);
ALTER TABLE `database_accession` ADD FOREIGN KEY `FK_DB_ACCESSION_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `names` ADD INDEX (`compound_id`);
ALTER TABLE `names` ADD FOREIGN KEY `FK_NAMES_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `reference` ADD INDEX (`compound_id`);
ALTER TABLE `reference` ADD FOREIGN KEY `FK_REFERENCE_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `relation` ADD INDEX (`final_id`);
ALTER TABLE `relation` ADD FOREIGN KEY `FK_RELATION_TO_FINAL_COMPOUND_ID`(`final_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `relation` ADD INDEX (`init_id`);
ALTER TABLE `relation` ADD FOREIGN KEY `FK_RELATION_TO_INIT_COMPOUND_ID`(`init_id`) REFERENCES `compounds`(`id`);
ALTER TABLE `structures` ADD FOREIGN KEY `FK_STRUCTURES_TO_COMPOUND`(`compound_id`) REFERENCES `compounds`(`id`);

SET FOREIGN_KEY_CHECKS = 1;
