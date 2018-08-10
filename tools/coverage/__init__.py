import copy
import fnmatch

from ..resources import Resources, FileType, FileRef
from ..notifier.mock import MockNotifier


def create_coverage_build_profile(build_profile):
    common = [u"-DENABLE_LIBGCOV_PORT=1", u"--coverage"]
    linker_remove = [u'-Wl,--wrap,exit', u'-Wl,--wrap,atexit']
    linker_add = [u"--coverage"]

    coverage_profile = copy.deepcopy(build_profile)
    coverage_profile[0][u'GCC_ARM']['common'].extend(common)
    coverage_profile[0][u'GCC_ARM']['ld'].extend(linker_add)
    for flag in linker_remove:
        if flag in coverage_profile[0][u'GCC_ARM']['ld']:
            coverage_profile[0][u'GCC_ARM']['ld'].remove(flag)

    return coverage_profile


def split_coverage_resources(res, patterns):
    c_srcs = set()
    cpp_srcs = set()

    for c_src in res._file_refs[FileType.C_SRC]:
        for pattern in patterns:
            if fnmatch.fnmatch(c_src.name, pattern) or fnmatch.fnmatch(c_src.path, pattern):
                c_srcs.add(c_src)
                break

    for cpp_src in res._file_refs[FileType.CPP_SRC]:
        for pattern in patterns:
            if fnmatch.fnmatch(cpp_src.name, pattern) or fnmatch.fnmatch(cpp_src.path, pattern):
                cpp_srcs.add(cpp_src)
                break

    res._file_refs[FileType.C_SRC] -= c_srcs
    res._file_refs[FileType.CPP_SRC] -= cpp_srcs

    return c_srcs, cpp_srcs


def compile_coverage_sources(res, toolchain, coverage_resources):
    res._file_refs[FileType.C_SRC] = coverage_resources[0]
    res._file_refs[FileType.CPP_SRC] = coverage_resources[1]

    return toolchain.compile_sources(res, res.get_file_paths(FileType.INC_DIR))
