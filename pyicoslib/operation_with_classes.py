
class OperationFailed(Exception):
    pass

class UnknownOperation(Exception):
    pass


class Operation:
    active = True

class Normalize:
    def __str__(self):
        return 'normalize'

class Extend:
    def __str__(self):
        return 'extend'

class Subtract:
    def __str__(self):
        return 'subtract'

class Split:
    def __str__(self):
        return 'split'

class Trim:
    def __str__(self):
        return 'trim'

class Filter:
    def __str__(self):
        return 'filter'

class Poisson:
    
    def __str__(self):
        return 'poisson'


class NoWrite:
    def __str__(self):
        return 'nowrite'

class DiscardArtifacts:
    def __str__(self):
        return 'discard'

class RemoveRegion:
    def __str__(self):
        return 'remove'

class RemoveDuplicates:
    def __str__(self):
        return 'remove_duplicates'

class ModFDR:
    def __str__(self):
        return 'modfdr'

class StrandCorrelation:
    def __str__(self):
        return 'strand_correlation'

class Enrichment:
    incompatible_with = [ModFDR, Filter, Poisson]

    def __str__(self):
        return 'enrichment'


class OperationController:
 
    operations = []
    def add(operation):
        if operation == 'normalize':
            operations.append(Normalize())
        elif operation == 'extend':
            operations.append(Extend())
        elif operation == 'subtract':
            operations.append(Subtract())
        elif operation == 'split':
            operations.append(Split())
        elif operation == 'trim':
            operations.append(Trim())
        elif operation == 'poisson':
            operations.append(Poisson())
        elif operation == 'nowrite':
            operations.append(NoWrite())
        elif operation == 'discard':
            operations.append(DiscardArtifacts())
        elif operation == 'remove_duplicates':
            operations.append(RemoveDuplicates())
        elif operation == 'strand_correlation':
            operations.append(StrandCorrelation())
        elif operation == 'enrichment':
            operations.append(Enrichment())
        else:
            raise UnknownOperation


    def exists(operation):
        """Returns True if the operation has been added to the controller, False otherwise"""
        for o in self.operations:
            if o == operation.__class__:
                return True
        return False        

    def deactivate(operation):
        for o in self.operations:
            if o == operation.__class__:
                o.active = False
        return False        
        





