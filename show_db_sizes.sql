 -- Adapted from https://dataedo.com/kb/query/mysql/list-10-largest-tables
select
	table_schema, table_name,
	round((data_length + index_length) / 1024 / 1024, 2) total_size_mib,
	round(data_length / 1024 / 1024, 2) data_size_mib,
	round(index_length / 1024 / 1024, 2) index_size_mib

from information_schema.tables
order by total_size_mib desc
limit 10;
