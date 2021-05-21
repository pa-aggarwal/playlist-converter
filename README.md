# Playlist Converter

[![Python](https://img.shields.io/badge/python-3.6%2B-blue?style=flat-square)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](./tests)
[![License: MIT](https://img.shields.io/github/license/pa-aggarwal/playlist-converter?color=orange&style=flat-square)](https://opensource.org/licenses/MIT)

Convert a text file of songs to a playlist on your <a href="https://open.spotify.com/">Spotify account</a>. Create your playlists faster instead of manually searching for songs.

![Demo](./assets/demo.gif)

Recorded using <a href="https://www.screentogif.com/">ScreenToGif</a>.

## Table of Contents

* [How It Works](#how-it-works)
* [Credits](#credits)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Configuration](#configuration)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)

## How It Works

* This application reads the contents of every text file in a directory on your computer
* You must provide details of how your files are structured in a configuration file
* Getting a temporary access token from Spotify authorizes this app to access/change your account data
* Using the Python requests library, this application sends the data to Spotify's web API to create the playlist

## Credits

* <a href="https://developer.spotify.com/documentation/web-api/">Spotify Web API</a>
* <a href="https://docs.python-requests.org/en/master/">Requests Library V2.25.1</a>

## Getting Started

Before running this project locally, make sure you meet/install the prerequisites listed below. After meeting the prerequisites, follow the instructions in the [Installation](#installation) section.

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

2\. Create a python virtual environment, activate it, and install the packages in the `requirements.txt` file.
```
# Navigate to directory
cd playlist-converter

# Create virtual environment 'venv'
python -m venv venv

# Activate virtual environment
. venv/Scripts/activate

# Install packages from requirements.txt
python -m pip install -r requirements.txt
```

3\. You must create your own configuration file called `config.ini` in the config directory, by copying the template config `template.ini` file.
```
# Copy the template config file
cp config/template.ini config/config.ini
```
Open the `config.ini` file in your preferred text editor and change the values of the config keys to match your file setup. See the [Configuration](#configuration) section for what these keys are and how to fill them in.

4\. Visit https://developer.spotify.com/console/get-search-item/ to get a temporary access token from Spotify. Check mark the following scopes to authenticate this application:
* user-library-read
* playlist-modify-public
* playlist-modify-private

Copy and paste the access token into your configuration file under the `access_token` option.

**Note:** Spotify's access tokens expire after 1 hour, so you'll need to repeat this step if you're using this application again at a later time.

### Configuration

What are the config keys and how do I fill them in?
* `directory_path`: Absolute path to the directory containing the text file(s) you want to convert
* `data_order`: `track artist` or `artist track` based on how songs are listed in your files.
* `data_delimiter`: The characters separating track name from artist name(s), preferrably at least 3 chars long e.g. `---`, `###`
* `user_id`: Your username on your spotify account
* `access_token`: Token value from step 4 of [Installation](#installation)

Here is an example file setup (location and contents), along with a configuration file:

```
$ pwd
C:\Users\user\Desktop\playlists

$ ls
playlist-01.txt playlist-02.txt

$ cat playlist-01.txt
Name: My Playlist
3005---Childish Gambino
See You Again---Tyler, The Creator, Kali Uchis
...
```

`config.ini`
```
[FILE_INFO]
directory_path = C:\Users\user\Desktop\playlists
data_order = track artist
data_delimiter = ---

[API]
user_id = priyaaggarwal
access_token = long-key-from-spotify
```

## Usage

Make sure you've completed steps from the [Installation](#installation) section before running this application. This includes making your configuration file and putting text files to convert in their own directory.

In the cloned repository with the venv activated, run this command to create your playlists:
```
python -m playlist_converter.app
```
This may take a couple of minutes depending on how large your files are.

You may see an error message if there was an issue trying to convert your files, like one of the following:
* Missing configuration file or config keys
* Invalid directory path
* No text files found to convert
* HTTP error from invalid access token or something else

If you received no errors, then open your spotify account to see your new playlists.

To check if tests are passing, run this command:
```
python -m unittest discover -s tests
```

## Contributing

Contributions and feedback for improvements as well as new features are welcome!
1. Fork this repository.
2. Create a new branch for your contribution (`git checkout -b new-feature`).
3. Add your contribution, and write tests if needed.
4. Ensure the test suite passes.
5. Commit your changes to the branch (`git commit -m "My new feature does X"`).
6. Push to the branch (`git push origin new-feature`).
7. Open a pull request.

## License

Distributed under the MIT License. See [LICENSE.txt](https://github.com/pa-aggarwal/playlist-converter/blob/master/LICENSE.txt) for more information.
