"""
Parser Common: The common flags and functions shared between Pyicoteo parsers
"""

"""
Pyicoteo is free software: you can redistribute it and/or modify
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
import os

if sys.version_info < (2, 6):
    print "Pyicoteo requires python 2.6 or greater (no Python 3 support yet)"
    sys.exit(1)

import argparse
import ConfigParser
from ..turbomix import Turbomix, OperationFailed
from ..defaults import *

__version__ = VERSION

def run_turbomix(turbomix, debug=False):
    try:
        turbomix.run()
    except KeyboardInterrupt:
        print 'Canceled by user.'
    except OperationFailed:
        if debug:
           raise
        else:
            print 'Operation Failed.'


def _big_warning(message):
    print "\n**************************************WARNING*********************************WARNING**************************************************************"
    print message
    print "**************************************WARNING*********************************WARNING**************************************************************\n"

def _error_exit(message):
    print ("\nERROR: %s")%message
    sys.exit(1)     

def _file_exists(path):
    if path:
        if not os.path.exists(path):
            print
            print "Pyicoteo couldn't find the following file or directory: %s"%path
            print
            sys.exit(1)       


def validate_operations(args, turbomix):
    if MODFDR in turbomix.operations:
        _big_warning('You are using the ModFDR without a stranded format as output. This means that the strand information will be ignored. If you want to include the strand information, please consider using the --stranded flag')

    if ENRICHMENT in turbomix.operations and args.experiment_format == BAM and args.sequential == True:
        _big_warning('Please make sure that the region files is ordered in the same way your BAM files are ordered, or else results will be incorrect!')


def _isratio(argument, name):
    if argument < 0 or argument > 1:
        _error_exit("%s is a ratio, it should be between 0 and 1"%name)        


def validate(args):
    _isratio(args.binsize, "--binsize")
    _isratio(args.binstep, "--binstep")
    if args.poisson_test not in POISSON_OPTIONS:
        _error_exit("%s is not a valid Pyicoteo poisson test. Please use one of the following: %s"%(args.poisson_test, POISSON_OPTIONS))

    if args.output_format == WIG and args.open_output == False:
        _big_warning('You chose as output format a WIG closed file. This will not be visible in the UCSC genome browser. Please consider adding the --open-output flag if you are intending to use the UCSC browser with it.')

    if not args.region and args.region_format == BED12:
        _error_exit("The autogenerated regions can only be calculated in BED format. Did you forget to specify the --region ?")            

    if args.experiment_format not in READ_FORMATS:
        _error_exit('Sorry, Pyicoteo cannot read in %s format. Write formats are %s'%(args.output_format, WRITE_FORMATS))

    if args.output_format not in WRITE_FORMATS:
        _error_exit('Sorry, Pyicoteo cannot write in %s format. Write formats are %s'%(args.output_format, WRITE_FORMATS))

    _file_exists(args.experiment)
    _file_exists(args.experiment_b)
    _file_exists(args.region)
    _file_exists(args.control)
    _file_exists(args.replica)


def new_subparser(*args):
    return argparse.ArgumentParser(add_help=False)


def init_turbomix(args, parser_name=PARSER_NAME):
    turbomix = Turbomix(args.experiment, args.output, args.experiment_format, args.output_format, args.wig_label, args.open_experiment, args.open_output, args.debug,
                        args.rounding, args.tag_length, args.remlabels, args.control, args.control_format, args.open_control, args.region,
                        args.region_format, args.open_region, args.span, args.frag_size, args.p_value, args.height_limit, args.correction,
                        args.trim_proportion, args.no_sort, args.duplicates, args.threshold, args.trim_absolute, args.max_delta,
                        args.min_delta, args.height_filter, args.delta_step, args.verbose, args.species, args.cached, args.split_proportion, args.split_absolute, 
                        args.repeats, args.masker_file, args.max_correlations, args.keep_temp, args.experiment_b, args.replica, args.replica_b, args.poisson_test, 
                        args.stranded, args.proximity, args.postscript, args.showplots, args.plot_path, args.pseudocount, args.len_norm, args.label1, 
                        args.label2, args.binsize, args.zscore, args.blacklist, args.sdfold, args.recalculate, args.counts_file, args.mintags, args.binstep, 
                        args.tmm_norm, args.n_norm, args.skip_header, args.total_reads_a, args.total_reads_b, args.total_reads_replica, args.a_trim, args.m_trim, 
                        args.use_replica, args.tempdir, args.samtools, args.access_sequential, args.experiment_label, args.replica_label, args.title_label, 
                        args.count_filter, args.force_sort, args.push_distance, args.quant_norm, parser_name, args.region_magic, args.gff_file, 
                        args.interesting_regions, args.disable_significant_color, args.f_custom_in, args.custom_in_sep, args.f_custom_out, 
                        args.custom_out_sep, args.galaxy_workarounds, args.html_output, args.overlap)

    validate_operations(args, turbomix)
    return turbomix


def set_defaults(parser):
    parser.set_defaults(experiment=EXPERIMENT, experiment_format=EXPERIMENT_FORMAT, open_experiment=OPEN_EXPERIMENT, debug=DEBUG, discard=DISCARD, output=OUTPUT, control=CONTROL, 
                        wig_label = LABEL, output_format=OUTPUT_FORMAT,open_output=OPEN_OUTPUT, rounding=ROUNDING, control_format=CONTROL_FORMAT, region=REGION, region_format=REGION_FORMAT, 
                        open_region =OPEN_REGION,frag_size = FRAG_SIZE, tag_length = TAG_LENGTH, span=SPAN, p_value=P_VALUE, height_limit=HEIGHT_LIMIT, 
                        correction=CORRECTION, no_subtract = NO_SUBTRACT, normalize = DO_NORMALIZE, trim_proportion=TRIM_PROPORTION,open_control=OPEN_CONTROL, 
                        no_sort=NO_SORT, duplicates=DUPLICATES, threshold=THRESHOLD, trim_absolute=TRIM_ABSOLUTE, max_delta=MAX_DELTA, min_delta=MIN_DELTA, 
                        height_filter=HEIGHT_FILTER, delta_step=DELTA_STEP, verbose=VERBOSE, species=SPECIES, cached=CACHED, split_proportion=SPLIT_PROPORTION,
                        split_absolute=SPLIT_ABSOLUTE, repeats=REPEATS, masker_file=MASKER_FILE, max_correlations=MAX_CORRELATIONS, keep_temp=KEEP_TEMP, postscript = POSTSCRIPT,
                        remlabels=REMLABELS, experiment_b=EXPERIMENT, replica=EXPERIMENT, replica_b=EXPERIMENT, poisson_test=POISSONTEST, stranded=STRANDED_ANALYSIS,
                        proximity=PROXIMITY, showplots=SHOWPLOTS, plot_path=PLOT_PATH, pseudocount=PSEUDOCOUNT, len_norm=LEN_NORM, label1=LABEL1, 
                        label2=LABEL2, binsize=BINSIZE, zscore=ZSCORE, blacklist=BLACKLIST, sdfold=SDFOLD, recalculate=RECALCULATE, 
                        counts_file=COUNTS_FILE, mintags=REGION_MINTAGS, binstep=WINDOW_STEP, tmm_norm=TMM_NORM, n_norm=N_NORM, skip_header=SKIP_HEADER,  
                        total_reads_a=TOTAL_READS_A, total_reads_b=TOTAL_READS_B, total_reads_replica=TOTAL_READS_REPLICA, a_trim=A_TRIM, m_trim=M_TRIM, 
                        use_replica=USE_REPLICA, tempdir=TEMPDIR, samtools=USESAMTOOLS, access_sequential=SEQUENTIAL, experiment_label = EXPERIMENT_LABEL, 
                        replica_label = REPLICA_LABEL, title_label = TITLE_LABEL, count_filter = COUNT_FILTER, force_sort=FORCE_SORT, 
                        push_distance=PUSH_DIST, quant_norm=QUANT_NORM, parser_name=PARSER_NAME,
                        region_magic=REGION_MAGIC, gff_file=GFF_FILE, interesting_regions=INTERESTING_REGIONS, disable_significant_color=DISABLE_SIGNIFICANT,
                        f_custom_in=F_CUSTOM, custom_in_sep=CUSTOM_SEP, f_custom_out=F_CUSTOM, custom_out_sep=CUSTOM_SEP, galaxy_workarounds=GALAXY_WORKAROUNDS, 
                        html_output=HTML_OUTPUT, experiments=None, no_duplicates=False, overlap=EPSILON)


def parse_validate_args(parser, test_args=None): #test_args for unit testing
    """
    Parses and validates the arguments, returns a turbomix instance
    """
    set_defaults(parser)

    if test_args: #for unit testing
        args = parser.parse_args(test_args)
    else:
        args = parser.parse_args()

    validate(args)
    if args.counts_file: #the formats are overridden when using enrichment (only of cosmetic value, when printing the flags)   
        args.experiment_format = COUNTS
        args.experiment_b_format = COUNTS
        args.output_format = COUNTS

    if not args.control_format: #If not specified, the control format is equal to the experiment format
        args.control_format = args.experiment_format
        args.open_control = args.open_experiment

    if args.experiments: #for the pyicoenrich parser
        args.experiment, args.experiment_b = args.experiments

    if (args.experiment_format and args.experiment_format == CUSTOM_FORMAT) or (args.output_format and args.output_format == CUSTOM_FORMAT):
        from ..core import CustomReader, CustomWriter # FIXME: better way instead of import?
        CustomReader.f_custom_in = args.f_custom_in
        CustomReader.custom_in_sep = args.custom_in_sep
        CustomWriter.f_custom_out = args.f_custom_out
        CustomWriter.custom_out_sep = args.custom_out_sep

        if args.galaxy_workarounds:
            # Workaround for galaxy parameter passing
            mapped_chars = { '>' :'__gt__', 
                     '<' :'__lt__', 
                     "'" :'__sq__',
                     '"' :'__dq__',
                     '[' :'__ob__',
                     ']' :'__cb__',
                     '{' :'__oc__',
                     '}' :'__cc__',
                     '@' : '__at__',
                     '\n' : '__cn__',
                     '\r' : '__cr__',
                     '\t' : '__tc__',
                     '#' : '__pd__'
                     }
            for key, value in mapped_chars.items():
                CustomReader.custom_in_sep = CustomReader.custom_in_sep.replace(value, key)
                CustomWriter.custom_out_sep = CustomWriter.custom_out_sep.replace(value, key)

    return args

#A bit dirty, but works. Common flags that may be used by different pyicoteo tools. If one flag corresponds exclusively to one tool, move there. 

read_formats = str(READ_FORMATS)
write_formats = str(READ_FORMATS)
experiment = new_subparser()
experiment.add_argument('experiment', help='The experiment file or directory')
experiment_flags = new_subparser()
experiment_flags.add_argument('-o','--open-experiment', action='store_true', dest='open_experiment', default=OPEN_EXPERIMENT, help='Defines if the experiment is half-open or closed notation. [Default %(default)s]')
experiment_flags.add_argument( '-f','--experiment-format',default=EXPERIMENT_FORMAT,  dest='experiment_format', help="""The format the experiment file is written as.
                         The options are %s. [Default pk]"""%read_formats)

experiment_flags.add_argument('--f-custom-in', nargs='+', help="Custom input file format (integers: columns containing, in order, 'seqname', 'start', 'end', 'strand')")
experiment_flags.add_argument('--custom-in-sep', help="Custom format input file separator")
experiment_flags.add_argument('--f-custom-out', nargs='+', help="Custom output file format (integers: columns containing, in order, 'seqname', 'start', 'end', 'strand')")
experiment_flags.add_argument('--custom-out-sep', help="Custom format output file separator")

experiment_b = new_subparser()
experiment_b.add_argument('experiment_b',  help='The experiment file B')
optional_replica = new_subparser()
optional_replica.add_argument('--replica', help='Experiment A replica file')
replica = new_subparser()
replica.add_argument('replica', help='Experiment A replica file')
control = new_subparser()
control.add_argument('control', help='The control file or directory')
control_format = new_subparser()
control_format.add_argument('--control-format', default=CONTROL_FORMAT, help='The format the control file is written as. [default: The same as experiment format]')
optional_control = new_subparser()
optional_control.add_argument('--control', help='The control file or directory')

optional_control = new_subparser()
optional_control.add_argument('--control', help='The control file or directory')

open_control = new_subparser()
open_control.add_argument('--open-control', action='store_true', default=OPEN_CONTROL, help='Define if the region file is half-open or closed notation. [Default closed]')
basic_parser = new_subparser()
basic_parser.add_argument('--debug', action='store_true', default=DEBUG)
basic_parser.add_argument('--no-sort',action='store_true', default=NO_SORT, help='Force skip the sorting step. WARNING: Use only if you know what you are doing. Processing unsorted files assuming they are will outcome in erroneous results')
basic_parser.add_argument('--force-sort',action='store_true', default=False, help='Force the sorting step')
basic_parser.add_argument('--silent' ,action='store_false', default=VERBOSE, dest='verbose', help='Run without printing in screen')
basic_parser.add_argument('--disable-cache' ,action='store_false', default=CACHED, dest='cached', help='Disable internal reading cache. When Clustering low coverage files, it will increase speed and improve memory usage. With very read dense files, the speed will decrease.')
basic_parser.add_argument('--keep-temp', action='store_true', default=KEEP_TEMP, help='Keep the temporary files')
basic_parser.add_argument('--postscript', action='store_true', default=POSTSCRIPT, help='get the output graphs in postscript format instead of .png')
basic_parser.add_argument('--showplots', action='store_true', default=SHOWPLOTS, help='Show the plots as they are being calculated by matplotlib. Note that the execution will be stopped until you close the window pop up that will arise')
basic_parser.add_argument('--label1', default=LABEL1, help="Manually define the first label of the graphs.")
basic_parser.add_argument('--label2', default=LABEL2, help="Manually define the second label of the graphs.")
basic_parser.add_argument('--tempdir', default=TEMPDIR, help="Manually define the temporary directory where Pyicoteo will write. By default Pyicoteo will use the temporary directory the system provides (For example, /tmp in unix systems)")
basic_parser.add_argument('--samtools', default=USESAMTOOLS, action='store_true', help="Use samtools for reading BAM files [Default: Pyicoteo uses its own library] (reading BAM works without samtools for convert, extend, and other operations, but not for enrichment yet)]")
basic_parser.add_argument('--skip-header', action='store_true', default=SKIP_HEADER, help="Skip writing the header for the output file. [Default %(default)s]")
#basic_parser.add_argument('--get-report', action='store_true', default=SKIP_HEADER, help=". [Default %(default)s]")

basic_parser.add_argument('--galaxy-workarounds', default=GALAXY_WORKAROUNDS, action='store_true', help='Enables workarounds for compatibility with the Galaxy Project [Default %(default)s]')

stranded_flag = new_subparser()
stranded_flag.add_argument('--stranded', action='store_true', default=STRANDED_ANALYSIS, help="Decide if the strand is taken into consideration for the analysis. This requires a BED6 region file with the strand information in its 6th column.")

output = new_subparser()
output.add_argument('output', help='The output file or directory')
optional_output = new_subparser()
optional_output.add_argument('--output', help='The output file or directory')

output_flags = new_subparser()
output_flags.add_argument('-O','--open-output', action='store_true', default=OPEN_OUTPUT, help='Define if the output is half-open or closed notation. [Default closed]')
output_flags.add_argument('-F','--output-format',default=OUTPUT_FORMAT, help='Output format. Valid formats are %s.'%str(WRITE_FORMATS))
blacklist_help = 'Reads a bed file with coordinates that you want to exclude from the analysis. Useful for discarding "noisy" probable artifactual regions like centromeres and repeat regions. [Default %(default)s]'
blacklist = new_subparser()
blacklist.add_argument('blacklist', default=BLACKLIST, help=blacklist_help)
optional_blacklist = new_subparser()
optional_blacklist.add_argument('--blacklist', default=BLACKLIST, help=blacklist_help)
region = new_subparser()
region.add_argument('region', help='The region file')
optional_region = new_subparser()
optional_region.add_argument('--region', help='The region file or directory. In the enrichment analysis, if its not specified it will be calculated automatically from the tags in both files and the distance of clustering specified in the --proximity flag')
region_format = new_subparser()
region_format.add_argument('--region-format',default=REGION_FORMAT, help='The format the region file is written as. [default %(default)s]')
region_format.add_argument('--open-region', action='store_true', default=OPEN_REGION, help='Define if the region file is half-open or closed notation. [Default closed]')

checkrep_flags = new_subparser()
checkrep_flags.add_argument('--experiment-label', default=EXPERIMENT_LABEL, help='The label that will identify the experiment file in the "check replicas" plot')
checkrep_flags.add_argument('--replica-label', default=REPLICA_LABEL, help='The label that will identify the experiment file in the "check replicas" plot')
checkrep_flags.add_argument('--title-label', default=REPLICA_LABEL, help='The label that will identify the experiment file in the "check replicas" plot')
checkrep_flags.add_argument('--count-filter', default=COUNT_FILTER, type=float, help='Filter the points that go below a threshold to better visualize the correlation between the replicas')
total_reads_flags = new_subparser()
total_reads_flags.add_argument('--total-reads-a', type=int, default=0, help="To manually set how many reads the dataset in 'experiment' has. If not used, it will be counted from the read or counts file. Default (automatically calculated from reads or counts files)")
total_reads_flags.add_argument('--total-reads-b', type=int, default=0, help="To manually set how many reads the dataset in 'experiment_b' has. If not used, it will be counted from the read or counts file. Default (automatically calculated from reads or counts files)")
total_reads_flags.add_argument('--total-reads-replica', type=int, default=0, help="To manually set how many reads the dataset in 'experiment_replica' has. If not used, it will be calculated from the read or the counts file. Default %(default)s (not used)")
total_reads_flags.add_argument('--a-trim', type=float, default=A_TRIM, help="Proportion of A values to be discarded when doing the TMM normalization. Only applied when combined with --tmm-norm. [Default %(default)s]")
total_reads_flags.add_argument('--m-trim', type=float, default=M_TRIM, help="Proportion of M values to be discarded when doing the TMM normalization. Only applied when combined with --tmm-norm. [Default %(default)s]")
pseudocount = new_subparser() 
pseudocount.add_argument('--pseudocount', action='store_true', default=PSEUDOCOUNT, help="The usage of pseudocounts in the enrichment calculation allows the inclusion of regions that have n reads in one dataset and 0 reads in the other.  [Default %(default)s]")
zscore = new_subparser()  
zscore.add_argument('--zscore', type=float, default=ZSCORE, help="Significant Z-score value. [Default %(default)s]")        
use_replica = new_subparser()
use_replica.add_argument("--use-replica", action='store_true', default=USE_REPLICA, help="Indicates that for the calculation of the counts tables, a replica was used. [Default %(default)s]")
label = new_subparser()
label.add_argument('--wig-label', default=LABEL, help='The label that will identify the experiment in the WIG tracks.')
span = new_subparser()
span.add_argument('--span', default=SPAN, help='The span of the variable and fixed wig formats [Default %(default)s]', type=int)
round = new_subparser()
round.add_argument('--round',action='store_true', dest='rounding', default=ROUNDING, help='Round the final results to an integer')
pvalue = new_subparser()
pvalue.add_argument('--p-value',type=float, default=P_VALUE, help='The threshold p-value that will make a cluster significant. [Default %(default)s]')
tolerated_duplicates =new_subparser()
tolerated_duplicates.add_argument('--duplicates',type=int, default=DUPLICATES, help='The number of duplicated reads accept will be counted. Any duplicated read after this threshold will be discarded. [Default %(default)s]')
height = new_subparser()
height.add_argument('--k-limit',type=int, default=HEIGHT_LIMIT, help='The k limit Pyicoteo will analize to when performing a poisson test. Every cluster that goes over the threshold will have a p-value of 0, therefore considered significant. For performance purposes, raising it will give more precision when defining low p-values, but will take longer to execute. [Default %(default)s]')
correction = new_subparser()
correction.add_argument('--correction',type=float, default=CORRECTION, help='This value will correct the size of the genome you are analyzing. This way you can take into consideration the real mappable genome [Default %(default)s]')
tag_length = new_subparser()
tag_length.add_argument( '--tag-length',default=TAG_LENGTH, type=int, help='The tag length, or the extended one. Needed when converting from a Clustered format (wig, pk) to a non clustered format (bed, eland) [Default %(default)s]')
frag_size = new_subparser()
frag_size.add_argument('frag_size', help='The estimated inmmunoprecipitated fragment size. This is used by the extend operation to extend the tags, taking into consideration their strand, if provided. If the strand is not provided, Pyicoteo will assume positive strand.', type=int)
optional_frag_size = new_subparser()
optional_frag_size.add_argument('-x', '--frag-size', help='The estimated inmmunoprecipitated fragment size. This is used by Pyicoteo to reconstruct the original signal in the wet lab experiment.', type=int)
push_distance = new_subparser()
push_distance.add_argument('push_distance', help='', type=int)
optional_push = new_subparser()
optional_push.add_argument('--push', dest="push_distance", default=None, help='', type=int)
no_subtract = new_subparser()
no_subtract.add_argument('--no-subtract',action='store_true', default=False, help='Don\'t subtract the control to the output, only normalize.')
normalize = new_subparser()
normalize.add_argument('--normalize',action='store_true', default=False, help='Normalize to the control before subtracting')
extend = new_subparser()
extend.add_argument('--extend',action='store_true', default=False, help='Extend')
subtract = new_subparser()
subtract.add_argument('--subtract',action='store_true', default=False, help='subtract')
filterop = new_subparser()
filterop.add_argument('--filter',action='store_true', default=False, help='filterop')
poisson = new_subparser()
poisson.add_argument('--poisson',action='store_true', default=False, help='poisson')
modfdr = new_subparser()
modfdr.add_argument('--modfdr',action='store_true', default=False, help='modfdr')
remduplicates = new_subparser()
remduplicates.add_argument('--remduplicates',action='store_true', default=False, help='remduplicates')
split = new_subparser()
split.add_argument('--split',action='store_true', default=False, help='split')
trim = new_subparser()
trim.add_argument('--trim',action='store_true', default=False, help='trim')
strcorr = new_subparser()
strcorr.add_argument('--strcorr',action='store_true', default=False, help='strcorr')
remregions = new_subparser()
remregions.add_argument('--remregions',action='store_true', default=False, help='remregions')
remartifacts = new_subparser()
remartifacts.add_argument('--remartifacts',action='store_true', default=False, help='remartifacts')
checkrep = new_subparser()
checkrep.add_argument('--checkrep',action='store_true', default=False, help='check replicas')
split_proportion = new_subparser()
split_proportion.add_argument('--split-proportion', default=SPLIT_PROPORTION, help='Fraction of the cluster height below which the cluster is splitted. [Default %(default)s]', type=float)
trim_proportion = new_subparser()
trim_proportion.add_argument('--trim-proportion', default=TRIM_PROPORTION, help='Fraction of the cluster height below which the peak is trimmed. Example: For a cluster of height 40, if the flag is 0.05, 40*0.05=2. Every cluster will be trimmed to that height. A position of height 1 is always considered insignificant, no matter what the cluster height is. [Default %(default)s]', type=float)
trim_absolute = new_subparser()
trim_absolute.add_argument('--trim-absolute', default=TRIM_ABSOLUTE, help='The height threshold to trim the clusters. Overrides the trim proportion. [Default %(default)s]', type=int)
split_absolute = new_subparser()
split_absolute.add_argument('--split-absolute', default=SPLIT_ABSOLUTE, help='The height threshold to split the clusters. [Default %(default)s]', type=int)
repeats = new_subparser()
repeats.add_argument('--repeats', help='Number of random repeats when generating the "background" for the modfdr operation[Default %(default)s]', default=REPEATS, type=int)
masker_file = new_subparser()
masker_file.add_argument('--masker', help='You can provide a masker file that will be used by the modfdr operation background generation so that randomized reads will not fall in this areas')
poisson_test = new_subparser()
poisson_test.add_argument('--poisson-test', help="Decide what property of the cluster will be used for the poisson analysis. Choices are %s [Default %s]"%(POISSON_OPTIONS, POISSONTEST), default=POISSONTEST)   
remlabels = new_subparser()
remlabels.add_argument('--remlabels', help='Discard the reads that have this particular label. Example: --discard chr1 will discard all reads with chr1 as tag. You can specify multiple tags to discard using the following notation --discard chr1 chr2 tagN')
threshold = new_subparser()
threshold.add_argument('--threshold', help='The height threshold used to cut', type=int)
species = new_subparser()
species.add_argument('-p', '--species', default=SPECIES, help='The species that you are analyzing. This will read the length of the chromosomes of this species from the files inside the folder "chrdesc". If the species information is not known, the filtering step will assume that the chromosomes are as long as the position of the furthest read. [Default %(default)s]')
plot_path = new_subparser()
plot_path.add_argument('plot_path', default=PLOT_PATH, help='The path of the file to plot.')
correlation_flags = new_subparser()
correlation_flags.add_argument('--max-delta',type=int, default=MAX_DELTA, help='Maximum distance to consider when correlating the positive and the negative groups of reads [Default %(default)s]')
correlation_flags.add_argument('--min-delta',type=int, default=MIN_DELTA, help='Minimum distance to consider when correlating the positive and the negative groups of reads  [Default %(default)s]')
correlation_flags.add_argument('--correlation-filter', dest="height_filter", type=int, default=HEIGHT_FILTER, help='The minimum number of overlapping reads in a cluster to include it in the test [Default %(default)s]')
correlation_flags.add_argument('--delta-step',type=int, default=DELTA_STEP, help='The step of the delta values to test [Default %(default)s]')
correlation_flags.add_argument('--max-correlations',type=int, default=MAX_CORRELATIONS, help='The maximum pairs of clusters to analyze before considering the test complete. Lower this parameter to increase time performance [Default %(default)s]')    
counts_file = new_subparser()
counts_file.add_argument('counts_file', help='The counts file. The format required is a bed file with fields "name", "start", "end", "name2", "score(ignored)", "strand", "count file a", "count file b", "count file a", "count replica a" where the counts can be RPKMs or simple counts')

optional_gtf = new_subparser()
optional_gtf.add_argument('--gff-file', help='The GFF file from which to extract the genomic regions, in combination with --region-magic flag')
magic_flag = new_subparser()
magic_flag.add_argument('--region-magic', nargs='+', help="Desired features to filter (exons, introns, sliding window for inter-/intragenic zones, tss)")

overlap_flag = new_subparser()
overlap_flag.add_argument('--overlap', type=float, default=EPSILON, help="Minimum overlap between a read and a region to be considered 'inside' it [default is EPSILON, the smallest number closest to 0]")



#check replicas operation TODO unfinished
#subparsers.add_parser('checkrep', help='Check how good the replicas are.', parents=[experiment, experiment_flags, basic_parser, replica, region, region_format, checkrep_flags, output])
#check replicas operation
#subparsers.add_parser('checkrepcount', help='Check how good the replicas are (from a Pyicoteo count file)', parents=[counts_file, basic_parser, enrichment_flags, total_reads_flags, checkrep_flags, output])
#
#subparsers.add_parser('plot', help="Plot a file with Pyicoteo plotting utilities. Requires matplotlib >=0.9.7 installed.", parents=[basic_parser, plot_path, output, zscore])




