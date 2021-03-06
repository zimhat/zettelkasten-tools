import os
from slugify import slugify
import subprocess
import re

zk_archive = os.path.expanduser("~/Documents/zettelkasten/")
# don't forget trailing slash

def get_title(zk_archive, filename):
    '''
    Retrieve the title

    zk_archive -- str, path of the zettelkasten
    filename -- str, name of the zettel
    '''
    z_path = zk_archive + filename
    with open(z_path, 'r') as z:
        z_title = z.readline().rstrip()
    return z_title

def gen_slug(filename, title):
    '''
    Generate the good filename from the old one + title

    filename -- str, old filename
    title -- str, first line of the zettel
    '''
    z_id = filename[:12]  # 12 is the length of my timestamp
    z_title_slug = slugify(title)
    z_new_filename = z_id + '-' + z_title_slug + '.rst'
    return z_new_filename

def git_cmd(cmd, zk_archive):
    '''
    Execute the specified git cmd

    cmd -- str, git command
    zk_archive -- str, path of the zettelkasten
    '''
    return subprocess.run(cmd.split(), cwd=zk_archive)

def get_all_zettels(zk_archive):
    '''
    Return a list of all zettels

    zk_archive -- str, path of the zettelkasten
    '''
    z_files = list()
    for z_filename in os.listdir(zk_archive):
        if '.rst' in z_filename:
            z_files.append(z_filename)
    return z_files

def gather_links(z_filename, zk_archive):
    '''
    Retrieve all the links inside a zettel

    z_filename -- str, name of the zettel
    zk_archive -- str, path of the zettelkasten
    '''
    with open(zk_archive + z_filename, 'r') as z:
        z_content = z.read()
    regex_links = r"\[\[([0-9]{12}.*?\.rst)\]\]"
    z_links = re.findall(regex_links, z_content)
    without_sources = list()
    for link in z_links:
        if 'sources/' not in link:
            without_sources.append(link)
    return without_sources

def find_filename(z_id, zk_archive):
    '''
    Find the filename of the zettel beginning with the specified id.

    z_id -- str, former unique ID of the zettel, like 198707052100
    '''
    for z_filename in get_all_zettels(zk_archive):
        if z_id in z_filename:
            return z_filename

def change_links(z_filename, zk_archive):
    '''
    Replace all the links in the zettel by good ones

    z_filename -- str, name of the zettel
    zk_archive -- str, path of the zettelkasten
    '''
    z_links = gather_links(z_filename, zk_archive)
    with open(zk_archive + z_filename, 'r') as z:
        z_content = z.read()
    for link in z_links:
        z_new_link = find_filename(link[:12], zk_archive)  # this works because it presumes all the filenames have been checked with zk_slugify
        z_content = z_content.replace(link, z_new_link)
    with open(zk_archive + z_filename, 'w') as z:
        z.write(z_content)

def zk_slugify(zk_archive):
    '''
    Rename every zettel that needs it

    zk_archive -- str, path of the zettelkasten
    '''
    #git_add = 'git add *.rst'
    #git_cmd(git_add, zk_archive)
    z_files = get_all_zettels(zk_archive)
    for z_filename in z_files:
        z_title = get_title(zk_archive, z_filename)
        z_new_filename = gen_slug(z_filename, z_title)
        if z_new_filename != z_filename:
            git_mv = 'git mv {} {}'.format(z_filename, z_new_filename)
            git_cmd(git_mv, zk_archive)

def zk_change_all_links(zk_archive):
    '''
    Make all links valid links with the proper ID

    zk_archive -- str, path of the zettelkasten
    '''
    zettels = get_all_zettels(zk_archive)
    for zettel in zettels:
        z_links = gather_links(zettel, zk_archive)
        if z_links != []:
            try:
                change_links(zettel, zk_archive)
            except TypeError:
                print("Problem of link in {}".format(zettel))
                print(z_links)

def zk_find_orphans(zk_archive):
    '''
    Find zettels that don't have any links to them

    zk_archive -- str, path of the zettelkasten
    '''
    zettels = get_all_zettels(zk_archive)
    linked_zettels = list()
    for zettel in zettels:
        links = gather_links(zettel, zk_archive)
        for link in links:
            if link not in linked_zettels:
                linked_zettels.append(link)
    not_linked = list()
    for zettel in zettels:
        if zettel not in linked_zettels:
            not_linked.append(zettel)
    return not_linked

if __name__ == "__main__":
    #zk_archive = 'tests/sources/'
    zk_slugify(zk_archive)
    zk_change_all_links(zk_archive)
