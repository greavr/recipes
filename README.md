Coming soon inc

pip3 install virtualenv 
python3 -m venv env source env/bin/activate 
pip3 install -r requirements.txt 
export FLASK_APP=main.py 
export FLASK_ENV=development 
python3 -m flask run

deactivate


gcloud iam service-accounts create sa-recipe \
    --description="Recipe GCS" \
    --display-name="sa-recipe"

gcloud projects add-iam-policy-binding rgreaves-sandbox \
    --member=serviceAccount:sa-recipe@rgreaves-sandbox.iam.gserviceaccount.com --role=roles/storage.objectAdmin

gcloud iam service-accounts keys create ~/key.json \
  --iam-account sa-recipe@rgreaves-sandbox.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="~/key.json"
export GCS_LOC="gs://rgreaves-recipes/new_recipes.json"