#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A helper class designed to handle the managment of options and
positional arguments to qsub and related Grid Engine executables.

Contains functions to write the requested execution string either
to the command line or to a script file.
"""

import argparse
from itertools import chain, combinations

def all_string_combinations(ss):
  lists = chain(*map(lambda x: combinations(ss, x), range(1, len(ss)+1)))
  return [''.join(x) for x in lists]

class qsubOptions():
    "A data type meant to collect qsub options. See man qsub for information"

    def __init__(self, optstring = '', prog = 'qsub'):
        #Which SGE command are we going to work with?
        self.prog = prog
        sge_program_names = ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter', 'qresub', 'qmake']
        assert self.prog in sge_program_names, 'Unsupported SGE command: '+prog+'not one of '+', '.join(sge_program_names)

        #SUPPRESS = If not specified, do not generate variable in namespace
        self.parser = argparse.ArgumentParser(
           description = 'Options to pass to qsub', 
           formatter_class=argparse.RawTextHelpFormatter, 
           argument_default=argparse.SUPPRESS, 
           epilog = """The following is scraped from the qsub manpage for GE 6.2u5 dated 2009/12/01 12:24:06"""
           )

        #BEGIN SGE OPTION PARSER
        #BUG if help still begins with a line with -option, have cosmetic bug where metavar cannot be specified correctly
        yesno = ['y', 'yes', 'n', 'no']
        
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin']:
            self.parser.add_argument('-@', metavar = 'optionfile')
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-a', metavar = 'date_time')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-ac', metavar = 'variable[=value]', action = 'append')
        if prog in ['qsub', 'qalter', 'qrsh', 'qsh', 'qlogin']:
            self.parser.add_argument('-ar', metavar = 'ar_id')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-A', metavar = 'account_string')
        self.parser.add_argument('-binding', nargs='+', metavar=('binding_instance', 'binding_strategy'))
        if prog in ['qsub', 'qrsh']:
            self.parser.add_argument('-b', choices = yesno)
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-c', metavar = 'occasion_specifier')
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-ckpt', metavar = 'ckpt_name')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin']:
            self.parser.add_argument('-clear', action = 'store_true')
        if prog in ['qsub', 'qsh', 'qrsh', 'qalter']:
            self.parser.add_argument('-cwd', action = 'store_true')
        if prog in ['qsub', 'qrsh']:
            self.parser.add_argument('-C', metavar = 'prefix_string')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-dc', action = 'append', metavar = 'variable')
        if prog in ['qsh', 'qrsh']:
            self.parser.add_argument('-display', metavar = 'display_specifier')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-dl', metavar = 'date_time')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-e', metavar = 'path')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-hard', action = 'store_true')
        if prog in ['qsub', 'qrsh', 'qalter', 'qresub']:
            #NOTE in SGE this is -h, here I have renamed it to -hold
            #TODO check if multiple holds are parsed correctly
            self.parser.add_argument('-hold', choices = 'usonUOS')
        if prog in ['qsub', 'qrsh', 'qalter']:
            self.parser.add_argument('-hold_jid', nargs = '+', metavar = 'wc_job_list')
        if prog in ['qsub', 'qrsh', 'qalter']:
            self.parser.add_argument('-hold_jid_ad', nargs = '+', metavar = 'wc_job_list')
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-i', metavar = 'file')
        if prog in ['qrsh', 'qmake']:
            self.parser.add_argument('-inherit', action = 'store_true')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-j', choices = yesno)
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-js', nargs='?', type = int, metavar = 'job_share')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin']:
            self.parser.add_argument('-jsv', metavar = 'jsv_url')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-l', metavar = 'keywords')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            #TODO check if multiple arguments are parsed correctly
            choices = all_string_combinations('beasn')
            self.parser.add_argument('-m', nargs='+', choices = choices)
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-M', metavar = 'user[@host]')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-masterq', nargs='+', metavar='wc_queue_list')
        if prog in ['qsub', 'qrsh', 'qalter']:
            self.parser.add_argument('-notify', action = 'store_true')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin']:
            self.parser.add_argument('-now', choices = yesno)
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-N', metavar = 'name')
        if prog in ['qrsh']:
            self.parser.add_argument('-noshell', action = 'store_true')
        if prog in ['qrsh']:
            self.parser.add_argument('-nostdin', action = 'store_true')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-o', metavar = 'path')
        if prog in ['qalter']:
            self.parser.add_argument('-ot', metavar = 'override_tickets')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-P', metavar = 'project_name')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-p', metavar = 'priority')
        if prog in ['qsub', 'qsh', 'qrsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-pe', nargs = 2, metavar = ('parallel_environment', 'n'))
        if prog in ['qrsh', 'qlogin']:
            self.parser.add_argument('-pty', choices = yesno)
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-q', nargs = '+', metavar = 'wc_queue_list')
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-R', choices = yesno)
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-r', choices = yesno)
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-sc', action='append', metavar = 'variable[=value]')
        if prog in ['qsub']:
            self.parser.add_argument('-shell', choices = yesno)
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-soft', action = 'store_true')
        if prog in ['qsub']:
            self.parser.add_argument('-sync', choices = yesno)
        if prog in ['qsub', 'qsh', 'qalter']:
            self.parser.add_argument('-S', metavar = 'pathname')
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-t', metavar = 'n[-m[:s]]')
        if prog in ['qsub', 'qalter']:
            self.parser.add_argument('-tc', type = int, metavar = 'max_running_tasks')
        if prog in ['qsub']:
            self.parser.add_argument('-terse', action = 'store_true')
        if prog in ['qalter']:
            self.parser.add_argument('-u', metavar = 'username')
        if prog in ['qsub', 'qrsh', 'qalter']:
            self.parser.add_argument('-v', metavar = 'variable[=value]')
        if prog in ['qrsh', 'qmake']:
            self.parser.add_argument('-verbose', action = 'store_true')
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-verify', action = 'store_true')
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            #TODO parse acceptability of qrsh argument properly
            self.parser.add_argument('-V', action = 'store_true')
        if prog in ['qsub', 'qrsh', 'qsh', 'qlogin', 'qalter']:
            self.parser.add_argument('-w', choices = 'ewnpv')
        if prog in ['qsub', 'qrsh', 'qsh', 'qalter']:
            self.parser.add_argument('-wd', metavar = 'working_dir')
        if prog in ['qsub', 'qrsh']:
            self.parser.add_argument('command', nargs='?', default='echo')
        if prog in ['qsub', 'qrsh', 'qalter']:
            self.parser.add_argument('command_args', nargs = '*')
        if prog in ['qsh']:
            self.parser.add_argument('xterm_args', nargs = '*')

        #END SGE OPTION PARSER
        self.parse('echo')
    
    def parse(self, inputstring = ''):
        """Helper method: parses a string"""
        return self.parse_args(inputstring.split())

    def parse_and_add(self, inputstring = '', namespace = None):
        if namespace is None:
            namespace = self.args
        return self.parse_args(inputstring.split(), namespace = namespace)

    def parse_args(self, args = None, namespace = None):
        """Helper method: parses a list"""
        if args == None:
            self.args = self.parser.parse_args(namespace = namespace) #default is sys.argv[1:]
        else:
            self.args = self.parser.parse_args(args, namespace = namespace)
        return self.args



    def write_qsub_script(self, filename, echo = False):
        """
        Writes the entire command line to a qsub script

        filename: name of file to write
        echo    : echo contents of script to stdout. Default: False
        """

        buf= ['#!/usr/bin/env qsub',
              '# Written using pyGRID module']

        for option, value in self.args.__dict__.items():
            if value == True:
                value = ''
            
            if option not in ['command', 'command_args', 'xterm_args', 'code']:
                if isinstance(value, list):
                    val = ' '.join(value)
                else:
                    val = str(value)

                buf.append(' '.join(['#$', '-'+option, val]))

        args = getattr(self.args, 'command_args', [])
        args = getattr(self.args, 'xterm_args', args)

        if hasattr(self.args,'code'):
            buf.append(' ')
            buf.append('# Code inserted by pyGRID')
            buf.append(self.args.code)
            buf.append(' ')

        if hasattr(self.args,'command'):
            buf.append(' '.join([self.args.command] + args))

        if echo: print '\n'.join(buf)
        
        if filename is not None:
            f = open(filename, 'w')
            f.write('\n'.join(buf))
            f.close()



    def execute(self, mode = 'local', path=''):
        """
        Executes qsub

        known modes: local - run locally
                     echo  - echoes out execution string only

        path: path to qsub/... executable: Default = nothing
        """

        #Form execution string

        import os
        program = os.path.join(path, self.prog)
        options = []

        for option, value in self.args.__dict__.items():
            if value == True:
                value = ''

            if isinstance(value, list):
                val = ' '.join(value)
            else:
                val = str(value)

            if option not in ['command', 'command_args', 'xterm_args', 'code']:
                options.append('-'+option +' '+val)

        args = getattr(self.args, 'command_args', [])
        args = getattr(self.args, 'xterm_args', args)

        exestring = ' '.join([program] + options + [self.args.command] + args)

        if mode == 'echo':
            print exestring
        elif mode == 'local':
            import subprocess
            p = subprocess.Popen(exestring, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
            print p.stdout.read()



if __name__ == '__main__':
    print 'Attempting to validate qsub arguments using argparse'
    o = qsubOptions()
    o.parse_args() 
    o.args.t = '1-1000'
    print 'I will now print the script'
    o.write_qsub_script('/dev/null', echo = True)
    print '*'*70
    print 'I will now print the command line'
    o.execute(mode = 'echo')