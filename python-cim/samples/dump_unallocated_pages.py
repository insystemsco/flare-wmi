#!/usr/bin/env python2
'''
extract unallocated physical pages from a CIM repository.

author: Willi Ballenthin
email: william.ballenthin@fireeye.com
'''
import os
import sys
import logging

import argparse

import cim


logger = logging.getLogger(__name__)


def extract_unallocated_data_pages(repo):
    for i in range(repo.logical_data_store.page_count):
        try:
            _ = repo.data_mapping.get_logical_page_number(i)
        except cim.UnmappedPage:
            yield repo.logical_data_store.get_physical_page_buffer(i)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Extracted unallocated physical pages from a CIM repo.")
    parser.add_argument("input", type=str,
                        help="Path to input file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Disable all output but errors")
    args = parser.parse_args(args=argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger().setLevel(logging.INFO)

    try:
        repo = cim.CIM(cim.CIM_TYPE_WIN7, args.input)
    except Exception as e:
        # TODO: detect winxp version and use that
        logger.error('bad cim')
        return -1

    for page in extract_unallocated_data_pages(repo):
        os.write(sys.stdout.fileno(), page)

    return 0


if __name__ == "__main__":
    sys.exit(main())