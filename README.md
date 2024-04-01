# Word Chain bot

Word Chain bot is a community game discord bot written in python the discord.py. Members of a discord server can play a word chain game with it.
The bot apparently only supports the following languages:
- English (US)
- English (GB)
- Hungarian

## Modification

It can easily be extended, and maybe will be by me in the future. But you can do it yourself, you only need to modify the `Dockerfile`, and the `init/init.sql` file.
In the `Dockerfile` you need to download the suitable hunspell linux package, because the bot is spell checking every word in that language you chose.
You can see the supported languages on [hunspell's gitHub](https://github.com/hunspell/hunspell).

In the `init/init.sql` file you have to add the added languages at the bottom, and the special character the language have(characters that are more than one letter).

## Starting the bot

You can run the bot with docker, after you filled your data in the `.env`, `db_env/.env` files, which you can find in the release branch.

