# Playlist Converter

Convert a text file of songs to a playlist on your <a href="https://open.spotify.com/">Spotify account</a>. Create your playlists faster instead of manually searching for songs.

<!-- DEMO Video/Picture -->
<!-- Table of Contents -->
<!-- How It Works -->

## Getting Started

Before running this project locally, make sure you meet/install the prerequisites listed below. After meeting the prerequisites, follow the instructions in the **Installation** section.

### Prerequisites

#### Spotify Account

If you don't already have a Spotify account, go to their <a href="https://www.spotify.com/us/signup/">sign up page</a> and create one.

#### Python 3.6+

You must have <a href="https://www.python.org/downloads/">Python</a> version 3.6 or greater installed on your computer.

Once you've installed Python, open Git Bash or your preferred CLI on Windows, or Terminal on Linux/MAC. Run this command to verify you have the right version of Python:
```
python --version
# Python 3.*
```

### Installation

1\. Clone this repository on your machine.
```
git clone https://github.com/pa-aggarwal/playlist-converter.git
```

2\. Create a python virtual environment and install the packages in the `requirements.txt` file.
```
# Navigate to directory
cd playlist-converter

# Create virtual environment 'venv'
python -m venv venv

# Install packages from requirements.txt
python -m pip install -r requirements.txt
```

3\. You must create your own configuration file called `config.ini` in the config directory, by copying the template config `template.ini` file.
```
# Copy the template config file
cp config/template.ini config/config.ini
```
Open the `config.ini` file in your preferred text editor and change the values of the config options to match your file setup. See the **Configuration** section for what these options are and how to fill them in.

4\. Visit https://developer.spotify.com/console/get-search-item/ to get an access token from Spotify. Check mark the following scopes to authenticate this application:
* user-library-read
* playlist-modify-public
* playlist-modify-private

Copy and paste the access token into your configuration file under the `access_token` option.

### Configuration

What are the config options and how do I fill them in?
* `directory_path`: Absolute path to the directory containing the text file(s) to convert
* `data_order`: Value is "track artist" or "artist track" based on how data appears in your files
* `data_delimiter`: The characters separating track name from artist name
* `user_id`: Your username on your spotify account
* `access_token`: Token value from step 4 of installation section

See the **Usage** section for an example of a configuration file and what a text file to convert looks like.

<!-- Usage -->
<!-- Contributing -->
<!-- Contact -->
<!-- Acknowledgements -->
<!-- License -->
