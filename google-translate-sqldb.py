import sys
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import pyodbc
import argparse

connection_string = 'Driver={SQL Server}; Server=FAZTP-DELL;MARS_Connection=True;Port=1433; User ID=sa; Database=Finance; Password=123123;'

def get_translation(text, src_lang = 'en', target_lang = 'ar'):
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
def update_sql_table_translations(table_name = "TRANSLATIONS", pk_col = "text", src_col = "english", target_col = "arabic", overwrite = True):
	select_string = "SELECT {pk_col}, {src_col} FROM {table_name} {overwrite}".format(table_name = table_name, pk_col = pk_col, src_col = src_col, target_col = target_col, overwrite = "" if overwrite else "WHERE " + target_col + " IS NULL")
	print(select_string)
	update_string = "UPDATE {table_name} SET {target_col} = ? WHERE {pk_col} = ?".format(table_name = table_name, target_col = target_col, pk_col = pk_col)	

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
			
			update_cursor.execute(update_string, (get_translation(row[1]), row[0]))
			cnn.commit()
	cnn.commit()
	cnn.close()

def print_help():
	print("""
	Help:
	- 1st argument can be : 'translate'
		""")
	
parser = argparse.ArgumentParser()
parser.add_argument("fn", help="translate -is the only option now")
parser.add_argument("--text", help="Text to Translate")
parser.add_argument("--src_lang", type=str, default="en")
parser.add_argument("--target_lang", type=str, default="ar")
args = parser.parse_args()

if args.fn == "translate":
	translated = get_translation(args.text, src_lang = args.src_lang, target_lang = args.target_lang)
	with open('translation.txt', 'w+', encoding='utf-8') as f:
		f.write(translated)
else:
	print("Invalid Argument")
# update_sql_table_translations()