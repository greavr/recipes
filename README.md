Coming soon

pip3 install virtualenv 
python3 -m venv env source env/bin/activate 
pip3 install -r requirements.txt 
export FLASK_APP=index.py 
export FLASK_ENV=development 
python3 -m flask run

deactivate
