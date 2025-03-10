DROP DATABASE IF EXISTS projet;
CREATE DATABASE projet;
USE projet;

CREATE TABLE `recette` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `note` DECIMAL NOT NULL,
    `temps_preparation` VARCHAR(255) NOT NULL,
    `difficulte` VARCHAR(255) NOT NULL,
    `prix` VARCHAR(255) NOT NULL,
    `titre` VARCHAR(255) DEFAULT 'inconnu',
    PRIMARY KEY(`id`)
);

CREATE TABLE `ingredient` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nom` VARCHAR(255) DEFAULT 'inconnu' NULL,
    `quantite` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`)
);

CREATE TABLE `etape` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `numero` INTEGER NOT NULL,
    `etape` TEXT NOT NULL,
    `recette_id` INTEGER NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY (`recette_id`) REFERENCES `recette`(`id`) 
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE `materiel` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `equipement` VARCHAR(255) DEFAULT 'inconnu',
    PRIMARY KEY(`id`)
);

CREATE TABLE `recette_ingredient` (
    `recette_id` INTEGER NOT NULL,
    `ingredient_id` INTEGER NOT NULL,
    PRIMARY KEY(`recette_id`, `ingredient_id`),
    FOREIGN KEY(`recette_id`) REFERENCES `recette`(`id`) 
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(`ingredient_id`) REFERENCES `ingredient`(`id`) 
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE `recette_materiel` (
    `recette_id` INTEGER NOT NULL,
    `materiel_id` INTEGER NOT NULL,
    PRIMARY KEY(`recette_id`, `materiel_id`),
    FOREIGN KEY(`recette_id`) REFERENCES `recette`(`id`) 
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(`materiel_id`) REFERENCES `materiel`(`id`) 
    ON UPDATE CASCADE ON DELETE CASCADE
);
