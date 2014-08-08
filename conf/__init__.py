import os
CURDIR = os.path.dirname(os.path.abspath(__file__))
ROOTDIR = os.path.abspath(os.path.join(CURDIR, '..'))

settings = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', '5000')),
        'server.environment': 'development',
    },
}

root_settings = {
    '/': {
        'tools.staticdir.root': ROOTDIR,
    },
    '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': os.path.join(ROOTDIR, 'static', 'favicon.ico')
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static'
    },
    '/media': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'media'
    }
}

morse_gen_settings = {
    'dbfile': os.path.join(ROOTDIR, 'db', 'morse_gen.db'),
    'exec_path': os.path.join(ROOTDIR, 'bin', 'morse_wav_gen.py'),
    'media_dir': 'media/'
}
