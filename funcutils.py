import logging
import inspect
from functools import wraps

logger = logging.getLogger('funcutils')


def memoize(key_maker):
    """Given a function which can generate hashable keys from another
    functions arguments, memoize returns a decorator that will cache
    the results of the decorated function"""
    def decorator(f):
        cache = {}
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get key for cache and values that will be passed on to
            # the decorated function through updated keyword arguments
            key = key_maker(*args, **kwargs)
            if cache.get(key):
                logger.debug('Returning from cache key: %s' % (repr(key)))
                return cache[key]
            else:
                results = f(*args, **kwargs)
                logger.debug('Caching results of execution')
                cache[key] = results
                return results
        return wrapper
    return decorator


def caller_info(levels_down=1):
    """Return module and function name of function two levels
    down the stack, so- the caller of whichever function called
    this one"""
    # inspect stack for caller module and function
    func, mod, mod_name = None, None, None
    caller = inspect.stack()[levels_down+1]
    try:
        func = caller[3]
        mod = inspect.getmodule(caller[0])
        mod_name = getattr(mod, '__name__', '__main__')
    finally:
        del caller
        del mod
    return mod_name, func


def flatten(l):
    """Take a heterogeneous list which may contain sublists
    and flatten them into a single stream of values"""
    for i in l:
        if is_seq(i):
            for j in flatten(i):
                yield j
        else:
            yield i


def tuplify(l, modifier=None):
    """Convert lists and sublists to tuples
    with optional modifier of each element"""
    new_l = []
    for i in l:
        if is_seq(i):
            new_l.append(tuplify(i, modifier=modifier))
        elif modifier:
            new_l.append(modifier(i))
        else:
            new_l.append(i)
    return tuple(new_l)


def is_seq(item):
    """Check for sequences"""
    if getattr(item, '__iter__', None) and not isinstance(item, bytearray):
        return True
    else:
        return False


def remove_ws(s):
    """Remove whitespace from string"""
    return ' '.join(s.split())


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def pipe(init, func_list=None):
    """Pipe the results and inputs of a list of functions

    Given an initial input value for the first function in
    the function list, pipe the results of each function
    into the input of the next.  If the results of a function
    in the pipeline are not truthy, return them without
    continuing down the pipeline
    """
    i = init
    while func_list:
        f = func_list.pop(0)
        i = f(i)
        if not i:
            return i
    return i
