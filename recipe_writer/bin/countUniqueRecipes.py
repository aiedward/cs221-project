import os, json

def main():
	pathToRoot = os.path.dirname(os.path.dirname(__file__))
	pathToRecipes = os.path.join(pathToRoot, "res", "jsonrecipes")
	allFiles = sorted(os.listdir(pathToRecipes))
	allRecipes = []
	for filename in allFiles:
		if filename[0] == ".":
			continue
		jsonFileName = os.path.join(pathToRecipes, filename)
		fullJsonString = None 
		with open(jsonFileName, 'r') as f: 
			fullJsonString = f.read()
		d = json.JSONDecoder()
		
		myDict = d.decode(fullJsonString)
		for _, val in myDict.items():
			allRecipes.append(val["recipeName"])
	
	print "path: " + pathToRecipes
	print "total num recipes: ", len(allRecipes)
	print "total num UNIQUE recipes: ", len(set(allRecipes))

if __name__ == "__main__":
	main()