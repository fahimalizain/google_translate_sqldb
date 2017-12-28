# Google Translates a SQL DB

## In development

## Supported Commands

```
	translate
		--text
		--print
		--filename
		
	translate_db
		--driver
		--server
		--port
		--database
		--username
		--password
		
		--tablename
		--pk_col
		--src_col
		--target_col
		--overwrite
		
		eg:
			python google-translate-sqldb.py --target_lang=es translate_db --driver="SQL Server" --server="FAZTP-DELL" --port=1433 --database="Finance" --username="sa" --password="123123" --tablename="TRANSLATIONS" --pk_col="text" --src_col="english" --target_col="arabic" --overwrite=True
	--src_lang		(default=en)
	--target_lang	(default=ar)
```