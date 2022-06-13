CREATE TABLE `backup_jobs` (
  `timestamp` datetime NOT NULL,
  `host` varchar(32) NOT NULL,
  `subclient` varchar(255) NOT NULL,
  `sizeOfMediaOnDisk` bigint(20) NOT NULL,
  `appTypeName` varchar(64) NOT NULL,
  `sizeOfApplication` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE `backup_jobs`
  ADD PRIMARY KEY (`timestamp`,`host`,`subclient`);
COMMIT;


