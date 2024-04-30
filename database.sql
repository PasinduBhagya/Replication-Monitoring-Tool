CREATE TABLE `statusProgress` (
  `statusID` int NOT NULL AUTO_INCREMENT,
  `dateTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `itemName` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `itemType` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `bcpServerDetails` (
  `serversID` int NOT NULL AUTO_INCREMENT,
  `projectName` varchar(50) DEFAULT NULL,
  `localServerIP` varchar(50) DEFAULT NULL,
  `localUsername` varchar(50) DEFAULT NULL,
  `BCPServerIP` varchar(50) DEFAULT NULL,
  `BCPUsername` varchar(50) DEFAULT NULL,
  `alias` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`serversID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `bcpSyncRules` (
  `ruleID` int NOT NULL AUTO_INCREMENT,
  `projectName` varchar(255) DEFAULT NULL,
  `localServerPath` varchar(255) DEFAULT NULL,
  `bcpServerPath` varchar(255) DEFAULT NULL,
  `serversID` int DEFAULT NULL,
  `extensions` varchar(255) DEFAULT NULL,
  `alias` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ruleID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
