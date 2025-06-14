this is the most dirty code you have ever seen. said that its usefull. 

what it does:

it shows a gui

        # Labels and entry fields
        self.labels = [
            "MIDI Numbers (comma-separated):",
            "Width Fraction (0 < x < 1):",
            "Semitone Deviation:",
            "Halving Speed:",
            "Is Open:",
            "Ising Number:",
            "Wind Pressure (mm H2O):",
            "Is Cylindrical:",
            "Foot Height:",
            "Wall Thickness:",
            "Leather Thickness:",
            "Object Spacing:",
            "Document Unit:",
            "Document Width (mm):",
            "Document Height (mm):",
            "Directory Path:",
            "Fill Canvas:",
            "No ears:",
            "Round tuning handle:",
            "Handle dia (mm):"
        ]

you can input different values that make up the parts of an organ pipe.

midinumbers: give the midinumber of the pipe you want (you can enter more then one number comma seperated)

width fraction : the fraction of the circumference that makes the mouth width.

semitonedeviation : the offset in semitones from the standart organ pipe.

halving speed: the number off semitones that halves the diameter of a pipe.

is open: whether you want an open or a closed pipe.

ising number : search the web for that.

wind pressure : speaks for itself

is cylindrical: whether you want sizes for a cylindrical pipe. the design for that is not implemented

Foot height: the amount added to the length to accomodate the block.

Wall thickness : the material thickness.

Leather thickness : the thickness of the stopper leather.

object spacing : the space between parts in the design graphics.

document sizes : the sizes of the created svg canvas

directory path: the place where the svg will be stored.

fill canvas : whether a seperate file will be made for each pipe.

no ears : whether ears will be added at the sides of the mouth.

round tuning handle : not yet implemented

Handle diameter : not yet implemented.

the flow is roughly

enter the parameters in a gui

calculate the dimensions in the calculator class

print the dimensions using the calculator class

transfer the dimensions to the generator class.

generate the svg output using the generator class.



give it a try for a single pipe. it will calculate the pipe dimensions a generate an svg file of the different parts. 

![image](https://github.com/user-attachments/assets/bc0eb312-dbde-4a97-9ea7-4813434669a5)




