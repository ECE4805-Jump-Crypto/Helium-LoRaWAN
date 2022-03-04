# Helium-LoRaWAN

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
python3 main.py
```

## Workflow

### Do not commit API Keys or other sensitive material to version control. These will be distrubuted between team members outside of github. Also, do not commit non-source code files. Place these in the .gitignore

When working on a feature first checkout a new branch and give it a good name

Ensure that you are on the master branch (branch should be master):

```
git status
```

Then checkout a new branch. 
If I were adding a feature that adds google maps integration I would give the branch a name like
```
git checkout -b nmeine-add-google-maps
```

Make sure that you're on the new branch
```
git status
```

Work and add commits, periodically checking for upstream merges into master (this will save time and reduce merge conflicts later on). 

You should also periodically push your branch to github
```
git add <files>
git commit -m <commit message>
git pull origin master
git merge master <your branch>
git push origin <your branch>
```
*Note: If you add dependencies, you need to update the requirements file and add that to your commit. Example shown below*

```
pip freeze > requirements.txt
git add requirements.txt
git commit -m "updated requirements"
```








