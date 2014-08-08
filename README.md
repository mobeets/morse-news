### Make your own morse .wav files

```
python bin/morse_wav_gen.py --infile message.txt --outfile outfile.wav --wpm 20
```

### Or, set up morse_news web app locally:

Install requirements, create heroku app, create heroku database
```
$ sudo pip install -r requirements.txt
$ heroku create --stack cedar
$ heroku apps:rename APPNAME
```

Create .env file with your twitter app keys:
```
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
```

Now tell heroku they're in .env
```
$ heroku plugins:install git://github.com/ddollar/heroku-config.git
$ heroku config:push
```

Go!
```
$ foreman start
```
