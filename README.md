# CRSEC
A novel agent architecture to facilitate the emergence of social norms within a generative agent society.

## Setting Up the Environment 

To set up your environment, you will need to generate a `utils.py` file that contains your OpenAI API key and download the necessary packages.

### Step 1. Generate Utils File

In the `reverie/backend_server` folder (where `reverie.py` is located), create a new file titled `utils.py` and copy and paste the content below into the file:

```
# Copy and paste your OpenAI API Key
openai_api_key = "<Your OpenAI API>"
# Put your name
key_owner = "<Name>"

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose 
debug = True
```

Replace `<Your OpenAI API>` with your OpenAI API key, and `<name>` with your name.

### Step 2. Install requirements.txt

Install everything listed in the `requirements.txt` file (I strongly recommend first setting up a virtualenv as usual). A note on Python version: we tested our environment on Python 3.9.7. 

## Running a Simulation 

To run a new simulation, you will need to concurrently start two servers: the environment server and the agent simulation server.

### Step 1. Starting the Environment Server

Again, the environment is implemented as a Django project, and as such, you will need to start the Django server. To do this, first navigate to `environment/frontend_server` (this is where `manage.py` is located) in your command line. Then run the following command:

    python manage.py runserver

Then, on your favorite browser, go to [http://localhost:8000/](http://localhost:8000/). If you see a message that says, "Your environment server is up and running," your server is running properly. Ensure that the environment server continues to run while you are running the simulation, so keep this command-line tab open!

### Step 2. Starting the Simulation Server

Open up another command line (the one you used in Step 1 should still be running the environment server, so leave that as it is). Navigate to `reverie/backend_server` and run `reverie.py`.

    python reverie.py

This will start the simulation server. A command-line prompt will appear, asking the following: "Enter the name of the forked simulation: ". To start a 10-agent simulation without any initial norm, type the following:

    base_the_ville_n10

The prompt will then ask, "Enter the name of the new simulation: ". Type any name to denote your current simulation (e.g., just "test-simulation" will do for now).

    test-simulation

Initialization will then started.

### Step 3. Creating norms for entrepreneurs

After the initialization, the prompt will ask the following: "Regenerate norms? (y or n): ". To generate norms for an norm entrepreneur, type "y", otherwise, type "n".

```
# generate norms
y
# otherwise
n
```

If you chose "y" in the last step, the prompt will then ask, "Enter the name of the entrepreneur: ". Type a name of an agent who's identify is  "entrepreneur". In our setup, there are 3 norm entrepreneurs: Abigail Chen, Bob Johnson and Francisco Lopez. Type the name of any one of them to complete a generation round.

```
# e.g.,
Abigail Chen
```

After completing norm generation, it will prompt "Regenerate norms? (y or n):" again. Type "y" to either generate norms for another entrepreneur or redo the generation for the current agent. When all norm generation is complete, type"n" to end this stage.

Then it will display the following prompt: "Enter option: "
