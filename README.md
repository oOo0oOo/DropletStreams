DropletStreams
==============

Droplet Simulation (State based) with an interactive interpreter


#### Stream Commands


**-->**

Declaration/Copy statement


**(size[, variation]) --> a**

Define a as a stream of droplets with defined size and variation (0-1).
**() --> a** defines droplets with volume 0, **(size) --> a** makes droplets with no variation in size.


**{molecule, amount} --> a**

Add amount of molecule to droplets in stream a

**a --> b**

b is copy of a (more like b can source from a. Others can step in)


**show a**

Shows what a is (in this case a stream).
Also shows droplets (we'll get to that later)


**a, b -c-> c**

Creates stream c by alternatingly sampling a and b


**a, b -m-> c**

Creates stream c by merging one droplet from a and b


**a -s-> b**

Splits droplets from stream a (amount and molecules) and creates stream b


**a -o-> b**

Copy a over b. This means if a droplet from b is requested, it is not generated
but requested from a instead.


**-!o-> b**

Remove copy over. Reset b to original droplets.


**a, ... , n -b10-> x**

Creates a buffer (randomizer) of size 10 (in example) from all provided input streams.
When initialized the buffer cycles through the provided input streams, pulling 1 droplet each
until buffer size is reached.
When a droplet is requested, a random droplet from the buffer is removed and returned; 
the next input stream provides the missing droplet.


**a -(+ mol1, ..., moln)-> b**

Filters stream a and only lets droplets pass which contain all mentioned names (comma separated).


**a -(- mol1, ..., moln)-> b**

Filters stream a and only lets droplets pass which do not contain all mentioned names.


**a -(monitor_name)-> b**

Sets up a monitor which plots information about each passing droplet.





###Droplet Commands

Until now we have only set up streams. A pipe system is a good anology, where we can now
request a droplet at the bottom.

**a -10-> b**

Samples 10 droplets from stream a and saves them as droplets b.
!You can currently have a stream bbb and droplets bbb at the same time! (Don't know if this is clever...)
This will also trigger the monitors in between the streams.

**a -+10-> b**

Similar to a -10-> b but adds to droplet container if present. 


**plot b**

plots droplets of b in 3d space (up to three molecules, rest is ignored).


**unique b**

shows how many unique droplets b contains


**hist 100, b**

Show histograms (100 bins) for each dye in droplets b




###Comments, Whitespace & Multi Line Statements

Use **#** to comment a line


All whitespace is ignored.


Use ; to separate multiple statements on one line like such:

**(100) --> a; {mol1, 100} --> a**





###Snippets & Loops

A snippet is a series of statements, which can be executed at a later point.
It is similar to a function without arguments.
To define a snippet write '>snippet_name' as the first statement. 
Every following statement on the same line constitutes the snippet.

**> create_red; (100) --> a; {red, 10} --> a**

The statement to execute a snippet is the snippet name, in this case:


**create_red**

To loop a series of statements use 'loop n' as the first statement of a line,
where n is the number of times the following statements will be executed.


**loop 3; {red, 10, 0.01} --> a**

To add some red to a three times.





###Load & Save

You can also load your simulations from files.
Just open a text editor, write the code and save the file as filename.streams
in the same folder as stream_parser.py.

To load and execute the statements in a file simply use: 

**filename >**


In case you want to save the content of the file in a snippet and use it later:

**filename > snippet_name**


It is currently not possible to save streams but droplets can be saved to a .csv file using:

**csv a, filename**

Saves droplets in a as filename.csv.

