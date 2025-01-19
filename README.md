Coming soon inc

Setup local env
```bash
pip3 install virtualenv 
apt install python3.11-venv
python3 -m venv env source env/bin/activate 
pip3 install -r src/requirements.txt 
python3 -m flask run
```

Deactivate local env
```bash
deactivate
```


Configure Service Account for GCP
```bash
gcloud iam service-accounts create sa-recipe \
    --description="Recipe GCS" \
    --display-name="sa-recipe"

gcloud projects add-iam-policy-binding rgreaves-sandbox \
    --member=serviceAccount:sa-recipe@rgreaves-sandbox.iam.gserviceaccount.com --role=roles/storage.objectAdmin

gcloud iam service-accounts keys create ~/key.json \
  --iam-account sa-recipe@rgreaves-sandbox.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="~/key.json"
```