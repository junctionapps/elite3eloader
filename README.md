![Screenshot](./docs/screenshot001.png?raw=true)
# elite3eloader
The purpose of this loader is to do away with multiple Excel sheets for loading data into Elite 3E. Keep in mind this is beta software, and there remains some fine tuning, however, the basic functionality is intact.

## Setup - First time only
This is a web based application meant to be run on the local machine (not a server), so there is a little setup to be done to make that happen. The reason for running locally in this manner, and not hosted on a firm server is because due to the target audience for such an application. I determined the user of this application would be a 3E administrator or Financial Analyst. Running it locally may be easier than convincing an IT department to host it on a server; although, it is ready to be hosted in that way, but you'd probably want to use a service account for credentials and handle reassigning the processes in 3E somehow.  

1. You need Python 3.7 or better. [Download and install here](https://www.python.org/downloads/) 

2. Clone this repository using the **Clone or Download** button above. Download the zip if you are not familiar with ssh or git. Unzip the file to a location on your local machine. For this documentation we're going to assume you extracted it to c:\dev\elite3eloader-master

3. Setup virtual environment
    - Open a command prompt (press Windows Key + R, then type in `cmd`)
    - Change directory to where you extracted the repo `cd c:\dev\elite3eloader-master`
    - Create a Python 3.7 virtual environment by typing `python -m venv venv` This may take a few moments.
    - If you get an error on the above line, or had an older version of python installed you may need to specify the path to Python 3.7 like: `c:\Python\    Python37\python -m venv venv` (do this while still in the `c:\dev\elite3eloader-master` directory) substituting the path to where ever you installed Python 3.7 (it may be in your c:\users\youruser\appdata\local....). 
 
4. Activate Virtual environment
    - at this point if you type `dir` you should see two folders in c:\dev\elite3eloader-master: (1) `venv` and (2) `elite3eloader-master`. We need to run a script in the virtual environment to activate it. 
    - type: `venv\Scripts\activate.bat` which will change your prompt to include the virtual environment name in the prompt to show it is active.

5. There are a number of libraries we'll need to download to make the application work. You can examine them in the elite3eloader-master\requirements.txt file if you want to take a peek, or install them now by typing `pip install -r elite3eloader-master\proj\requirements.txt` Expect this to take a few moments.

6. Hoping everything is going well. Now. we need to create a folder to store some static files. Create two folders under cdn to house these static folders: `mkdir elite3eloader-master\cdn\media` and `mkdir elite3eloader-master\cdn\static`. If you were look inside of the `c:\dev\elite3eloader-master\elite3eloader-master` folder now you should see folders `cdn`, `proj`, `docs`, `venv`, and files named `initial.json` and `README.md` (this file).

7. We need to change into the c:\dev\elite3eloader-master\elite3eloader-master\proj folder. Do that by typing `cd c:\dev\elite3eloader-master\elite3eloader-master\proj`. Now run `python manage.py collectstatic`. You should see a line like `122 static files copied to 'c:\dev\elite3eloader-master\elite3eloader-master\cdn\static`. This moves some files out of the proj folder and into an area for our server to serve them.

6. We should be all set now. While still in the `proj` folder Lets turn on the app by typing `python manage.py runserver`. This command will make the available only to the local machine. Ideally we should see no errors but a prompt telling us that the development server has started at http://127.0.0.1:8000/

7. Use Chrome to visit [http://127.0.0.1](http://127.0.0.1), where you should see the license which we'll go over next as we've moved past the setup phase.


## Running after setup is completed
If we want to tun on the service again later, the steps to follow are similar to 4 and 6 above.

Open a windows command prompt (Windows + R, type `cmd`)

`cd c:\dev\elite3eloader-master\`

`venv\Scripts\activate.bat`

`cd elite3eloader-master\proj`

`python manage.py runserver`

Then browse in your browser to http://127.0.0.1:8000


[Okay, we should be ready to use the loader](USAGE.md)
