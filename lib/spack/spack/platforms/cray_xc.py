import os
from spack.architecture import Platform, Target
from spack.operating_systems.linux_distro import LinuxDistro
from spack.operating_systems.cnl import Cnl
from spack.util.executable import which

class CrayXc(Platform):
    priority    = 20
    front_end   = 'sandybridge'
    back_end    = 'ivybridge'
    default     = 'ivybridge'

    back_os     = "CNL10"
    default_os  = "CNL10"

    def __init__(self):
        ''' Since cori doesn't have ivybridge as a front end it's better
            if we use CRAY_CPU_TARGET as the default. This will ensure
            that if we're on a XC-40 or XC-30 then we can detect the target
        '''
        super(CrayXc, self).__init__('cray_xc')

        # Handle the default here so we can check for a key error
        if 'CRAY_CPU_TARGET' in os.environ:
            self.default = os.environ['CRAY_CPU_TARGET']

        # Change the defaults to haswell if we're on an XC40
        if self.default == 'haswell':
            self.front_end = self.default
            self.back_end = self.default

        # Could switch to use modules and fe targets for front end
        # Currently using compilers by path for front end.
        self.add_target('sandybridge', Target('sandybridge'))
        self.add_target('ivybridge',
                        Target('ivybridge', 'craype-ivybridge'))
        self.add_target('haswell',
                        Target('haswell','craype-haswell'))

        # Front end of the cray platform is a linux distro.
        linux_dist = LinuxDistro()
        self.front_os = str(linux_dist)
        self.add_operating_system(str(linux_dist), linux_dist)
        self.add_operating_system('CNL10', Cnl())

    @classmethod
    def detect(self):
        if os.path.exists('/cray_home'):
            cc_verbose = which('cc')
            cc_verbose.add_default_arg('-craype-verbose')
            text = cc_verbose(output=str, error=str, ignore_errors=True).split()
            if '-D__CRAYXC' in text:
                return True
        return False
