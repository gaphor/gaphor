import copy
import inspect
import types
import string
import random
import time
import os

# This module is taken from SMW

def __getHundredNanosecondsSinceGregorianReform__():
    """<<<The timestamp is a 60 bit value. For UUID version 1, this is
    represented by Coordinated Universal Time (UTC) as a count of
    100-nanosecond intervals since 00:00:00.00, 15 October 1582 (the
    date of Gregorian reform to the Christian calendar).>>>"""

    # Since 1.1.1970 (unix epoch time)
    # BUG probably platform-dependent
    ns = time.time() * 1000 * 1000 * 10

    # Amount of 100 nanoseconds between 15.Oct.1582 to 1.1.1970
    # Takes even leap years into account
    ns_greg = ((1970-1583) * 365 + 78 + 92) * 24 * 60 * 60 * 1000 * 1000 * 10

    # BUG can long conversion lose information?
    return long(ns) + ns_greg

#Place holder for a RNG
theRNG=None

# Our NIC's MAC
ethernet = ""
# Our clocksequence
clocksequence = None
# Latest UTC
latest_utc = 0

def __generateString__(value, n_nibbles):
    """Generates nibbles, and reverses the resulting string."""
    s = []
    for i in range(n_nibbles):
        digit = value & 15
        value //= 16
        s.append(string.hexdigits[digit])

    s.reverse()
    return string.join(s, "")
    

def __generateID__():
    """This function returns a string with a unique ID for XMI objects.
    It adheres to the DCE specification of generating globally
    unique id:s. Assume there are buglets in this implementation,
    the spec isn't _that_ clean on the matter.
    http://www.opengroup.org/onlinepubs/9629399/apdxa.htm
    """
    
    global theRNG
    global ethernet
    global clocksequence
    global latest_utc

    if not theRNG:
        theRNG = random.Random(time.time())
        # Get the ethernet address
        try:
            #
            #
            # RedHat Linux, Debian GNU/Linux, SunOS 2.6
            #
            #
            f = os.popen("/sbin/ifconfig -a")
            try:
                while 1:
                    s = f.readline()
                    if not s:
                        raise Exception

                    #
                    # Linux
                    #
                    i = s.find("HWaddr")
                    if i != -1:
                        ethernet = string.join(s[i:].split()[1].split(":"), "")
                    else:
                        #
                        # SunOS
                        #
                        i = s.find("ether")
                        if i != -1:
                            e = s[i:].split()[1].split(":")
                            for i in range(len(e)):
                                if len(e[i]) == 1:
                                    e[i] = "0" + e[i]
                            ethernet = string.join(e, "")
                        else:
                            continue

                    f.close()
                    break
            except:
                f.close()
                raise
            
        except:
            #
            # Windows 2000 (perhaps also NT and XP)
            #
            try:
                f = os.popen("ipconfig /all")
                try:
                    while 1:
                        s = f.readline()
                        if not s:
                            raise Exception
                    
                        i = s.find("Physical Address")
                        if i != -1:
                            i = s.find(":")
                            if i != -1:
                                ethernet = string.join(s[i:].split()[1].split("-"), "")
                            else:
                                continue
                        else:
                            continue

                        f.close()
                        break
                except:
                    f.close()
                    raise
            except:
                # BUG: We randomize
                e = []
                for eth_i in range(12):
                    e.append(string.hexdigits[theRNG.randrange(16)])
                ethernet = string.join(e, "")

        # Initialize clock sequence. 14 bits
        clocksequence = theRNG.randrange(16384)
        
    s = ""
    # the final DCE string is of the form
    # "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    value = __getHundredNanosecondsSinceGregorianReform__()
    index = 0

    if value <= latest_utc:
        clocksequence += 1
    else:
        latest_utc = value

    # time_low
    s += __generateString__(value, 8)
    s += "-"
    
    # time_mid
    value >>= (4*8)
    s += __generateString__(value, 4)
    s += "-"
    value >>= (4*4)

    # time_hi_and_version
    value |= 1<<12 # UUID version 1
    s += __generateString__(value, 4)
    s += "-"

    value = clocksequence
    value |= 1<<15 # DCE variant
    s += __generateString__(value, 4)
    s += "-"

    s += ethernet

    return "DCE:%s" % s.upper()

def generate_id():
    return __generateID__()
