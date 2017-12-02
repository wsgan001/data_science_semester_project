# create_database.py
#
# Data Science - Final Project
# Zach Janicki and Michael McRoskey

# Imports -------------------------
import sys, sqlite3, string, re

# Global vars ---------------------
DEBUG = False

# ------------------ Papers table ---------------------
def insert_paper(db, paper_id, title, year, paper_text):
	command = 'INSERT INTO Papers VALUES (\"' + paper_id + '\",\"' + title + '\",\"' + year + '\",\"' + paper_text + '\")'
	db.execute(command)
	if DEBUG:
		print "Inserted paper \t" + paper_id

def delete_paper(db, paper_id):
	command = "DELETE FROM Papers WHERE paper_id=\'" + paper_id + "\';"
	db.execute(command)
	if DEBUG:
		print "Deleted paper \t" + paper_id
	
def update_paper(db, paper_id, field, value):
	command = "UPDATE Papers SET " + field + " = " + value + " WHERE paper_id = \"" + paper_id + "\""
	db.execute(command)
	if DEBUG:
		print "Updated paper \t" + paper_id + "\t with " + field + " = " + value
		
def extract_content(path):
	full_path = 'data/text/' + path
	with open(full_path) as f:
		return f.read().replace('\n', ' ')

def clean(string):
	string = string.lower()
	chars_to_remove = ['\"', '\'', '(', ')', '\x00']
	string = re.sub('[' + re.escape(''.join(chars_to_remove)) + ']', '', string)
    # return string.encode('ascii', errors='ignore').decode()
	return string

def populate_papers(db):
	
	# Create preliminary dictionary with paper_id, file paths, and titles
	papers = {}
	with open('data/microsoft/index.txt') as f:
		for line in f:
			line = line.strip("\n")
			content = line.split("\t")
			folder_name = content[0]
			file_name = content[1]
			paper_id = content[2]
			title = content[3]
			path = folder_name + "/" + file_name + ".txt"
			papers[paper_id] = (path, title)
	
	# Gather more information from larger papers file and compare
	with open('data/microsoft/Papers.txt') as f:
		for line in f:
			line = line.strip("\n")
			content = line.split("\t")
			paper_id = content[0]
			title_case = content[1]
			title = content[2]
			year = content[3]
			# date_of_proceeding = content[4]	# not recommended to use
			# doi = content[5]					# not recommended to use
			# conf_full_name = content[6]		# not recommended to use
			conf = content[7]
			# N/A = content[8]
			conf_id = content[9]
			# N/A = content[10]
			
			# Success
			if paper_id in papers:
				raw_text = extract_content(papers[paper_id][0])
				clean_text = clean(raw_text)
				insert_paper(db, paper_id, title, year, clean_text)
				if DEBUG:
					print "Success: " + paper_id + " inserted into db"
			# Failure
			else:
				if DEBUG:
					print "Failure: " + paper_id + " in Papers.txt does not exis in index.txt"


# ------------------ Authors table ---------------------
def insert_author(db, author_id, author_name, paper_id):
	command = 'INSERT INTO Authors VALUES (\"' + author_id + '\",\"' + author_name + '\",\"' + paper_id + '\")'
	db.execute(command)
	if DEBUG:
		print "Inserted author \t" + author_name + "\t" + author_id

def populate_authors(db):
	with open('data/microsoft/Authors.txt') as f:
		for line in f:
			content = line.split("\t")
			author_id = content[0]
			author_name = content[1]
			paper_id = "0"
			insert_author(db, author_id, author_name, paper_id)


# ------------------ Keywords table ---------------------
def insert_keyword(db, keyword, paper_id, confidence):
	command = 'INSERT INTO Keywords VALUES (\"' + keyword + '\",\"' + paper_id + '\",\"' + confidence + '\")'
	db.execute(command)
	if DEBUG:
		print "Inserted keyword \t" + keyword
		
def populate_keywords(db):
	with open('data/microsoft/PaperKeywords.txt') as f:
		for line in f:
			content = line.split("\t")
			paper_id = content[0]
			keyword = content[1]
			# keyword_id = content[2] 	# not recommended to use
			confidence = "0" 			# not sure what confidence refers to
			insert_keyword(db, keyword, paper_id, confidence)
	
def display_table(db, table):
	print "\n================== " + table + " =================="
	command = 'SELECT * FROM ' + table
	for row in db.execute(command):
		string = ""
		for item in row:
			string += item + "\t"
		print string


# ------------------ Main Execution ---------------------
if __name__ == "__main__":
	
	# Create the database
	conn = sqlite3.connect('data/database.db')
	c = conn.cursor()
	
	# Try to create blank Papers, Authors, Keywords tables (if first run)
	try:
		c.execute('''CREATE TABLE Papers(paper_id TEXT, title TEXT, year TEXT, paper_text TEXT)''')
		c.execute('''CREATE TABLE Authors(author_id TEXT, author_name TEXT, paper_id TEXT)''')
		c.execute('''CREATE TABLE Keywords(keyword TEXT, paper_id TEXT, confidence TEXT)''')
	except:
		print "Already created SQL tables\n"
	
	# Populate Papers table
	populate_papers(c)
	
	# Populate Authors table
	populate_authors(c)
	
	# Populate Keywords table
	populate_keywords(c)
		
	conn.commit()
	conn.close()