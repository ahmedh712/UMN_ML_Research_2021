Location

Link to paper/resource implemented
https://spacy.io/api/entityrecognizer
https://github.com/napsternxg/TwitterNER
https://pypi.org/project/geotext/
https://github.com/geopy/geopy

Title of classifier
location_pipeline_MSI.py

Fields it expects as input features
twitter location field

Documentation to recreate the classifier set up 

#pip install pandas numpy SpaCy geotext geocoder uszipcode geopy
(or install the same libraries with Conda or preferred env)
SpaCy Setup
python -m spacy download en_core_web_sm
TWITTER NER Setup
Create folder for twitter NER
go to the linked repo above and clone the repo into the said folder
follow instructions on repo for installation:
pip install -r requirements.txt
cd data
wget http://nlp.stanford.edu/data/glove.twitter.27B.zip
unzip glove.twitter.27B.zip
cd ..
Running the pipeline:
First configure the directory and location of the input and output. Ctrl+F the following variables, though they’re all together
Configurable fields within the code
data_directory
file_name
outfile
csize
chunksize for pandas to load the dataset. Since the pipeline uses chunking, the higher the csize the better. I use 3 million, more is always better but with diminishing returns
Once you configure directories and chunks, you’ll have to define the names for the columns of your output since chunking appends each run
saved_colnames
The current default column names are saved_colnames = ['UID', 'Names', 'Declared_Location','Ethnicity','Extracted_Location']
after that the program should run, outputting the defined columns above with the command: 
sbatch -p amdsmall location.sh







Rules you added Explanation (why and how it helps)
The pipeline uses normal case because it helps with twitter NER. It firstly checks it through geotext cities, a a library that has the highest precision of all the methods but a rather lower recall, since it requires near exact matches . Anything not identified by geotext cities is sent to SpaCy and twitter NER to extract a location field from it. Anything not extracted from there is then sent in a last effort to the comma rule, which checks if there is a “city, state” format in the original string, such as “Minneapolis, MN.” If both city and state are extractable, then that is used, or else the state is simply checked with a dictionary lookup and assigned the corresponding full state name (IE MN to Minnesota). Finally, using geopy, the string name is matched via a lookup online to a real location. This pipeline ensures maximum recall to miss the least amount of locations as possible, and then verifies the string location with geopy. For the geopy API lookups, it sorts the locations alphabetically then uses caching since the number of requests geopy allows is ratelimited, meaning this is the bottleneck. The cache allows avoiding repeat lookups. The larger preferred chunk size is so more identical queries can be made per chunk. 

Related Classification Accuracy Results


 

Ethnicity
	
Link to paper/resource implemented
https://spacy.io/api/entityrecognizer
https://github.com/appeler/ethnicolr

Fields it expects as input features
twitter name field
![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
Documentation to recreate the classifier set up (mention which libraries to download and how and the classifier can be run )

pip install pandas  numpy==1.19 nameparser stanza spacy emoji ethnicolr
pip install # python -m spacy download en_core_web_sm en_core_web_md en_core_web_lg
Running the pipeline:
First configure the directory and location of the input and output. Ctrl+F the following variables, though they’re all together
Configurable fields within the code
data_directory
file_name
outfile
csize
chunksize for pandas to load the dataset. Size doesn’t particularly matter for ethnicity classification
Once you configure directories and chunks, you’ll have to define the names for the columns of your output since chunking appends each run
saved_colnames
The current default column names are saved_colnames = ['UID', 'Names', 'Declared_Location', 'Ethnicity']
after that the program should run, outputting the defined columns above with the command: 
sbatch -p amdsmall ethnicty.sh


Rules you added Explanation (why and how it helps)
	The pipeline uses 3 SpaCy libraries because using only one particular one yielded a high number of false negatives, but a blend of all 3 led to nearly no false negatives. Twitter NER was not used as it had worse results extracting names than the SpaCy combination. 
Related Classification Accuracy Results 








