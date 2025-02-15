#!/usr/bin/env python3
import sys
import os

import optparse
import chpl_locale_model, chpl_tasks, chpl_platform, overrides, third_party_utils
from utils import error, memoize, warning, try_run_command, run_command


@memoize
def get():
    hwloc_val = overrides.get('CHPL_HWLOC')
    if not hwloc_val:
        tasks_val = chpl_tasks.get()
        if tasks_val == 'qthreads':
            hwloc_val = 'bundled'
        else:
            hwloc_val = 'none'

    return hwloc_val


@memoize
def get_uniq_cfg_path():
    return '{0}-{1}'.format(third_party_utils.default_uniq_cfg_path(),
                            chpl_locale_model.get())


# returns 2-tuple of lists
#  (compiler_bundled_args, compiler_system_args)
@memoize
def get_compile_args():
    hwloc_val = get()
    if hwloc_val == 'bundled':
        ucp_val = get_uniq_cfg_path()
        return third_party_utils.get_bundled_compile_args('hwloc', ucp=ucp_val)
    elif hwloc_val == 'system':
        # try pkg-config
        args = third_party_utils.pkgconfig_get_system_compile_args('hwloc')
        if args != (None, None):
            return args
        # try homebrew
        hwloc_prefix = chpl_platform.get_homebrew_prefix('hwloc')
        if hwloc_prefix:
            return ([], ['-I{0}'.format(os.path.join(hwloc_prefix, 'include'))])

        error("Could not find a suitable hwloc installation.  Please install hwloc or set CHPL_HWLOC=bundled or CHPL_HWLOC=none.")

    return ([ ], [ ])


# returns 2-tuple of lists
#  (linker_bundled_args, linker_system_args)
@memoize
def get_link_args():
    hwloc_val = get()
    if hwloc_val == 'bundled':
        return third_party_utils.pkgconfig_get_bundled_link_args(
                                          'hwloc', ucp=get_uniq_cfg_path())
    elif hwloc_val == 'system':
        if third_party_utils.has_pkgconfig():
            # Check that hwloc version is OK
            exists, retcode, my_out, my_err = try_run_command(
                                ['pkg-config', '--atleast-version=2.1', 'hwloc'])
            if exists and retcode != 0:
                error("CHPL_HWLOC=system requires hwloc >= 2.1", ValueError)

            return third_party_utils.pkgconfig_get_system_link_args('hwloc')
        # try homebrew
        hwloc_prefix = chpl_platform.get_homebrew_prefix('hwloc')
        if hwloc_prefix:
            # TODO: this should also check the version
            return ([], ['-L{0}'.format(os.path.join(hwloc_prefix, 'lib')),
                         '-lhwloc'])

        error("Could not find a suitable hwloc installation. Please install hwloc or set CHPL_HWLOC=bundled or CHPL_HWLOC=none.")

    return ([ ], [ ])

@memoize
def get_prefix():
    hwloc_val = get()
    if hwloc_val == 'bundled':
        ucp_val = get_uniq_cfg_path()
        return third_party_utils.get_bundled_install_path('hwloc', ucp=ucp_val)
    elif hwloc_val == 'system':
        # try pkg-config
        if third_party_utils.has_pkgconfig():
            prefix = run_command(['pkg-config', '--variable', 'prefix', 'hwloc'])
            if prefix:
                return prefix.strip()
        # try homebrew
        hwloc_prefix = chpl_platform.get_homebrew_prefix('hwloc')
        if hwloc_prefix:
            return hwloc_prefix.strip()

        error("Could not find a suitable hwloc installation.  Please install hwloc or set CHPL_HWLOC=bundled or CHPL_HWLOC=none.")

    return ''

def _main():
    hwloc_val = get()

    parser = optparse.OptionParser(usage='usage: %prog [--prefix] [--compile] [--link]')
    parser.add_option('--prefix', dest='action',
                      action='store_const',
                      const='prefix', default='')
    parser.add_option('--compile', dest='action',
                      action='store_const',
                      const='compile', default='')
    parser.add_option('--link', dest='action',
                      action='store_const',
                      const='link', default='')

    (options, args) = parser.parse_args()

    if options.action == 'prefix':
        sys.stdout.write("{0}\n".format(get_prefix()))
    elif options.action == 'compile':
        sys.stdout.write("{0}\n".format(get_compile_args()))
    elif options.action == 'link':
        sys.stdout.write("{0}\n".format(get_link_args()))
    else:
        sys.stdout.write("{0}\n".format(hwloc_val))

if __name__ == '__main__':
    _main()
