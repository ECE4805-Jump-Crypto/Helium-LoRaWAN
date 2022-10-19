# Helium-LoRaWAN
## Method to use flask run on backend
1. Download app.py

2.import packages:
```
pip install flask
```
```
pip install flask_cors
```

3. In terminal, for Mac input:(after "=" is the file name)
```
export FLASK_APP=app
```
for Windows CMD
```
set FLASK_APP=app
```
for Windows PowerShell:
```
$env:FLASK_APP = "app"

```

4. Set environment
```
set FLASK_ENV=dev

```
or 
```
$ FLASK_ENV=development

```

5. Run(Frontend and Backend must run simultaneously)
```
flask run

```
