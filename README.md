# Humble Trove Downloader

`HumbleTrove` is used to create a complete backup of your entire Humble Trove library.

If you've downloaded a game already, it will only download updates for the game.

## Installation

Your Python version must be at least 3.6, but newer versions are much appreciated.

You must clone the repository, then install our prerequisities using Python's pip utility.

```
git clone https://github.com/darktohka/HumbleTrove
cd HumbleTrove

python -m pip install -r requirements.txt
```

## Cookies

In order to run the program, you must provide the `_simpleauth_sess` cookie.

First, create a `cookie.txt` file in the root directory, next to the `requirements.txt` file. After that, you'll have to find your `_simpleauth_sess` cookie.

Log into Humble Bundle first!

On Chrome, simply open Chrome's Dev Tools using Ctrl+Shift+I, then press the `Application` tab, and navigate to `Cookies` under `Storage`.

Find `_simpleauth_sess` in the table, and copy its value into the `cookie.txt` file you created.

## Running

On Windows, simply run `start.bat` to download all games from your Humble Trove.

There is another utility, `verify.bat`, which will complete a full hash verification of your game library. This operation takes a long time, however, and is only recommended if you have corrupt game files.

You can also run the program directly from the shell:

- To download all games for your platform: `python -m humbletrove.HumbleTrove`
- To download and verify all games for your platform: `python -m humbletrove.HumbleTrove --verify`
- To download all games on all platforms: `python -m humbletrove.HumbleTrove --windows --linux --mac`

Feel free to mix those options together if needed!