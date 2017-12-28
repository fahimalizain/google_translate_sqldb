import sys
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import pyodbc
import argparse

connection_string = 'Driver={{{driver}}}; Server={{{server}}};Port={port}; User ID={{{username}}}; Database={{{database}}}; Password={{{password}}};'

def get_translation(text, src_lang = 'en', target_lang = 'ar', **kwargs):
	data = {'sl': src_lang, 'tl' : target_lang, 'text': text}
	querystring = urllib.parse.urlencode(data)
	url = urllib.parse.urljoin('http://www.translate.google.com', querystring)	
	request = urllib.request.Request('http://translate.google.com' + '?' + querystring)
	# request = urllib.request.Request('http://translate.google.com')
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11')	
	with urllib.request.urlopen(request) as response:
		the_page = response.read()
		#print feeddata
		soup = BeautifulSoup(the_page, "html.parser")
		return str(soup.find('span', id="result_box").contents[0].contents[0])

#
def update_sql_table_translations(connection_string, tablename, pk_col, src_col, target_col, overwrite, **kwargs):
	select_string = "SELECT {pk_col}, {src_col} FROM {tablename} {overwrite}".format(tablename = tablename, pk_col = pk_col, src_col = src_col, target_col = target_col, overwrite = "" if overwrite else "WHERE " + target_col + " IS NULL")
	print(select_string)
	update_string = "UPDATE {tablename} SET {target_col} = ? WHERE {pk_col} = ?".format(tablename = tablename, target_col = target_col, pk_col = pk_col)

	cnn = pyodbc.connect(connection_string)
	cursor = cnn.cursor()
	update_cursor = cnn.cursor()	
	
	rows = cursor.execute(select_string).fetchall()
	print("Updating Translations for {} rows".format(len(rows)))
	for row in rows: # row indices according to select statement
		if row[0] and row[1]:
			try:
				print(row[0])
			except:
				pass
			
			update_cursor.execute(update_string, (get_translation(row[1], **kwargs), row[0]))
			cnn.commit()
	cnn.commit()
	cnn.close()


def process_args():
	parser = argparse.ArgumentParser()
	sub_parsers = parser.add_subparsers(title='Sub Commands', dest="type")
	sub_parsers.required = True

	parser_translate = sub_parsers.add_parser('translate', help="Translates a text")
	parser_translate.add_argument("--text", required=True, type=str)
	parser_translate.add_argument("--filename", type=str)
	parser_translate.add_argument("--print", help="Prints to stdout", default=False, action="store_true")

	# translate_db
	parser_translate_db = sub_parsers.add_parser('translate_db', help="Translates a database Table")
	#	database_details
	parser_translate_db.add_argument("--driver", type=str, help="Name of the driver as found in ODBC DataSources Administrator panel", required=True)
	parser_translate_db.add_argument("--server", type=str, help="Database server name, eg: MYPC\SQLEXPR", required=True)
	parser_translate_db.add_argument("--port", type=int, help="Database server port, eg: 1433", required=True)
	parser_translate_db.add_argument("--database", type=str, help="Database name", required=True)
	parser_translate_db.add_argument("--username", type=str, help="Login username", required=True)
	parser_translate_db.add_argument("--password", type=str, help="login password", required=True)
	
	#	table details
	parser_translate_db.add_argument("--tablename", type=str, help="Enter the table_name to UPDATE", required=True)
	parser_translate_db.add_argument("--pk_col", type=str, help="Primary key column", required=True)
	parser_translate_db.add_argument("--src_col", type=str, help="Source text column", required=True)
	parser_translate_db.add_argument("--target_col", type=str, help="Target text column", required=True)
	
	#	misc
	parser_translate_db.add_argument("--overwrite", type=bool, help="Target text column", default=False)

	parser.add_argument("--src_lang", type=str, default="en")
	parser.add_argument("--target_lang", type=str, default="ar")
	return parser.parse_args()

def main():
	args = process_args()
	if (args.type == "translate"):
		translated = get_translation(args.text, src_lang = args.src_lang, target_lang = args.target_lang)
		if args.filename:
			with open(args.filename, 'w+', encoding='utf-8') as f:
				f.write(translated)
	
		if args.print:
			sys.stdout.buffer.write(translated.encode('utf-8'))
	else:
		# we can guarantee its translate_db here
		conn_str = connection_string.format(**vars(args))
		print(vars(args))
		update_sql_table_translations(conn_str, **vars(args))

if __name__ == "__main__":
	main()