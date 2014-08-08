import os
import pickle

import cherrypy
from formencode import Invalid
from mako.lookup import TemplateLookup

import conf
from bin.model import MorseParamItem, MorseWavTask, query_to_content
from bin.forms import feed_choice_form_rows, FeedChoiceForm
from bin.twitter_search import user_handle

lookup = TemplateLookup(directories=['templates'])
class Root(object):
    def __init__(self, data, exec_path, outdir):
        self.data = data
        self.exec_path = exec_path
        self.outdir = outdir
        self.twitter_handle = user_handle()

    def recently_added(self):
        dts = sorted(self.data)[-5:]
        return [self.data[dt] for dt in reversed(dts)]

    @cherrypy.expose
    def default(self, *data):
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def index(self, **data):
        result, errors = '', ''
        if cherrypy.request.method == 'POST':
            result, errors = self.process_form(data)
        recents = self.recently_added()
        no_news_yet = 'No news yet! Create a .wav below.' if not recents else ''
        tmp = lookup.get_template('index.html')
        return tmp.render(no_news_yet=no_news_yet, wav_rows=recents, result=result, errors=errors, form_rows=feed_choice_form_rows())

    def process_form(self, in_data):
        form = FeedChoiceForm(allow_extra_fields=True, filter_extra_fields=True)
        try:
            data = form.to_python(in_data)
        except Invalid, e:
            errors = e.unpack_errors()
            return '', form.error_msg(errors)
        is_rss, name, query = form.choice(data)
        params = form.params(data)
        return self.add(name, query, is_rss, params)

    def add(self, name, query, is_rss, params):
        content = query_to_content(query, is_rss, self.twitter_handle)
        if not content:
            return '', 'No results found for query: ' + query
        m = MorseWavTask(self.exec_path, self.outdir, name, params, content)
        self.data[m.item.dt] = m.item
        return m.msg(), ''

def load_db_as_dict(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except:
        raise
        return {}

def save_dict_as_db(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def inner_main(settings):
    dbfile = settings['dbfile']
    save_dict_as_db(dbfile, {}) # clear db
    exec_path = settings['exec_path']
    outdir = settings['media_dir']
    data = load_db_as_dict(dbfile)
    r = Root(data, exec_path, outdir)
    return r, lambda: save_dict_as_db(dbfile, r.data)

def main():
    cherrypy.config.update(conf.settings)
    
    morse_gen_app, morse_gen_flush = inner_main(conf.morse_gen_settings)
    root_app = cherrypy.tree.mount(morse_gen_app, '/', conf.root_settings)
    root_app.merge(conf.settings)

    if hasattr(cherrypy.engine, 'subscribe'): # CherryPy >= 3.1
        cherrypy.engine.subscribe('stop', morse_gen_flush)
    else:
        cherrypy.engine.on_stop_engine_list.append(morse_gen_flush)

    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()
