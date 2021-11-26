import unicodedata

def load():
    path = input('Path to file: ')
    mapping = dict()
    try:
        with open(path) as file:
            for line in file:
                codepoint, seq = line.split()[:2]
                codepoint = int(codepoint, 16)
                if codepoint not in mapping:
                    mapping[codepoint] = set()
                mapping[codepoint].add(seq)
    except FileNotFoundError:
        print('Could not find that file!')
    return mapping

def get_codepoint(message):
    s = input(message)
    if len(s) == 1:
        return ord(s)
    if s.startswith('0x'):
        return int(s, 16)
    try:
        return int(s)
    except:
        print('That is not a valid codepoint.')
    return 160

def causes_collision(mapping, seq, curr_codepoint):
    for codepoint in mapping:
        if codepoint == curr_codepoint:
            continue
        for seq2 in mapping[codepoint]:
            if seq.startswith(seq2) or seq2.startswith(seq):
                print('Collision with', hex(codepoint), chr(codepoint), seq2)
                return True
    return False

def check(mapping):
    ok = True
    key_pairs = [(k1, k2) for k1 in mapping for k2 in mapping if k1 < k2]
    for k1, k2 in key_pairs:
        seq_pairs = [(s1, s2) for s1 in mapping[k1] for s2 in mapping[k2]]
        for s1, s2 in seq_pairs:
            if s1.startswith(s2) or s2.startswith(s1):
                print('Collision between', hex(k1), chr(k1), s1, 'and',
                    hex(k2), chr(k2), s2)
                ok = False
    if ok:
        print('Everything seems fine.')

def edit(mapping):
    print('Now editing sequences.',
        '(commands menu/move/skip/filter/delete/undo/help)')
    codepoint = get_codepoint('Where do you want to start? (e.g. 0xa0) ')
    prev = codepoint
    skipping = False
    filter = ''
    while True:
        try:
            if codepoint > 0x10ffff:
                if filter != '':
                    print('Nothing ahead seems to match the filter.')
                    filter = ''
                else:
                    print('Reached the end of all the codepoints.')
                codepoint = prev
                continue
            name = unicodedata.name(chr(codepoint))
        except ValueError as e:
            if filter == '' and not skipping:
                print('No name for codepoint', codepoint)
            codepoint += 1
            continue
        if not filter in name:
            codepoint += 1
            continue
        if codepoint in mapping:
            if skipping:
                codepoint += 1
                continue
            print(hex(codepoint), chr(codepoint), name,
                '-- current sequences:', *mapping[codepoint])
        else:
            print(hex(codepoint), chr(codepoint), name)
        cmd = input(': ')
        if cmd == 'menu':
            return
        elif cmd == 'move':
            codepoint = get_codepoint('Where to? ')
        elif cmd == 'skip':
            skipping = not skipping
            print(('S' if skipping else 'Not s') + 'kipping filled codepoints')
        elif cmd == 'filter':
            filter = input('Filter string: ')
            prev = codepoint
        elif cmd == 'delete':
            if codepoint in mapping:
                del mapping[codepoint]
        elif cmd == 'undo':
            codepoint = prev
            del mapping[codepoint]
        elif cmd == 'help':
            print('Go read the code.')
        else:
            seqs = set()
            for seq in cmd.split():
                if causes_collision(mapping, seq, codepoint):
                    break
                seqs.add(seq)
            else:
                if len(seqs) > 0:
                    mapping[codepoint] = seqs
                    prev = codepoint
                codepoint += 1

def show(mapping):
    print('Type "all" at any time to show all sequences.')
    cmd = input(': ')
    for codepoint in sorted(mapping.keys()):
        if cmd != 'all':
            print(hex(codepoint), chr(codepoint),
                unicodedata.name(chr(codepoint)))
            cmd = input(': ')
            if cmd != chr(codepoint) * len(mapping[codepoint]):
                print('=', *mapping[codepoint], '\n')
        else:
            print(hex(codepoint), chr(codepoint), '=', *mapping[codepoint])

def save(mapping):
    path = input('Path to file: ')
    with open(path, 'w') as file:
        for codepoint in sorted(mapping.keys()):
            for seq in mapping[codepoint]:
                file.write(hex(codepoint) + ' ' + seq + ' '
                    + ' ' * (14 - len(seq)) + chr(codepoint) + ' '
                    + unicodedata.name(chr(codepoint)) + '\n')

def compile(mapping):
    key_names = {
        '`': 'grave', '~': 'asciitilde', '!': 'exclam', '@': 'at',
        '#': 'numbersign', '$': 'dollar', '%': 'percent', '^': 'asciicircum',
        '&': 'ampersand', '*': 'asterisk', '(': 'parenleft', ')': 'parenright',
        '-': 'minus', '_': 'underscore', '=': 'equal', '+': 'plus',
        '[': 'bracketleft', '{': 'braceleft', ']': 'bracketright',
        '}': 'braceright', '\\': 'backslash', '|': 'bar', ';': 'semicolon',
        ':': 'colon', '\'': 'apostrophe', '"': 'quotedbl', ',': 'comma',
        '<': 'less', '.': 'period', '>': 'greater', '/': 'slash',
        '?': 'question'
    }
    path = input('Path to file: ')
    with open(path, 'w') as file:
        for codepoint in sorted(mapping.keys()):
            for seq in mapping[codepoint]:
                file.write('<Multi_key>')
                at = False
                for c in seq:
                    w = c
                    if at:
                        if c == '@':
                            w = 'Multi_key'
                        elif c == 's':
                            w = 'space'
                        elif c == '<':
                            w = 'at'
                        else:
                            print('I do not know the symbol @' + c)
                            return
                        at = False
                    elif c == '@':
                        at = True
                        continue
                    elif c in key_names:
                        w = key_names[c]
                    elif not ('0' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'):
                            print('I do not know the symbol ' + c)
                    file.write(' <' + w + '>')
                file.write(' : "' + chr(codepoint) + '"\n')

def main():
    mapping = dict()
    while True:
        print('What would you like to do?',
            '(load/edit/check/show/save/compile/quit)')
        cmd = input()
        if cmd == 'load':
            mapping = load()
        if cmd == 'edit':
            edit(mapping)
        if cmd == 'check':
            check(mapping)
        if cmd == 'show':
            show(mapping)
        if cmd == 'save':
            save(mapping)
        if cmd == 'compile':
            compile(mapping)
        if cmd == 'quit':
            break

if __name__ == '__main__':
    main()
