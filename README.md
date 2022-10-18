# Helium-LoRaWAN
## Method to use flask run on backend
1. Download app.py

2. In terminal, for Mac input:
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

3. Set environment
```
FLASK_ENV=dev

```
or 
```
$ FLASK_ENV=development

```

4. Run(Frontend and Backend must run simultaneously)
```
flask run

```
