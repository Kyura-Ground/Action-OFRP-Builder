#!/usr/bin/env python3
"""Use shallow clones throughout the downloaded OrangeFox sync helper."""
from pathlib import Path
import re
import sys


def shallow_commands(source):
    counts = {'git clone': 0, 'repo init': 0}

    def update(match):
        indent, command, arguments = match.groups()
        counts[command] += 1
        # Override any upstream depth before adding one consistent value.
        arguments = re.sub(r'(?<!\S)--depth(?:=|\s+)[^\s;]+', '', arguments).lstrip()
        options = ['--depth=1']
        if command == 'git clone':
            options += [flag for flag in ['--single-branch', '--no-tags']
                        if flag not in arguments.split()]
        else:
            arguments = re.sub(r'(?<!\S)--manifest-depth(?:=|\s+)[^\s;]+', '', arguments).lstrip()
            options.append('--manifest-depth=1')
        return indent + command + ' ' + ' '.join(options) + ' ' + arguments

    result = re.sub(r'(?m)^([ \t]*)(git clone|repo init)([^\n]*)', update, source)
    if not all(counts.values()):
        raise ValueError('Sync helper changed: expected git clone and repo init commands')
    return result, counts


if __name__ == '__main__':
    path = Path(sys.argv[1])
    source, counts = shallow_commands(path.read_text())
    path.write_text(source)
    print(f'Shallow sync configured: {counts}')
