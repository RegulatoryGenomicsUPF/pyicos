"""
Pyicos is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

from lib import argparse
import ConfigParser
from turbomix import Turbomix, OperationFailed
from core import (BED, ELAND, PK, SPK, ELAND_EXPORT, WIG, CLUSTER_FORMATS, READ_FORMATS, WRITE_FORMATS)
__version__ = '0.9.8'
from defaults import *

class PicosParser:
    def config_section_map(self, section, config_file):
        dict1 = {}
        options = config_file.options(section)
        for option in options:
            try:
                dict1[option] = config_file.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1


    def validate(self, args):
        if args.binsize < 0 or args.binsize > 1:
            print "\nBinsize is a ratio, it should be between 0 and 1"
            sys.exit(1)

        if args.poisson_test not in POISSON_OPTIONS:
            print "\n%s is not a valid pyicos poisson test. Please use one of the following: %s"%(args.poisson_test, POISSON_OPTIONS)
            sys.exit(1)

    def new_subparser(self, *args):
        return argparse.ArgumentParser(add_help=False)

    def create_parser(self):
        read_formats = str(READ_FORMATS)
        write_formats = str(WRITE_FORMATS)
        parser = argparse.ArgumentParser(version=__version__)
        subparsers = parser.add_subparsers(help='The operation you want to perform. Note that some operations imply previous automatic operations.')

        #parent parsers
        experiment = self.new_subparser()
        experiment.add_argument('experiment', help='The experiment file or directory')

        experiment_flags = self.new_subparser()
        experiment_flags.add_argument('-o','--open-experiment', action='store_true', dest='open_experiment', default=OPEN_EXPERIMENT, help='Defines if the experiment is half-open or closed notation. [Default %(default)s]')
        experiment_flags.add_argument( '-f','--experiment-format',default=EXPERIMENT_FORMAT,  dest='experiment_format', help="""The format the experiment file is written as.
                                 The options are %s. [Default pk]"""%read_formats)


        experiment_b = self.new_subparser()
        experiment_b.add_argument('experiment_b',  help='The experiment file B')
        #No neccesary anyway
        #experiment_b_flags = self.new_subparser()
        #experiment_b_flags.add_argument('--open-experiment-b', action='store_true', default=OPEN_EXPERIMENT, help='Defines if the experiment is half-open or closed notation. [Default %(default)s]')
        #experiment_b_flags.add_argument( '--experiment-b-format',default=EXPERIMENT_FORMAT,  dest='control_format', help="""The format the experiment file is written as.
        #                         The options are %s. [Default pk]"""%read_formats)

        replica_a = self.new_subparser()
        replica_a.add_argument('--replica-a', help='Experiment A replica file')
        
        replica_b = self.new_subparser()
        replica_b.add_argument('--replica-b', help='Experiment B replica file')

        control = self.new_subparser()
        control.add_argument('control', help='The control file or directory')
        control_format = self.new_subparser()
        control_format.add_argument('--control-format', default=CONTROL_FORMAT, help='The format the control file is written as. [default %(default)s]')

        optional_control = self.new_subparser()
        optional_control.add_argument('--control', help='The control file or directory')
        open_control = self.new_subparser()
        open_control.add_argument('--open-control', action='store_true', default=OPEN_CONTROL, help='Define if the region file is half-open or closed notation. [Default %(default)s]')


        basic_parser = self.new_subparser()
        basic_parser.add_argument('--debug', action='store_true', default=DEBUG)
        basic_parser.add_argument('--no-sort',action='store_true', default=NO_SORT,
                                  help='Force skip the sorting step. WARNING: Use only if you know what you are doing. Processing unsorted files assuming they are will outcome in erroneous results')
        basic_parser.add_argument('--silent' ,action='store_false', default=VERBOSE, dest='verbose', help='Run without printing in screen')
        basic_parser.add_argument('--disable-cache' ,action='store_false', default=CACHED, dest='cached', help='Disable internal reading cache. When Clustering low coverage files, it will increase speed and improve memory usage. With very read dense files, the speed will decrease.')
        basic_parser.add_argument('--keep-temp', action='store_true', default=KEEP_TEMP, help='keep the temporary files (for debugging purposes)')
        basic_parser.add_argument('--postscript', action='store_true', default=POSTSCRIPT, help='get the output graphs in postscript format instead of .png')
        basic_parser.add_argument('--showplots', action='store_true', default=SHOWPLOTS, help='Show the plots as they are being calculated by matplotlib. Note that the execution will be stopped until you close the window pop up that will arise')
        basic_parser.add_argument('--label1', default=LABEL1, help="Manually define the second label of the graphs.")
        basic_parser.add_argument('--label2', default=LABEL2, help="Manually define the second label of the graphs.")

        output = self.new_subparser()
        output.add_argument('output', help='The output file or directory')

        output_flags = self.new_subparser()
        output_flags.add_argument('-O','--open-output', action='store_true', default=OPEN_OUTPUT, help='Define if the output is half-open or closed notation. [Default %(default)s]')
        output_flags.add_argument('-F','--output-format',default=OUTPUT_FORMAT, help='Format desired for the output. You can choose between %s. WARNING, for some operations, some outputs are not valid. See operation help for more info. [default pk]'%write_formats)


        blacklist_help = 'Reads a bed file with coordinates that you want to exclude from the analysis. Useful for discarding "noisy" probable artifactual regions like centromeres and repeat regions. [Default %s]'
        blacklist = self.new_subparser()
        blacklist.add_argument('blacklist', default=BLACKLIST, help=blacklist_help)
        optional_blacklist = self.new_subparser()
        optional_blacklist.add_argument('--blacklist', default=BLACKLIST, help=blacklist_help)


        region = self.new_subparser()
        region.add_argument('region', help='The region file')


        optional_region = self.new_subparser()
        optional_region.add_argument('--region', help='The region file or directory. In the enrichment analysis, if its not specified it will be calculated automatically from the tags in both files and the distance of clustering specified in the --proximity flag')
        region_format = self.new_subparser()
        region_format.add_argument('--region-format',default=REGION_FORMAT, help='The format the region file is written as. [default %(default)s]')
        region_format.add_argument('--open-region', action='store_true', default=OPEN_REGION, help='Define if the region file is half-open or closed notation. [Default %(default)s]')

        enrichment_flags = self.new_subparser()
        enrichment_flags.add_argument('--stranded', action='store_true', default=STRANDED_ANALYSIS, help="Decide if the strand is taken into consideration for the analysis. This requires a region file in bed format with the strand information in its 6th column.")
        enrichment_flags.add_argument('--proximity', default=PROXIMITY, type=int, help="Determines if two regions calculated automatically are close enough to be clustered. Default %(default)s nt")
        enrichment_flags.add_argument('--no-pseudocount', action='store_true', default=NOPSEUDOCOUNT, help="The usage of pseudocounts in the enrichment calculation allows the inclusion of regions that have n reads in one dataset and 0 reads in the other.  [Default %(default)s]")
        enrichment_flags.add_argument('--simple-counts', action='store_true', default=SIMPLECOUNTS, help="To calculate densities, RPKM values are used by default. This flag changes the calculation to simple read counts. [Default %(default)s]")
        enrichment_flags.add_argument('--binsize', type=float, default=BINSIZE, help="The size of the bins to calculate the local sd and mean for the background model. [Default %(default)s]")        
        enrichment_flags.add_argument('--sdfold', type=float, default=SDFOLD, help="The standard deviation fold used to generate the background model. [Default %(default)s]")  
        enrichment_flags.add_argument('--recalculate', type=bool, default=RECALCULATE, help="Recalculate the z-score when plotting. Useful for doing different plots with 'pyicos plot' [Default %(default)s]")         
        
        zscore = self.new_subparser()  
        zscore.add_argument('--zscore', type=float, default=ZSCORE, help="Significant Z-score value. [Default %(default)s]")        

        label = self.new_subparser()
        label.add_argument('--label', default=LABEL, help='The label that will identify the experiment')

        span = self.new_subparser()
        span.add_argument('--span', default=SPAN, help='The span of the variable and fixed wig formats', type=int)

        round = self.new_subparser()
        round.add_argument('--round',action='store_true',dest='rounding', default=ROUNDING, help='Round the final results to an integer')
        pvalue = self.new_subparser()
        pvalue.add_argument('--p-value',type=float, default=P_VALUE, help='The threshold p-value that will make a cluster significant. [Default %(default)s]')

        tolerated_duplicates =self.new_subparser()
        tolerated_duplicates.add_argument('--duplicates',type=int, default=DUPLICATES, help='The number of duplicated reads accept will be counted. Any duplicated read after this threshold will be discarded. [Default %(default)s]')

        height = self.new_subparser()
        height.add_argument('--k-limit',type=int, default=HEIGHT_LIMIT, help='The k limit Pyicos will analize to when performing a poisson test. Every cluster that goes over the threshold will have a p-value of 0, therefore considered significant. For performance purposes, raising it will give more precision when defining low p-values, but will take longer to execute. [Default %(default)s]')

        correction = self.new_subparser()
        correction.add_argument('--correction',type=float, default=CORRECTION, help='This value will correct the size of the genome you are analyzing. This way you can take into consideration the real mappable genome [Default %(default)s]')

        tag_length = self.new_subparser()
        tag_length.add_argument( '--tag-length',default=TAG_LENGTH, type=int, help='The tag length, or the extended one. Needed when converting from a Clustered format (wig, pk) to a non clustered format (bed, eland) [Default %(default)s]')

        frag_size = self.new_subparser()
        frag_size.add_argument('frag_size', help='The estimated inmmunoprecipitated fragment size. This is used by the extend operation to extend the tags, taking into consideration their strand, if provided. If the strand is not provided, Pyicos will assume positive strand.', type=int)
        optional_frag_size = self.new_subparser()
        optional_frag_size.add_argument('-x', '--frag-size', help='The estimated inmmunoprecipitated fragment size. This is used by Pyicos to reconstruct the original signal in the original wet lab experiment.', type=int)

        no_subtract = self.new_subparser()
        no_subtract.add_argument('--no-subtract',action='store_true', default=False, help='Dont subtract the control to the output, only normalize.')

        normalize = self.new_subparser()
        normalize.add_argument('--normalize',action='store_true', default=False, help='Normalize to the control before subtracting')

        extend = self.new_subparser()
        extend.add_argument('--extend',action='store_true', default=False, help='Extend')
        subtract = self.new_subparser()
        subtract.add_argument('--subtract',action='store_true', default=False, help='subtract')
        filterop = self.new_subparser()
        filterop.add_argument('--filter',action='store_true', default=False, help='filterop')
        poisson = self.new_subparser()
        poisson.add_argument('--poisson',action='store_true', default=False, help='poisson')
        modfdr = self.new_subparser()
        modfdr.add_argument('--modfdr',action='store_true', default=False, help='modfdr')
        remduplicates = self.new_subparser()
        remduplicates.add_argument('--remduplicates',action='store_true', default=False, help='remduplicates')
        split = self.new_subparser()
        split.add_argument('--split',action='store_true', default=False, help='split')
        trim = self.new_subparser()
        trim.add_argument('--trim',action='store_true', default=False, help='trim')
        strcorr = self.new_subparser()
        strcorr.add_argument('--strcorr',action='store_true', default=False, help='strcorr')
        remregions = self.new_subparser()
        remregions.add_argument('--remregions',action='store_true', default=False, help='remregions')
        remartifacts = self.new_subparser()
        remartifacts.add_argument('--remartifacts',action='store_true', default=False, help='remartifacts')

        split_proportion = self.new_subparser()
        split_proportion.add_argument('--split-proportion', default=SPLIT_PROPORTION, help='Fraction of the cluster height below which the cluster is splitted. [Default %(default)s]', type=float)

        trim_proportion = self.new_subparser()
        trim_proportion.add_argument('--trim-proportion', default=TRIM_PROPORTION, help='Fraction of the cluster height below which the peak is trimmed. Example: For a cluster of height 40, if the flag is 0.05, 40*0.05=2. Every cluster will be trimmed to that height. A position of height 1 is always considered insignificant, no matter what the cluster height is. [Default %(default)s]', type=float)
        trim_absolute = self.new_subparser()
        trim_absolute.add_argument('--trim-absolute', default=TRIM_ABSOLUTE, help='The height threshold to trim the clusters. Overrides the trim proportion. [Default %(default)s]', type=int)

        split_absolute = self.new_subparser()
        split_absolute.add_argument('--split-absolute', default=SPLIT_ABSOLUTE, help='The height threshold to split the clusters. [Default %(default)s]', type=int)

        repeats = self.new_subparser()
        repeats.add_argument('--repeats', help='Number of random repeats when generating the "background" for the modfdr operation[Default %(default)s]', default=REPEATS, type=int)
        masker_file = self.new_subparser()
        masker_file.add_argument('--masker', help='You can provide a masker file that will be used by the modfdr operation background generation so that randomized reads will not fall in this areas')

        poisson_test = self.new_subparser()
        poisson_test.add_argument('--poisson-test', help="Decide what property of the cluster will be used for the poisson analysis. Choices are %s [Default %s]"%(POISSON_OPTIONS, POISSONTEST), default=POISSONTEST)
        
        remlabels = self.new_subparser()
        remlabels.add_argument('--remlabels', help='Discard the reads that have this particular label. Example: --discard chr1 will discard all reads with chr1 as tag. You can specify multiple tags to discard using the following notation --discard chr1 chr2 tagN')

        threshold = self.new_subparser()
        threshold.add_argument('--threshold', help='The height threshold used to cut', type=int)

        species = self.new_subparser()
        species.add_argument('-p', '--species', default=SPECIES,
                             help='The species that you are analyzing. This will read the length of the chromosomes of this species from the files inside the folder "chrdesc". If the species information is not known, the filtering step will assume that the chromosomes are as long as the position of the furthest read.')


        plot_path = self.new_subparser()
        plot_path.add_argument('plot_path', default=PLOT_PATH, help='The path of the file to plot.')

        correlation_flags = self.new_subparser()
        correlation_flags.add_argument('--max-delta',type=int, default=MAX_DELTA, help='Maximum delta [Default %(default)s]')
        correlation_flags.add_argument('--min-delta',type=int, default=MIN_DELTA, help='Minimum delta [Default %(default)s]')
        correlation_flags.add_argument('--height-filter',type=int, default=HEIGHT_FILTER, help='Height to filter the peaks [Default %(default)s]')
        correlation_flags.add_argument('--delta-step',type=int, default=DELTA_STEP, help='The step of the delta values to test [Default %(default)s]')
        correlation_flags.add_argument('--max-correlations',type=int, default=MAX_CORRELATIONS, help='The maximum of clusters that will be enough to calculate the strand correlation shift. Lower this parameter to increase time performance [Default %(default)s]')    


        protocol_name = self.new_subparser()
        protocol_name.add_argument('protocol_name', help='The protocol configuration file.')
        #callpeaks operation
        subparsers.add_parser('callpeaks', help='The complete peak calling sequence proposed in the future publication. The region file is optional. The same goes for the control file, if not provided, there will not be a normalization or a subtraction.',
                              parents=[experiment, experiment_flags, basic_parser, optional_control, control_format, open_control, optional_blacklist, output, output_flags, optional_frag_size, round, label, span, no_subtract, remlabels, pvalue, height, correction, trim_proportion, species, tolerated_duplicates, poisson_test])
        #convert operation
        subparsers.add_parser('convert', help='Convert a file to another file type.',
                              parents=[experiment, experiment_flags, basic_parser, output, output_flags, round, label, tag_length, span, optional_frag_size, remlabels])

        subparsers.add_parser('subtract', help='Subtract two clustered files. Operating with directories will only give apropiate results if the files and the control are paired in alphabetical order.', parents=[experiment,experiment_flags, basic_parser, control, control_format, open_control, output, output_flags, round, normalize, tag_length, span, label, remlabels])
        #split operation
        subparsers.add_parser('split', help='Split the peaks in subpeaks. Only accepts pk or wig as output (other formats under development).', parents=[experiment, experiment_flags, basic_parser, output, output_flags, round, split_proportion, split_absolute, label, remlabels])
        #trim operation
        subparsers.add_parser('trim', help='Trim the clusters to a given threshold.', parents=[experiment, experiment_flags, basic_parser, output, output_flags, round, trim_absolute, trim_proportion, label, remlabels])
        #discard operation
        subparsers.add_parser('discard', help='Discards artifacts from a file. Only accepts pk or wig as output.', parents=[experiment, experiment_flags, basic_parser, output, output_flags, round, span, label, remlabels])
        #remove duplicates operation
        subparsers.add_parser('remduplicates', help='Removes the duplicated reads in a file. Only accepts tag-like files (bed, eland, sam)', parents=[experiment, experiment_flags, basic_parser, output, output_flags, tolerated_duplicates, round, span, label, remlabels])
        #normalize operation
        subparsers.add_parser('normalize', help='Normalize a pk file respect of the control.', parents=[experiment, experiment_flags, basic_parser, control, control_format, output, output_flags, open_control, round, label, span, remlabels])
        #extend operation
        subparsers.add_parser('extend', help='Extends the reads of a file to the desired length. This operation requires tag-like files (bed, eland, sam)', parents=[experiment,experiment_flags,  basic_parser,  output, output_flags, frag_size, round, label, span, remlabels])
        #poisson analysis
        subparsers.add_parser('poisson', help='Analyze the significance of accumulated reads in the file using the poisson distribution. With this tests you will be able to decide what is the significant threshold for your reads.',
                              parents=[experiment,experiment_flags,  basic_parser, output_flags, optional_frag_size, pvalue, height, correction, species, remlabels, poisson_test])
        #cut operations
        subparsers.add_parser('filter', help="""Analyze the significance of accumulated reads in the file using the poisson distribution and generate the resulting profiles, in wig or pk formats""",
                              parents=[experiment,experiment_flags,  basic_parser, output, optional_frag_size, output_flags, round, pvalue, height, correction, threshold, species, remlabels, poisson_test])
        #modfdr analysis
        subparsers.add_parser('modfdr', help="""Use the modified FDR method to determine what clusters are significant in an specific region. Output in a clustered format only.""",
                              parents=[experiment, experiment_flags, basic_parser, region, output, output_flags, round, pvalue, repeats, masker_file, remlabels])
        #remove operation
        subparsers.add_parser('remregions', help='Removes regions that overlap with another the coordinates in the "black list" file.',
                              parents=[experiment, experiment_flags, basic_parser, output_flags, blacklist, region_format, output, remlabels])
        #strcorr operation
        subparsers.add_parser('strcorr', help='A cross-correlation test between forward and reverse strand clusters in order to find the optimal extension length.',
                              parents=[experiment, experiment_flags, basic_parser, output, output_flags, correlation_flags, remlabels])
        #enrichment operation
        subparsers.add_parser('enrichment', help='(UNDER DEVELOPMENT) An enrichment test based on the MA plots', parents=[experiment, experiment_b, experiment_flags, basic_parser, output_flags, replica_a, replica_b, optional_region, region_format, output, enrichment_flags, zscore])
        #protocol reading
        subparsers.add_parser('protocol', help='Import a protocol file to load in Pyicos', parents=[protocol_name])

        subparsers.add_parser('plot', help="(UNDER DEVELOPMENT) Plot a file with pyicos plotting utilities. Requires matplotlib installed.", parents=[basic_parser, plot_path, output, zscore])

        #whole exposure
        subparsers.add_parser('all', help='Exposes all pyicos functionality through a single command', parents=[experiment, experiment_flags, basic_parser, optional_control, control_format, open_control, optional_region, output, output_flags, optional_frag_size, round, label, span, no_subtract, remlabels, pvalue, height, correction, trim_proportion, trim_absolute, species, tolerated_duplicates, masker_file, correlation_flags, split_proportion, split_absolute, normalize, extend, subtract, filterop, poisson, modfdr, remduplicates, split, trim, strcorr, remregions, remartifacts])

        return parser

    def run_parser(self):
        parser = self.create_parser()
        parser.set_defaults(experiment=EXPERIMENT, experiment_format=EXPERIMENT_FORMAT, open_experiment=OPEN_EXPERIMENT, debug=DEBUG, discard=DISCARD, output=OUTPUT, control=CONTROL, 
                            label = LABEL, output_format=OUTPUT_FORMAT,open_output=OPEN_OUTPUT, rounding=ROUNDING, control_format=CONTROL_FORMAT, region=REGION, region_format=REGION_FORMAT, 
                            open_region =OPEN_REGION,frag_size = FRAG_SIZE, tag_length = TAG_LENGTH, span=SPAN, p_value=P_VALUE, height_limit=HEIGHT_LIMIT, 
                            correction=CORRECTION, no_subtract = NO_SUBTRACT, normalize = DO_NORMALIZE, trim_proportion=TRIM_PROPORTION,open_control=OPEN_CONTROL, 
                            no_sort=NO_SORT, duplicates=DUPLICATES, threshold=THRESHOLD, trim_absolute=TRIM_ABSOLUTE, max_delta=MAX_DELTA, min_delta=MIN_DELTA, 
                            height_filter=HEIGHT_FILTER, delta_step=DELTA_STEP, verbose=VERBOSE, species=SPECIES, cached=CACHED, split_proportion=SPLIT_PROPORTION,
                            split_absolute=SPLIT_ABSOLUTE, repeats=REPEATS, masker_file=MASKER_FILE, max_correlations=MAX_CORRELATIONS, keep_temp=KEEP_TEMP, postscript = POSTSCRIPT,
                            remlabels=REMLABELS, experiment_b=EXPERIMENT, replica_a=EXPERIMENT, replica_b=EXPERIMENT, poisson_test=POISSONTEST, stranded=STRANDED_ANALYSIS,
                            proximity=PROXIMITY, showplots=SHOWPLOTS, plot_path=PLOT_PATH, no_pseudocount=NOPSEUDOCOUNT, simple_counts=SIMPLECOUNTS, label1=LABEL1, 
                            label2=LABEL2, binsize=BINSIZE, zscore=ZSCORE, blacklist=BLACKLIST, sdfold=SDFOLD, recalculate=RECALCULATE)

        args = parser.parse_args()

        self.validate(args)

        #Add any parameters found in the config file. Override them with anything found in the args later
        if sys.argv[1] == 'protocol':
            config = ConfigParser.ConfigParser()
            config.read(args.protocol_name)
            try:
                section = self.config_section_map("Pyicotrocol", config)
            except ConfigParser.NoSectionError:
                print "\nERROR: %s is not a Pyicos Protocol file, is missing the [Pyicotrocol] header or it doesn't exists\n"%args.protocol_name
                sys.exit(0)

            for key, value in section.items(): #this works fine for all string values
                try:
                    t = type(parser._defaults[key])
                    if t == int:
                        args.__dict__[key] = config.getint("Pyicotrocol", key)
                    elif t == float:
                        args.__dict__[key] = config.getfloat("Pyicotrocol", key)
                    elif t == bool:
                        args.__dict__[key] = config.getboolean("Pyicotrocol", key)
                    elif t == str:
                        args.__dict__[key] = config.get("Pyicotrocol", key)

                except KeyError:
                    if key == 'input':
                        args.__dict__['experiment'] = config.get("Pyicotrocol", 'input')
                        print
                        print "WARNING: The keyword 'input' for the protocol files is deprecated, please use 'experiment' instead"

                    elif key != 'operations':
                        print 'ERROR: There is an error in your protocol file.  "%s" is not a Pyicos parameter'%key
                        sys.exit(0)


        if not args.control_format: #If not specified, the control format is equal to the experiment format
            args.control_format = args.experiment_format
            args.open_control = args.open_experiment

        turbomix = Turbomix(args.experiment, args.output, args.experiment_format, args.output_format, args.label, args.open_experiment, args.open_output, args.debug,
                            args.rounding, args.tag_length, args.remlabels, args.control, args.control_format, args.open_control, args.region,
                            args.region_format, args.open_region, args.span, args.frag_size, args.p_value, args.height_limit, args.correction,
                            args.trim_proportion, args.no_sort, args.duplicates, args.threshold, args.trim_absolute, args.max_delta,
                            args.min_delta, args.height_filter, args.delta_step, args.verbose, args.species, args.cached, args.split_proportion, args.split_absolute, 
                            args.repeats, args.masker_file, args.max_correlations, args.keep_temp, args.experiment_b, args.replica_a, args.replica_b, args.poisson_test, 
                            args.stranded, args.proximity, args.postscript, args.showplots, args.plot_path, args.no_pseudocount, args.simple_counts, args.label1, 
                            args.label2, args.binsize, args.zscore, args.blacklist, args.sdfold, args.recalculate)

        if sys.argv[1] == 'protocol':
            operations = section['operations'].split(',')
            for operation in operations:
                print "Adding operation %s to protocol..."%operation
                turbomix.operations.append(operation.strip())
                
        elif sys.argv[1] == 'convert':
            if args.frag_size:
                turbomix.operations = [EXTEND]

        elif sys.argv[1] == 'subtract':
            turbomix.operations = [SUBTRACT]
            if args.normalize:
                turbomix.operations.append(NORMALIZE)

        elif sys.argv[1] == 'normalize':
            turbomix.operations = [NORMALIZE]

        elif sys.argv[1] == 'extend':
            turbomix.operations = [EXTEND]

        elif sys.argv[1] == 'strcorr':
            turbomix.operations = [STRAND_CORRELATION, NOWRITE]

        elif sys.argv[1] == 'poisson':
            turbomix.operations = [POISSON, NOWRITE]

        elif sys.argv[1] == 'filter':
            turbomix.operations = [POISSON, FILTER]

        elif sys.argv[1] == 'remove':
            turbomix.operations = [REMOVE_REGION]

        elif sys.argv[1] == 'enrichment':
            turbomix.operations = [ENRICHMENT, PLOT]

        elif sys.argv[1] == 'split':
            turbomix.operations = [SPLIT]

        elif sys.argv[1] == 'trim':
            turbomix.operations = [TRIM]

        elif sys.argv[1] == 'discard':
            turbomix.operations = [DISCARD_ARTIFACTS]

        elif sys.argv[1] == 'remduplicates':
            turbomix.operations = [REMOVE_DUPLICATES]

        elif sys.argv[1] == 'remregions':
            turbomix.operations = [REMOVE_REGION]      

        elif sys.argv[1] == 'modfdr':
            turbomix.operations = [ModFDR]

        elif sys.argv[1] == 'callpeaks':
            turbomix.operations = [SPLIT, EXTEND, POISSON, FILTER, REMOVE_DUPLICATES] 
            if args.duplicates > 1: #If there is only 1 duplicate, there is no need to discard artifacts
                turbomix.operations.append(DISCARD_ARTIFACTS)
            if args.blacklist:
                turbomix.operations.append(REMOVE_REGION)
            if args.control:
                turbomix.operations.append(NORMALIZE)
                if not args.no_subtract:
                    turbomix.operations.append(SUBTRACT)

        elif sys.argv[1] == 'plot':
            turbomix.operations = [PLOT, NOWRITE]      
        
        elif sys.argv[1] == 'all':
            if args.normalize: turbomix.operations.append(NORMALIZE)
            if args.extend: turbomix.operations.append(EXTEND)
            if args.subtract: turbomix.operations.append(SUBTRACT)
            if args.filter: turbomix.operations.append(FILTER)
            if args.poisson: turbomix.operations.append(POISSON)
            if args.modfdr: turbomix.operations.append(ModFDR)
            if args.remduplicates: turbomix.operations.append(REMOVE_DUPLICATES)
            if args.split: turbomix.operations.append(SPLIT)
            if args.trim: turbomix.operations.append(TRIM)
            if args.strcorr: turbomix.operations.append(STRAND_CORRELATION)
            if args.remregions: turbomix.operations.append(REMOVE_REGION)
            if args.remartifacts: turbomix.operations.append(DISCARD_ARTIFACTS)

        #parameters are set, now try running
        try:
            turbomix.run()

        except KeyboardInterrupt:
            print 'Canceled by user.'

        except OperationFailed:
            if args.debug:
               raise
            else:
                print 'Operation Failed.'
        """except IOError as error:
            if args.debug:
                raise
            else:            
                print error""" #Not compatible with python 2.5
        




