
This directory should only contain subdirectories with MMA library files.

The directory 'stdlib' should always be present. It contains the library
files distributed with MMA.

Other, user supplied, library files should be placed in
separate directories. For example, if you create your
own polka library file, you might want to create the
directory 'mymma' and place the file(s) there.

If you do this, make sure that you update the mma library
database with the mma -g command, or force the processing
of your files with the Use directive. Databases are stored
in each subdirectory and have the name .mmaDB. Don't try to
edit these ... just keep them updated with the command "mma -g".

Some initial guidelines.... 

>> Start each file with a commented filename. Just makes editing easier.

>> Follow the filename with  BEGIN DOC/END section. This holds a
   descriptive comment, used in the library reference header. 
   
>> Include an "Author" directive line. Currently this is treated as a
   comment, but we might use it in the future.

>> Do document ANY variables you use in the file with the DocVar command.

>> Add a DocDefine to the end of each goove definition. Something like:
	
       DefGroove Waltz This is a nice waltz groove.

   This is extracted using the -Dx command line option for creation
   of the library documentation.
		
>> Be as descriptive as possible in the pattern and groove names.
   Probably not as easy as it sounds ... but punct. and digits
   are permitted in pattern/groove names. Just remember that
   they are case-insensitive.

>> Use lots of comments and blank lines.
		
>> Try not to overwrite common names. There are no warnings for this,
   and it could create unwanted results. With auto-loading of grooves,
   name duplicates become more problematical!
	
>> Including voice, volume, random settings in a groove is probably
   a good idea. Easy enough for a user to override after he/she
   selects.

>> Don't make assumptions. Yes, you can get away without putting a
   Time directive at the top of lib file, but don't. Lib files should
   have an explicit SeqClear and SeqSize as well.
		
>> It is probably a bad idea for library files to include other library
   files. 

>> Do use the standard pattern include files! And don't rename the
   patterns defined in them ... well, unless you're sure you want to.
    
>> Create patterns in logical order. The order in which you define them
   is also the order in which they'll be listed in the docs.
   
March/2005, bvdp.



