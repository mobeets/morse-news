from formencode import Schema, validators
from model import MorseParamItem

feed_choice_names = ['twitter', 'rss_custom', 'rss_default']
max_name_length = 20
morse_speed_defaults = range(2, 42, 2)
feed_defaults = {
    'Guardian World': 'http://feeds.guardian.co.uk/theguardian/world/rss',
    'Wired': 'http://feeds.wired.com/wired/index',
    'BBC Top Stories': 'http://feeds.bbci.co.uk/news/rss.xml',
    'NYTimes World': 'http://feeds.nytimes.com/nyt/rss/World',
    'Wired Science': 'http://www.wired.com/wiredscience/feed/',
    'FTAlphaville': 'http://ftalphaville.ft.com/blog/feed/',
    'Slate': 'http://feeds.slate.com/slate',
    }

class FeedChoiceForm(Schema):
    feed_choice = validators.String()
    feed_tweets = validators.UnicodeString()
    feed_url = validators.URL()#add_http=True, check_exists=True)
    feed_def = validators.String()
    morse_speed = validators.Int(not_empty=True)
    goal_speed = validators.Int(not_empty=True)
    pitch_var = validators.Bool(not_empty=True)

    def params(self, data):
        morse_speed = data['morse_speed']
        goal_speed = data['goal_speed']
        pitch_var = data['pitch_var']
        return MorseParamItem(morse_speed, goal_speed, pitch_var)

    def choice(self, data):
        is_rss = True
        if data['feed_choice'] == 'twitter':
            name = 'twitter: ' + data['feed_tweets']
            query = data['feed_tweets']
            is_rss = False
        elif data['feed_choice'] == 'rss_default':
            if data['feed_def'] not in feed_defaults:
                pass
            name = data['feed_def']
            query = feed_defaults[data['feed_def']]
        elif data['feed_choice'] == 'rss_custom':
            name = data['feed_url']
            query = data['feed_url']
        return is_rss, name[:max_name_length], query

    def error_msg(self, data):
        msgs = []
        for key, val in data.iteritems():
            if key == 'feed_url':
                key = 'RSS feed url'
            msgs.append(key + ': ' + val)
        return '<br>'.join(msgs)

def input_field(in_id, in_name, in_type, in_value):
    return '<input id="{0}" name="{1}" type="{2}" value="{3}">'.format(in_id, in_name, in_type, in_value)

def select_field(in_id, in_name, opts):
    return '<select id="{0}" name="{1}">{2}</select>'.format(in_id, in_name, ''.join(opts))

def option_field(in_label, in_value):
    return '<option value="{0}">{1}</option>'.format(in_value, in_label)

def feed_choice_form_rows():
    feed_choice_0 = input_field('feed_choice-0', 'feed_choice', 'radio', feed_choice_names[0])
    feed_choice_1 = input_field('feed_choice-1', 'feed_choice', 'radio', feed_choice_names[1])
    feed_choice_2 = input_field('feed_choice-2', 'feed_choice', 'radio', feed_choice_names[2])

    feed_tweets_label = 'Search twitter:'
    feed_tweets = input_field('feed_tweets', 'feed_tweets', 'text', '')

    feed_url_label = 'Enter RSS feed url:'
    feed_url = input_field('feed_url', 'feed_url', 'text', '')

    feed_def_label = 'Choose an RSS feed:'
    feed_def_opts = [option_field(name, name) for name in feed_defaults]
    feed_def = select_field('feed_def', 'feed_def', feed_def_opts)

    pitch_var_label = 'Vary pitch randomly:'
    pitch_var = input_field('pitch_var', 'pitch_var', 'checkbox', 'y')

    morse_speed_label = 'Morse speed:'
    morse_speed_opts = [option_field('{0} WPM'.format(i), i) for i in morse_speed_defaults]
    morse_speed = select_field('morse_speed', 'morse_speed', morse_speed_opts)

    goal_speed_label = 'Goal speed:'
    goal_speed_opts = [option_field('N/A', 0)] + morse_speed_opts
    goal_speed = select_field('goal_speed', 'goal_speed', goal_speed_opts)
    
    submit = input_field('submit', 'submit', 'submit', 'Submit')

    return [
        [feed_choice_0 + ' ' + feed_tweets_label, feed_tweets],
        [feed_choice_1 + ' ' + feed_url_label, feed_url],
        [feed_choice_2 + ' ' + feed_def_label, feed_def],
        [morse_speed_label, morse_speed],
        [goal_speed_label, goal_speed],
        [pitch_var_label, pitch_var],
        ['', submit],
    ]
