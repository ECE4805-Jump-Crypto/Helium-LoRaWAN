# Helium-LoRaWAN
## Method to use flask run on backend
1. In back folder import packages:
```
pip install flask
```
```
pip install flask_cors
```

2. In terminal, for Mac input:(after "=" is the file name)
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
set FLASK_ENV=dev

```
or 
```
$ FLASK_ENV=development

```

4. Run(Frontend and Backend must run simultaneously)
```
flask run

```
