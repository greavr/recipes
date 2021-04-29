from flask import Flask, render_template, flash, request, redirect, jsonify, Response
from collections import Counter
import json
from sortedcontainers import SortedDict
from operator import itemgetter
import operator
import os
from google.cloud import storage
from urllib.parse import urlparse

## Config App
app = Flask(__name__)
JSON_Loc = "./new_recipes.json"
allRecipes = None

# Load All JSON
def LoadJson():
    global JSON_Loc
    with open(JSON_Loc, encoding="utf8") as f:
        data = json.load(f)
    return sorted(data, key = lambda i: i['Title'])


# Load from Bucket
def LoadGSC(PathToLoad):
    o = urlparse(PathToLoad, allow_fragments=False)
    gcs_bucket = o.netloc
    gcs_file = o.path[1:]
    print ("Load: " + gcs_bucket + ", " + gcs_file)
    # Load File from GCS
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(gcs_bucket)
    blob = bucket.get_blob(gcs_file)
    data_to_process = blob.download_as_string()
    data = json.loads(data_to_process)
    return sorted(data, key = lambda i: i['Title'])

def SaveGSC(PathToSave,sortedRecipes):
    o = urlparse(PathToSave, allow_fragments=False)
    gcs_bucket = o.netloc
    gcs_file = o.path[1:]
    print ("Save: " + gcs_bucket + ", " + gcs_file)
    # Load File from GCS
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(gcs_bucket)
    blob = bucket.blob(gcs_file)
    blob.upload_from_string(json.dumps(sortedRecipes, indent=4))

# Append New Recipe
def AddRecipe(NewRecipe):
    global allRecipes
    allRecipes.append(NewRecipe)
    SaveJson(allRecipes)

# Remove Recipe
def RemoveRecipe(RecipeTitle):
    global allRecipes
    for aRecipe in allRecipes:
        if aRecipe["Title"] == RecipeTitle:
            allRecipes.remove(aRecipe)
    SaveJson(allRecipes)

#Update Recipe
def UpdateRecipe(UpdatedRecipe, OldTitle):
    global allRecipes
    # Remove Old One
    for aRecipe in allRecipes:
        if aRecipe["Title"] == OldTitle:
            allRecipes.remove(aRecipe)

    # Add New One
    allRecipes.append(UpdatedRecipe)
    SaveJson(allRecipes)

def SaveJson(RecipeList):
    sortedRecipes = sorted(RecipeList, key = itemgetter('Title'))
    #Save File
    if os.getenv("GCS_LOC") != None:
        SaveGSC(os.getenv("GCS_LOC"),RecipeList)
    else:
        with open(JSON_Loc, 'w') as outfile:
            json.dump(sortedRecipes, outfile, indent=4)
    
    global allRecipes 
    GetJSON()

# Get Most Popular Recipes
def GetPopular(MaxReturn):
    # Return MaxReturn number of top results
    # Need to validate that source JSON has likes field, else defaults to 1

    global allRecipes

    # Hold variable for results
    addResult = {}
    for aResult in allRecipes:
        if "Likes" in aResult.keys():
            addResult[aResult["Title"]] = int(aResult["Likes"])
        else:
            addResult[aResult["Title"]] = 1

    # Add to return result set
    returnResult =  dict(sorted(addResult.items(), key=operator.itemgetter(1),reverse=True)[:MaxReturn])
    return returnResult

# Get Unique Values Based On Parameter
def GetUnique(SearchValue):
    # Function to get unique values (and Count) from list
    raw_count = {}
    global allRecipes
    for aRecipes in allRecipes:
        thisCategory = aRecipes[SearchValue]
        if len(thisCategory) > 0:
            if thisCategory in raw_count:
                raw_count[thisCategory] += 1
            else:
                raw_count[thisCategory] = 1
    result = SortedDict(raw_count)
    return result

def GetJSON():
    global allRecipes
    # Load All Recipes (if GSC Set use that)
    if os.getenv("GCS_LOC") != None:
        print ("GCS")
        allRecipes = LoadGSC(os.getenv("GCS_LOC"))
    else:
        print ("Local")
        allRecipes = LoadJson()

GetJSON()
PopularResults = GetPopular(5)
allCategories = GetUnique("Category")
allTimes =  GetUnique("Time")
allYields =  GetUnique("Yield")

def FindRecipesBy(Field,SearchValue):
    global allRecipes
    RecipesFound = []
    for aRecipe in allRecipes:
        if aRecipe[Field] == SearchValue:
            RecipesFound.append(aRecipe)
    return RecipesFound

# Default, display listpage page
@app.route("/recipe", methods=['GET'])
@app.route("/recipe/", methods=['GET'])
@app.route("/delete/", methods=['GET'])
@app.route("/delete", methods=['GET'])
@app.route("/save", methods=['GET'])
@app.route("/save/", methods=['GET'])
@app.route("/lookup/", methods=['GET'])
@app.route("/lookup", methods=['GET'])
@app.route("/like/", methods=['GET'])
@app.route("/like", methods=['GET'])
def LostPages():
    return redirect("/")

@app.route("/", methods=['GET'])
def default():
    #Display options
    GetJSON()
    print(allCategories)
    return render_template('index.html', Categories=allCategories, Times=allTimes, Yields=allYields, RecipeList=allRecipes, Popular=PopularResults)

# Search for results
@app.route("/lookup/", methods=['POST'])
def LookupRedirect():
    if "KeyWord" in request.form:
        KeyWord = request.form['KeyWord']
        return redirect("/lookup/"+KeyWord)
    else:
        return redirect("/")

# Function to Upvote
@app.route("/like/<string:RecipeName>", methods=['GET'])
def Like(RecipeName):
    # Increase Like count in recipe and save
    global allRecipes
    for aRecipe in allRecipes:
        if RecipeName == aRecipe["Title"]:
            # Check if key exists
            if "Likes" in aRecipe.keys():
                aRecipe["Likes"] += 1
            else:
                 aRecipe["Likes"] = 2
            UpdateRecipe(aRecipe, RecipeName)
            return redirect("/recipe/"+RecipeName)

@app.route("/lookup/<string:KeyWord>", methods=['GET'])
def lookup(KeyWord):
    #Return Values:
    KeyWord = KeyWord.lower()
    RecipeName = []
    IngredientsFilteredRecipes = []
    DirectionsFilteredRecipes = []

    # Search For keyword in Recipe name
    for aRecipe in allRecipes:
        if KeyWord in aRecipe["Title"].lower():
            RecipeName.append(aRecipe)


    # Search for keyword in Ingredients
    for aRecipe in allRecipes:
        # Itterate over Ingredients step
        found = False
        for aIngredients in aRecipe["Ingredients"]:
            if not found:
                if KeyWord in aIngredients.lower():
                    IngredientsFilteredRecipes.append(aRecipe)
                    found = True

    # Search for keyword in Directions
    for aRecipe in allRecipes:
        # Itterate over Ingredients step
        found = False
        for aDirections in aRecipe["Directions"].values():
            if not found:
                if KeyWord in aDirections.lower():
                    DirectionsFilteredRecipes.append(aRecipe)
                    found = True



    return render_template('search.html', Categories=allCategories, Popular=PopularResults,Times=allTimes, Yields=allYields,RecipeName=RecipeName, SearchWord=KeyWord, IngredientsFilteredRecipes=IngredientsFilteredRecipes, DirectionsFilteredRecipes=DirectionsFilteredRecipes)

# Load recipes with same time
@app.route("/time/<string:TimeFrame>", methods=['GET'])
def GetTimeFrame(TimeFrame):
    #Return Recipes with Same Time Frame
    RecipesToShow = FindRecipesBy("Time", TimeFrame)
    return render_template('time.html', Popular=PopularResults, Categories=allCategories , Times=allTimes, Yields=allYields,TimeFrame=TimeFrame, FilteredRecipes=RecipesToShow)


# Load recipes with same Yield
@app.route("/yield/<string:size>", methods=['GET'])
def GetYield(size):
    RecipesToShow = FindRecipesBy("Yield", size)
    return render_template('yield.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields,Yield=size, FilteredRecipes=RecipesToShow)

# Load recipes with same Category
@app.route("/category/<string:cat>", methods=['GET'])
def GetCategory(cat):
    RecipesToShow = FindRecipesBy("Category", cat)
    return render_template('categories.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields,Category=cat, FilteredRecipes=RecipesToShow)

# Load Recipe Details
@app.route("/recipe/<string:RecipeToOpen>", methods=['GET'])
def ShowRecipe(RecipeToOpen):
    global allRecipes
    for aRecipe in allRecipes:
        if aRecipe["Title"] == RecipeToOpen:
            recipeToDisplay = aRecipe

    return render_template('recipe.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields,thisRecipe=recipeToDisplay)

# Admin Page
@app.route("/admin/", methods=['GET'])
@app.route("/admin", methods=['GET'])
def Admin_home():
    #Display options
    print ("Loading admin")
    GetJSON()
    return render_template('admin.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields, RecipeList=allRecipes)

# Edit Recipe Details
@app.route("/edit/<string:RecipeToOpen>", methods=['GET'])
def Edit(RecipeToOpen):
    global allRecipes
    for aRecipe in allRecipes:
        if aRecipe["Title"] == RecipeToOpen:
            recipeToDisplay = aRecipe

    return render_template('edit.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields,thisRecipe=recipeToDisplay,Message="")

# Route for new
@app.route("/edit", methods=['GET'])
@app.route("/edit/", methods=['GET'])
def NewRecipe():
    return render_template('edit.html', Popular=PopularResults, Categories=allCategories, Times=allTimes, Yields=allYields,thisRecipe=[],Message="")

# Route for toggle status
@app.route("/toggle-status/<string:RecipeToToggle>", methods=['GET'])
def ToggleStatus(RecipeToToggle):
    # Set Active / In Active
    for aRecipe in allRecipes:
        if aRecipe["Title"] == RecipeToToggle:
            print("Status: Found Recipe")
            if "Active" in aRecipe.keys():
                print(aRecipe["Active"])
                if aRecipe["Active"]:
                    print("Status: Deactivating Recipe")
                    aRecipe["Active"] = False
                    UpdateRecipe(aRecipe,aRecipe["Title"])
                    return redirect("/admin")
                else:
                    print("Status: Activating Recipe")
                    aRecipe["Active"] = True
                    UpdateRecipe(aRecipe,aRecipe["Title"])
                    return redirect("/admin")
            else:
                print("Status: Deactivating Recipe")
                aRecipe["Active"] = False
                UpdateRecipe(aRecipe,aRecipe["Title"])
                return redirect("/admin")

# Route for Delete
@app.route("/delete/<string:RecipeToDelete>", methods=['GET', 'POST'])
def DeleteRecipe(RecipeToDelete):
    RemoveRecipe(RecipeToDelete)
    return redirect("/admin")

# Save Values
@app.route("/save", methods=['POST'])
def SaveValues():
    #Either Save or Update the values based upon use
    newRecipe = {}
    newRecipe["Title"] = request.form['Title']
    newRecipe["Time"] = request.form['Time']
    newRecipe["Category"] = request.form['Category']
    newRecipe["Yield"] = request.form['Yield']
    newRecipe["Likes"] = request.form['Likes']
    # Create Source Array
    source = {}
    source["Text"] = request.form['source_title']
    source["URL"] = request.form['source_url']
    newRecipe["Source"] = source

    if 'Active' in request.form:
        newRecipe["Active"] = True
    else:
        newRecipe["Active"] = False
    
    # Get Ingredients
    allThingsNeeded = []
    for aThing in request.form.getlist('Ingredients[]'):
        if aThing != "":
            allThingsNeeded.append(aThing)
    newRecipe["Ingredients"] = allThingsNeeded

    # Get Numbered Steps
    steps = {}
    count = 1
    for aItem in request.form.getlist('Directions[]'):
        if aItem != "":
            steps[count] = aItem
            count += 1
    newRecipe["Directions"] = steps

    if 'original_title' in request.form:
        print(request.form['original_title'])
        UpdateRecipe(newRecipe, request.form['original_title'])
    else:
        AddRecipe(newRecipe)    
    
    return redirect("/admin")


if __name__ == "__main__":
    ## Run APP
    app.run(host='0.0.0.0', port=8080)