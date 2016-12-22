import pymongo

f = open("raw_data.txt","r")
contents = f.readlines()
translation = {
	"captain":"captain falcon",
	"ganon":"ganondorf",
	"gekkouga":"greninja",		
	"koopa":"bowser",
	"koopajr":"bowser jr",
	"lizardon":"charizard",
	"murabito":"villager",
	"purin":"jigglypuff",
	"reflet":"robin",
	"robot":"rob",
	"rockman":"megaman",
	"rosetta":"rosalina",
	"szerosuit":"zerosuit",
	"pitb":"dark pit",
	"mariod":"dr mario"
}

dont_include = ["miienemyf","miienemys","miienemyg","koopag","lucariom","littlemacg","ironball","wiifit+","warioman"]

damage_data = {}

name = ""
move = ""
for line in contents:
	line = line.strip()
	if "BEGIN" in line and "_" not in line:
		name = line
		name = name.replace("BEGIN ","")
		name = name.replace("\n","")
		if name in translation:
			name = translation[name]
		damage_data[name] = {}
		continue
	elif name in dont_include:
		continue
	elif name is "" or line is "" or line is "\n" or "frame" in line:
		continue
	elif "%" not in line:
		move = line
	elif "Max" in line:
		dmg = line.split("Max Damage:")[1].strip(" ")
		dmg = float(dmg.strip("%"))
		damage_data[name][move] = dmg

def importIntoDB():
	from pymongo import MongoClient
	client = MongoClient('localhost', 27017)
	db = client["SmashPriority"]
	col  = db["damage_data"]
	for key in damage_data:
		doc = {
			"character": key 
		}
		for move in damage_data[key]:
			_move = "".join(c for c in move if c not in ('!','.',':'))
			doc[_move] = damage_data[key][move]
		col.insert(doc)

def getDamageDataFromDB():
	from pymongo import MongoClient
	client = MongoClient('localhost', 27017)
	db = client["SmashPriority"]
	col  = db["damage_data"]
	cursor = col.find()
	dmgData = {}
	charIndex = 0
	for document in cursor:
		name = document["character"]
		if name in dont_include:
			continue
		if name in translation:
			name = translation[name]
		total_dmg = []
		for damage in document:
			if str(type(document[damage])) == "<type 'float'>":
				total_dmg.append(tuple((damage, document[damage]))) 
		dmgData[name] = (total_dmg,charIndex)
		charIndex += 1
		print(name,charIndex)
	return dmgData
def printKeys():
	print(damage_data.keys())
def getData():
	return damage_data

def getDamageComparisons():
	d = getDamageDataFromDB()
	dmg_comparisons = {}
	for char1 in d:
		for char2 in d:
			priority_count = 0
			for move1 in d[char1][0]:
				move1_dmg = move1[1]
				for move2 in d[char2][0]:
					move2_dmg = move2[1]
					if ("Uair" in move1[0] and "Uair" in move2[0]) or ("U-" in move1[0] and "U-" in move2[0]) or ("Uair" in move1[0] and "U-" in move2[0]) or ("U-" in move1[0] and "Uair" in move2[0]):
						continue
					if move1_dmg - 8.0 > move2_dmg:
						priority_count += 1
			dmg_comparisons[tuple((char1,char2,d[char1][1],d[char2][1]))] = priority_count
	'''
	for pair in dmg_comparisons:
		if pair[0] !=  "jigglypuff":
			continue
		print(pair, dmg_comparisons[pair])
		raw_input()
	'''
	return dmg_comparisons


import operator
def getPriorityCountsPerCharacter():
	priorityCounts = {}
	comp = getDamageComparisons()
	for pair in comp:
		firstChar = pair[0]
		if firstChar not in priorityCounts:
			priorityCounts[firstChar] = comp[pair]
		else:
			priorityCounts[firstChar] += comp[pair]	
	priorityCounts = sorted(priorityCounts.items(), key=operator.itemgetter(1))	
	return priorityCounts

def getHighChartsDataFormat():
	hcData = []
	comps = getDamageComparisons()
	for comp in comps:
		currData = [comp[2],comp[3],comps[comp]]
		hcData.append(currData)
	return hcData

def writeHighChartsDataFormatToFile(fileName = "ssb_hc_data.txt"):
	f = open(fileName,"w+")
	d = getHighChartsDataFormat()
	f.write("[")
	for i in d:
		f.write(str(i) + ",")
	f.write("]")
	f.close()	

def getAllCharactersFromDB():
	ssb_chars = []
	from pymongo import MongoClient
	client = MongoClient('localhost', 27017)
	db = client["SmashPriority"]
	col  = db["damage_data"]
	cursor = col.find()
	dmgData = {}
	charIndex = 0
	for document in cursor:
		name = document["character"]
		if name not in dont_include:
			if name in translation:
				name = translation[name]	
			ssb_chars.append(str(name))
	return ssb_chars

writeHighChartsDataFormatToFile()
print(getAllCharactersFromDB())
#print(getDamageComparisons())
#print(getPriorityCountsPerCharacter())
