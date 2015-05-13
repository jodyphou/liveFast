'''

'''
import sqlite3
import sys
import os


THE_PATH = "PARTS.com.swag"
ROOT_SUBSTRING = 'xxxxx'
CHILD_REV_SUBSTRING = 'xx'
ARCHIVE_SUBSTRING = 'archive'
PDF_SUBSTRING = 'pdf'
DB_FILE = 'vault.db'
PART_NUBMER_SKIP = ['240','540']
DIRECTORY_LIST =[]

def traverse():

	cParentFolder = ''
	parentFolder = 'Test'
	tableName = 'Bob'

	for dirItems in DIRECTORY_LIST:

		currentPath = THE_PATH + '\\' + dirItems
		print currentPath

		for subdir, dirs, files in os.walk(currentPath):

			noVaultPath = subdir[len(THE_PATH) + 1: ]
			firstSlashIndex = noVaultPath.find('\\')

			if firstSlashIndex != -1:
				parentFolder = noVaultPath[:firstSlashIndex]
				if cParentFolder.find(parentFolder) == -1:
					cParentFolder = parentFolder
					folderSplit = cParentFolder.replace('_','-').replace(' ','').replace('&','').split('-')
					try:
						folderSplit.remove('xxxxx')
					except ValueError:
						print 'Opps'
					folderSplit.append(folderSplit[0])
					folderSplit.pop(0)
					tableName = ''.join(folderSplit)
					print tableName	
				else:
					pass
			else:
				pass

			subdirNoArch = subdir.lower()
			if subdirNoArch.find(ARCHIVE_SUBSTRING) == -1:

				if len(files) > 0:
					partNumberIndex = subdir.rfind('\\')
					partNumber = subdir[partNumberIndex + 1:]

					if len(partNumber) == 9:
						foundRev = revMatch( partNumber, files )
						insertIntoDB(tableName, partNumber, files, foundRev )
					else:
						#underscore
						underScoreIndex = partNumber.find('_')
						spaceIndex = partNumber.find(' ')

						if underScoreIndex > 0:
							foundRev = revMatch( partNumber[:underScoreIndex], files)
							insertIntoDB(tableName, partNumber[:underScoreIndex], files, foundRev )
						elif spaceIndex > 0:
							foundRev = revMatch( partNumber[:9], files )
							insertIntoDB(tableName, partNumber[:9], files, foundRev )
						else:
							foundRev = revMatch( partNumber[:12], files )
							insertIntoDB(tableName, partNumber[:12], files, foundRev )
				else:
					pass
			else:
				pass

def insertIntoDB(parentPart, partNumber, fileName, rev):

	conn = sqlite3.connect(DB_FILE)
	c = conn.cursor()

	fileNameStr = ','.join(fileName)

	#print parentPart + "," + partNumber + "," + fileNameStr + "," + rev
	try:
		c.execute ( "INSERT into %s VALUES(NULL, \'%s\', \'%s\', \'%s\')" % (parentPart, partNumber, fileNameStr , rev ) )
	except sqlite3.OperationalError:
		print 'Failed! ' + ( "INSERT into %s VALUES(NULL, \'%s\', \'%s\', \'%s\')" % (parentPart, partNumber, fileNameStr , rev ) )

	conn.commit()
	conn.close()

	pass


def revMatch(partNumber, fileName):

	lHyphenIndex = partNumber.find('-')

	childPN = partNumber[lHyphenIndex + 1:lHyphenIndex + 6]
	
	for items in fileName:
		# the file name at least contains the child partnumber
		if items.find(childPN) > 0:
			#pdf...
			if items.find(PDF_SUBSTRING) > 0:
				childPNIndex = items.find(childPN)

				if len(partNumber) == 9:
					#XYZ-XXXXX
					if len(items[childPNIndex + 5:-4]) > 0:
						parsePNSub = items[childPNIndex + 5:-4]
						################################################################
						#first use case the word rev...
						parsePNlower =  parsePNSub.lower()
						parsePNRevIndex = parsePNlower.find('rev')

						if parsePNRevIndex > 0:

							parsePNSplitSpace = parsePNSub[parsePNRevIndex:].split(' ')

							if len(parsePNSplitSpace) > 1:
								# Rev X
								if len(parsePNSplitSpace[0]) == 3:
									#print partNumber + " " + parsePNSplitSpace[1] + " " + items
									return parsePNSplitSpace[1]
								else:
									#print partNumber + " " + parsePNSplitSpace[0][3:] + " " + items
									return parsePNSplitSpace[0][3:]
							else:
								#print partNumber + " " + parsePNSub[parsePNRevIndex:][3] + " " + items
								return parsePNSub[parsePNRevIndex:][3]
						else:
							#print partNumber + " " + items[childPNIndex + 5:-4] + " " + items 
							return items[childPNIndex + 5:-4]
					else:
						#print partNumber + " None " + items
						return "None"
				else:
					#XYZ-XXXXX-XX
					parsePNSub = items[childPNIndex + 5:-4]
					################################################################
					#first use case the word rev...
					parsePNlower =  parsePNSub.lower()
					parsePNRevIndex = parsePNlower.find('rev')

					if parsePNRevIndex > 0:

						parsePNSplitSpace = parsePNSub[parsePNRevIndex:].split(' ')

						if len(parsePNSplitSpace) > 1:
							# Rev X
							if len(parsePNSplitSpace[0]) == 3:
								#print partNumber + " " + parsePNSplitSpace[1] + " " + items
								return parsePNSplitSpace[1]
							else:
								#print partNumber + " " + parsePNSplitSpace[0][3:] + " " + items
								return parsePNSplitSpace[0][3:]
						else:
							#print partNumber + " " + parsePNSub[parsePNRevIndex:][3] + " " + items
							return parsePNSub[parsePNRevIndex:][3]
					else:
						################################################################
						#dash number 
						#-XX
						dashString = items[childPNIndex + 5:-4]
						dashIndex = dashString.find(partNumber[-2:])
						underscoreIndex = dashString.find('_')

						if dashIndex > 0 and underscoreIndex == -1:
							#print partNumber + " " +  dashString[dashIndex + 2:] + " " + items
							return dashString[dashIndex + 2:]
						elif dashIndex == 0 and underscoreIndex == -1:
							#print partNumber + " " +  dashString[dashIndex + 2:] + " " + items
							return dashString[dashIndex + 2:]
						elif underscoreIndex > 0:
							#print partNumber + " " +  dashString[underscoreIndex + 1:] + " " + items
							return dashString[underscoreIndex + 1:]
						else:
							if len(items[childPNIndex + 5:-4]) == 1:
								#print partNumber + items[childPNIndex + 5:-4] + " " + items
								return items[childPNIndex + 5:-4]
							else:
								#print partNumber + " None " + items
								return "None"
			else:
				pass
				#print "skip! " +  items




	return 'None'


def initDB():

	cParentFolder = ''
	parentFolder = 'Test'

	if( os.path.isfile(DB_FILE)):
		os.remove(DB_FILE)

	#create table
	conn = sqlite3.connect(DB_FILE)
	c = conn.cursor()
	skipFlag = 0


	for subdir, dirs, files in os.walk(THE_PATH):
		
		noVaultPath = subdir[len(THE_PATH) + 1: ]
		firstSlashIndex = noVaultPath.find('\\')

		for pnSkip in PART_NUBMER_SKIP:
			if subdir.find(pnSkip) >= 0:
				skipFlag = 1
				#print 'Skip! ' + tableName
				break

		if firstSlashIndex != -1 and skipFlag == 0:
			parentFolder = noVaultPath[:firstSlashIndex]
			if cParentFolder.find(parentFolder) == -1:
				cParentFolder = parentFolder
				folderSplit = cParentFolder.replace('_','-').replace(' ','').replace('&','').split('-')
				try:
					folderSplit.remove('xxxxx')
				except ValueError:
					print 'Opps'
				folderSplit.reverse()
				tableName = ''.join(folderSplit)
				sqlStatement = "CREATE TABLE %s (id integer primary key autoincrement, partNumber varchar, files varchar, revision varchar)" % tableName
				print tableName
				#print sqlStatement
				c.execute(sqlStatement)
			else:
				
				pass
		else:
			print subdir
			pass

	conn.commit()
	conn.close()

def initDirectoryFile():
	cParentFolder = ''
	parentFolder = 'Test'

	if( os.path.isfile(DB_FILE)):
		os.remove(DB_FILE)

	#create table
	conn = sqlite3.connect(DB_FILE)
	c = conn.cursor()
	skipFlag = 0


	fileDir = open('dir.txt', 'r')


	for dir in fileDir:
		#print dir
		cParentFolder = dir[:-1]
		DIRECTORY_LIST.append(cParentFolder	)
		folderSplit = cParentFolder.replace('_','-').replace(' ','').replace('&','').split('-')
		try:
			folderSplit.remove('xxxxx')
		except ValueError:
			print 'Opps'
		#folderSplit.reverse()



		folderSplit.append(folderSplit[0])
		folderSplit.pop(0)
		tableName = ''.join(folderSplit)
		
		sqlStatement = "CREATE TABLE %s (id integer primary key autoincrement, partNumber varchar, files varchar, revision varchar)" % tableName
		#print "CREATE TABLE %s (id integer primary key autoincrement, partNumber varchar, files varchar, revision varchar)" % tableName
		#print tableName
		c.execute(sqlStatement)

	conn.commit()
	conn.close()
	fileDir.close()

	#print DIRECTORY_LIST	


def createDirectoryFile():
	
	fileDir = open('dir.txt', 'w+')

	os.chdir(THE_PATH)

	for name in os.listdir("."): 
		if os.path.isdir(name): 
			DIRECTORY_LIST.append(name)
			fileDir.write(name + '\n')

	os.chdir(os.getcwd())

	fileDir.close()

	print DIRECTORY_LIST	

#createDirectoryFile()
initDirectoryFile()
print "DB Table Init!"
#initDB()
print "Traverse!"
traverse()