VERSION_FILENAME = 'version.py'

def update_version(ui, repo, **kwargs):
    tag_name = kwargs['tag']
    if tag_name.startswith('v'):
        print '[pretag hook] updating version.py file with version : ', tag_name
        with open(VERSION_FILENAME, 'w') as f:
            f.write("VERSION = '{0}'".format(tag_name))
    else:
        print '[pretag hook] tag:{0} does not look like a version tag, ignoring it'.format(tag_name)