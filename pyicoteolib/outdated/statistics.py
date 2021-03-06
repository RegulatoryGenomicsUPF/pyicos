import math
import os
import sys
from datetime import datetime
import copy

import utils.log
from peak import Peak

class Analysis:
    """Abstract class for the different analysis methods"""
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        
        if os.path.isdir(output_path):
            if output_path[-1] != '/':
                output_path = '%s/'%output_path

            self.output_dir = output_path
            self.log = utils.log.Log('%sanalysis.txt' % self.output_dir) 
        else:
            self.log = utils.log.Log(output_path)
            self.output_dir = '%s/'%os.path.abspath(os.path.dirname(output_path))
            
    
    def set_parameters(self):
        raise NotImplementedError("You're using the abstract base class 'Analysis', use a specific class instead")
    
    def run(self):
        """entry point for the analysis process """  
        self.log.write('\nAutomatically generated by PICOS ANALYSIS\n-----------------\n\nDate: %s\n'%(datetime.now()))
        if os.path.isdir(self.input_path):
            self.log.write('Directory analyzed:%s\n'%os.path.abspath(self.input_path))
            for filename in os.listdir(self.input_path):
                if os.path.isfile(self.input_path+filename):
                    self._analize_file(self.input_path+filename)
        else:
            self._analize_file(self.input_path)
        self.log.write('\n\nAnalysis finished successfully!')
    
    def _analize_file(self, file_path):
        self.log.write('-------------------------------------\n\nFile:%s\n'%os.path.basename(file_path)) 
        self.analysis(file_path)
    
    def analysis(self, file_path):
        raise NotImplementedError("You're using the abstract base class 'Analysis', use a specific class instead")


class PoissonAnalysis(Analysis):
            
    def poisson(self, actual, mean):
        #From StackOverflow
        # naive:   math.exp(-mean) * mean**actual / factorial(actual)
        # iterative, to keep the components from getting too large or small:
        p = math.exp(-mean)
        for i in xrange(actual):
            p *= mean
            p /= i+1
        return p        
   
    def _process_line(self, line):
        """returns an array with the line processed: start, end, array of length:peak"""
        try:
            line = line.split()
            return (int(line[1]), int(line[2]), line[3].split('|')) 
        except:
            print 'skipping header'
            return None
      
    def _correct_bias(self, p_value):
        if p_value < 0:
            return 0
        else:
            return p_value
  
    def set_parameters(self, p_value, height_limit, correction_factor, read_length):
        self.p_value = p_value
        self.height_limit = height_limit
        self.correction_factor = correction_factor
        self.read_length = read_length
        
    def analysis(self, file_path):
        """
        We do 3 different global poisson statistical tests for each file:
        
        Nucleotide analysis:
        This analysis takes the nucleotide as the unit to analize. We give a p-value for each "height"
        of read per nucleotides using an accumulated poisson. With this test we can infer more accurately 
        what nucleotides in the "peak" are part of the DNA binding site
        
        Peak analysis:
        This analysis takes as a basic unit the "peak" profile and performs a poisson taking into account the height (and the length?)
        of the profile. This will help us to better know witch peaks are statistically significant and witch are product of chromatine noise
        
        Number of reads analysis:
        We analize the number of reads of the cluster. Number of reads = sum(xi *yi ) / read_length
        """
        self.log.write('Correction factor for the size of the genome is %s...\n\n'%(self.correction_factor))
        input_file = file(file_path, 'rb')
           
        readsperbase_log = utils.log.Log('%s/reads_per_base_%s.log'%(self.output_dir, os.path.basename(file_path)))
        maxheight_log = utils.log.Log('%s/maxheight_per_peak_%s.log'%(self.output_dir, os.path.basename(file_path)))
        numreads_log = utils.log.Log('%s/numreads_per_peak_%s.log'%(self.output_dir, os.path.basename(file_path)))
        
        total_bp_with_reads = 0.
        start = sys.maxint
        end = 0. 
        total_peaks = 0.
        total_reads = 0
        acum_height = 0.
        
        heights = dict()
        max_heights = dict()
        numreads_dict = dict()
        
        absolute_max_height = 0
        absolute_max_numreads = 0

        #process the file to extract the information
        for line in input_file:       
            processed_line = self._process_line(line)  
            
            if self._process_line(line) is not None:
                start = min(start, processed_line[0])
                end = max(end, processed_line[1]) 
                max_height = 0.
                acum_numreads = 0.
                total_peaks+=1
                
                for level in processed_line[2]:
                    numbers = level.split(':')
                    len = int(numbers[0])
                    height = float(numbers[1])
                    
                    if height not in heights:
                        heights[height] = len
                    else:  
                        heights[height] += len
                    
                    total_bp_with_reads+=len
                    max_height = max(max_height, height)
                    acum_numreads += len*height
                   
                #numreads per peak
                numreads_in_cluster = acum_numreads/self.read_length
                total_reads += numreads_in_cluster 
                absolute_max_numreads = max(numreads_in_cluster, absolute_max_numreads)
                
                if int(numreads_in_cluster) not in numreads_dict:
                    numreads_dict[int(numreads_in_cluster)] = 1
                else:  
                    numreads_dict[int(numreads_in_cluster)] += 1
        
                #maxheight per peak
                if max_height not in max_heights:
                    max_heights[max_height] = 1
                else:  
                    max_heights[max_height] += 1
                    
                acum_height += max_height
                absolute_max_height = max(max_height, absolute_max_height)
        
        total_bp = end-start #total base pairs in the 
        reads_per_bp =  total_bp_with_reads / total_bp*self.correction_factor
        
        p_nucleotide = 1.
        p_peak = 1.
        p_numreads = 1.
        k = 0
        self.log.write_line('k\tBp\tPeak\tNum_reads')
        while (absolute_max_numreads > k) or (absolute_max_height > k):
            p_nucleotide -= self.poisson(k, reads_per_bp) #analisis nucleotide
            p_peak -= self.poisson(k, acum_height/total_peaks) #analysis peak
            p_numreads -= self.poisson(k, total_reads/total_peaks) #analysis numreads
            
            p_nucleotide = self._correct_bias(p_nucleotide)
            p_peak = self._correct_bias(p_peak)
            p_numreads = self._correct_bias(p_numreads) 
            if ((p_nucleotide > self.p_value) or  (p_peak > self.p_value) or (p_numreads > self.p_value)) and (k < self.height_limit): 
                self.log.write_line('%s\t%.5f\t%.5f\t%.5f'%(k, p_nucleotide, p_peak, p_numreads)) 
            
            if k in heights:
                readsperbase_log.write_line("%s\t%s\t%.5f%%\t%.5f"%(k, heights[k], heights[k]/total_bp_with_reads, p_nucleotide))      
            if k in max_heights:
                maxheight_log.write_line("%s\t%s\t%.5f%%\t%.5f"%(k, max_heights[k], max_heights[k]/total_peaks, p_peak))   
            if k in numreads_dict:   
                numreads_log.write_line("%s\t%s\t%.5f%%\t%.5f"%(k, numreads_dict[k], numreads_dict[k]/total_peaks, p_numreads))
            k+=1
        
class CorrelationAnalysis(Analysis):
    
    delta_results = dict()
    best_delta = -1
    
    def __add_zeros(self, array, num_zeros):
        for i in range(0, num_zeros):
            array.append(0)
    
    def analize_paired_peaks(self, positive_peak, negative_peak, delta):
        from scipy.stats.stats import pearsonr
        positive_array = []
        negative_array = [] 
        #delta correction
        corrected_positive_start = positive_peak.start + delta
        #add zeros at the start of the earliest peak
        if corrected_positive_start > negative_peak.start:
            self.__add_zeros(positive_array, corrected_positive_start - negative_peak.start)
        elif negative_peak.start > corrected_positive_start:  
            self.__add_zeros(negative_array, negative_peak.start - corrected_positive_start)
        #add the values of the peaks
        positive_array.extend(positive_peak.get_heights())
        negative_array.extend(negative_peak.get_heights())
        #add the zeros at the end of the shortest array
        if len(positive_array) > len(negative_array):
            self.__add_zeros(negative_array, len(positive_array) - len(negative_array))
        elif len(positive_array) < len(negative_array):
            self.__add_zeros(positive_array, len(negative_array) - len(positive_array))
        
        return pearsonr(negative_array, positive_array)
    
    def set_parameters(self, min_delta=40, max_delta=200, delta_step=2, height_filter=15, duplicate_limit = 20, no_short=False):
        self.min_delta = min_delta
        self.max_delta = max_delta
        self.delta_step = delta_step
        self.height_filter = height_filter
        self.duplicate_limit = duplicate_limit
        self.no_short = no_short
        
    def analysis(self, file_path):
        #make sure that the file is sorted
        if self.no_short:
            sorted_pk = file(file_path, 'r')
        else:
            print 'Sorting stranded pk file...'
            bsort = utils.bigSort.BigSort()
            sorted_pk = bsort.sort(file_path,None,lambda x:(x.split()[0],int(x.split()[1]),int(x.split()[2])))
            print 'Sorted. Calculating correlation...'

        positive_peak = None
        negative_peak = None
        self.analized_pairs = 0. 
        for line in sorted_pk:
            peak = Peak(line, rounding = True)
            if (peak.get_max_height() > self.height_filter) and not peak.has_duplicates(self.duplicate_limit):
                    if peak.strand == '+':
                        positive_peak = copy.deepcopy(peak)#big positive peak found
                        self._start_analysis(positive_peak, negative_peak)
                    else:
                        negative_peak = copy.deepcopy(peak)#big negative peak found
                        self._start_analysis(positive_peak, negative_peak)
        
        print 'FINAL DELTAS:'
        data = []
        for delta in range(self.min_delta, self.max_delta, self.delta_step): 
            if delta in self.delta_results:
                self.delta_results[delta]=self.delta_results[delta]/self.analized_pairs
                data.append(self.delta_results[delta])
                self.log.write_line('Delta %s:%s'%(delta, self.delta_results[delta]))

        try:
            import matplotlib.pyplot 
            matplotlib.pyplot.plot(range(self.min_delta, self.max_delta), data)
            matplotlib.pyplot.plot()
            matplotlib.pyplot.savefig('%s%s.png'%(self.output_dir, os.path.basename(file_path)))   
            #matplotlib.pyplot.show()
        except ImportError:
            print 'you dont have matplotlib installed, therefore picos cant create the graphs'
        except:
            print 'cant print the plots, unknown error'
        
        sorted_pk.close()
        if self.no_short:
            print 'removing temp file at %s...'%(sorted_pk.name)
            os.remove(sorted_pk.name)
        
    def _start_analysis(self, positive_peak, negative_peak):
        if positive_peak is not None and negative_peak is not None:
            if (abs(negative_peak.start-positive_peak.end) < self.max_delta or abs(positive_peak.start-negative_peak.end) < self.max_delta or positive_peak.intersects(negative_peak)) and positive_peak.chr == negative_peak.chr:
                self.analized_pairs+=1
                print 'Pair of peaks:'
                print positive_peak.line(), negative_peak.line(),
                for delta in range(self.min_delta, self.max_delta+1, self.delta_step):  
                    r_squared = self.analize_paired_peaks(positive_peak, negative_peak, delta)[0]**2
                    if delta not in self.delta_results:
                        self.delta_results[delta] = r_squared
                    else:
                        self.delta_results[delta] += r_squared      
                    #print 'Delta %s:%s'%(delta, result)
                    
                    
                    
                    
                    
                    
        
