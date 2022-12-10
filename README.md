# Helium-LoRaWAN

## Dependencies
- SPLAT!
- Python3 3.8+


## Pre-reqs

Ensure python3 is installed and up-to-date (python 3.8+ is optimal)

```
python3 -V
```


## Installation & Usage

Clone the repository using ssh keys
```
git clone git@github.com:ECE4805-Jump-Crypto/Helium-LoRaWAN.git
cd Helium-LoRaWAN
```

Create virtual environment
```
python3 -m venv .venv
```

Activate environement on *nix systems:
```
source .venv/bin/activate
```

Or on windows:
```
.venv/Scripts/activate
```

Install requirements:
```
pip install -r requirements.txt
```

Run the code:
```
python3 -m simulate -h
```

To start the backend server:
```
python3 -m src.server
```

This will start a flask server running at 0.0.0.0 port 3000
Ensure that the front end gui is also running. Check repository for how to start





