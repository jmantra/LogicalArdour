
Short usage file for pg2mma.py.

This program is used to convert a PGMusic .pat file containing
extended patch definitions to a MMA format. The .pat files will
contain lines like:

        [                                                      
        [Yamaha PSR 9000 - E.Piano                                 
        [     (P1)                                                             
        4.0.114=Galaxy EP
        4.0.117=Stage EP
        4.0.115=Polaris EP
        5.0.118=Jazz Chorus
        5.0.113=Hyper Tines
        4.0.119=Cool! EP
        4.0.120=Phase EP
        5.0.116=New Tines

This program will convert the above to:

     Begin Patch Set
        // Yamaha PSR 9000 - E.Piano                                 
        //   (P1)                                                             
        4.0.114=GalaxyEp
        4.0.117=StageEp
        4.0.115=PolarisEp
        5.0.118=JazzChorus
        5.0.113=HyperTines
        4.0.119=Cool!Ep
        4.0.120=PhaseEp
        5.0.116=NewTines
     End

The names in the original file are converted to CamelCase; both ';' and []
comments are converted to MMA // style.

The conversion recognizes the "ONEBASED" keyword. When found, subsequent
patch values will be decremented by 1.

The produced files should be useable directly by mma. However, there are a
few cautions:

 - the .pat files we've looked at do contain errors. 
 - many of the .pat files redefine existing GM voice names. You will need to
   change these names or put up with warning messages from MMA.

Usage: pg2mma.py <infile> <outfile>

No options. Both infile and outfile must be specified. No files will
be overwritten.

bvdp, September 2007.

