# CSE 190 Assignment 5 README

## IBM Model 1
### Training 
First, you need to create an IBM model 1 object using IBM(1) and assign it to a 
variable. Then, you call "ibm.train(sys.argv[1], sys.argv[2], sys.argv[3])" 
in the main function. To run the program, run 
"python ibm_models.py <source corpus> <target corpus> <pickle file to save parameters>"

This may take time due to pickling a large number of parameters

To change the number of iterations, go to line 111 under "train" and just change
the number. The default is 5.

### Getting Alignments
Make sure you still have an IBM model 1 object. Then, you call 
"ibm.write_align(sys.argv[1], sys.argv[2], sys.argv[3])" in the main function.
To run the program, run "python ibm_models.py <source corpus> <target corpus> <pickle file to retrieve parameters>"
Make sure you are using the parameter file you got from training the model.

To change where you save your alignments, go to line 125 under "write_align" 
function and change the filename.

## IBM Model 2
### Training 
Before starting, you first need a pickled t-parameters file from IBM Model 1. 
Refer to the Training section of IBM Model 1.

Then, you call "ibm.train(sys.argv[1], sys.argv[2], sys.argv[3])" 
in the main function. To run the program, run 
"python ibm_models.py <source corpus> <target corpus> <pickle file to save parameters>"

This may take time due to pickling a large number of parameters

To change the number of iterations, go to line 111 under "train" and just change
the number. The default is 5.

To change the filename for getting t-parameters from IBM Model 1, go to line 50
under "initialize" function and change the filename.

### Getting Alignments
Make sure you still have an IBM model 2 object. Then, you call 
"ibm.write_align(sys.argv[1], sys.argv[2], sys.argv[3])" in the main function.
To run the program, run "python ibm_models.py <source corpus> <target corpus> <pickle file to retrieve parameters>"
Make sure you are using the parameter file you got from training the model.

To change where you save your alignments, go to line 125 under "write_align" 
function and change the filename.

## Growing Alignments
Before starting, you first have to get parameters to estimate p(e|f). First, 
create an IBM model 1 and train it where English is the foreign language. Make 
sure to save the pickled t parameters to a different file. Then, before creating 
an IBM model 2, go to the 'initialize' function and go to the line where it is 
about to load the pickled t parameters. Make sure you change the filename to the
one you used for IBM model 1. Also, make sure to save the IBM model 2's 
parameters to a different file. After getting IBM Model 2's parameters, get the 
alignments using "write_align". Make sure you save the your alignments in a 
different file.

At this point, make sure you have alignments for p(f|e) and p(e|f). 
In your main function, make sure to call "grow_align(sys.argv[1], sys.argv[2])".
To run the program, run "python ibm_models.py <p(f|e) alignments> <p(e|f) alignments>"

To change where you save your grown alignments, go to line 205 under 
"grow_align" function and change the filename

## Other notes
If you like, you can enable print statements to show the progress of the program
by uncommenting them in ibm_models.py.

 