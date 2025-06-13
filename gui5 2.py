import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext 
import math
import sys
import os
import copy
from lxml import etree as ET
from svgpathtools import parse_path
from rectpack import newPacker, float2dec, SkylineBlWm

debug = True
debug = True  # Set this to True for debug output, False to disable

class RectanglePacker:
    def __init__(self, dx=2, dy=2, canvas_width=297, canvas_height=210):
        self.dx = dx
        self.dy = dy
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def collect_blue_rectangles(self, element, blue_rectangles):
        if element.tag.endswith('rect') and 'stroke:blue' in element.attrib.get('style', ''):
            blue_rectangles.append(element)
            if debug: print(f"Collected blue rectangle: {ET.tostring(element, encoding='unicode')}")
        for child in element:
            self.collect_blue_rectangles(child, blue_rectangles)

    def pack_rectangles(self, root):
        blue_rectangles = []
        self.collect_blue_rectangles(root, blue_rectangles)

        if not blue_rectangles:
            if debug: print("No blue rectangles found.")
            return [root]

        if debug: print(f"Number of blue rectangles collected: {len(blue_rectangles)}")

        rectangles = [
            (
                round(float(rect.attrib['width'][:-2]) + self.dx, 3),
                round(float(rect.attrib['height'][:-2]) + self.dy, 3),
                rect.attrib['id']
            )
            for rect in blue_rectangles
        ]

        if debug:
            print("Rectangles to be packed:")
            for rect in rectangles:
                print(f"Width: {rect[0]}, Height: {rect[1]}, ID: {rect[2]}")

        total_area_of_rectangles = sum(w * h for w, h, _ in rectangles)
        area_of_bin = self.canvas_width * self.canvas_height
        num_bins = int(1.5 * total_area_of_rectangles / area_of_bin) + 1

        if debug:
            print(f"Total area of rectangles: {total_area_of_rectangles}")
            print(f"Area of a single bin: {area_of_bin}")
            print(f"Number of bins needed: {num_bins}")

        packer = newPacker(rotation=False)

        # Add calculated number of bins
        for _ in range(num_bins):
            packer.add_bin(self.canvas_width, self.canvas_height)

        for rect in rectangles:
            packer.add_rect(rect[0], rect[1], rect[2])
            if debug: print(f"Added rectangle to packer: {rect}")

        packer.pack()

        if debug: print(f"Number of bins used: {len(packer)}")

        new_roots = []
        for abin in packer:
            if debug: print(f"Processing bin {abin.bid} with {len(abin)} rectangles")

            # Create a new root element based on the original root, but only change size attributes
            new_root = ET.Element(
                root.tag,
                {k: v for k, v in root.attrib.items() if k not in ['width', 'height', 'viewBox']}
            )
            new_root.attrib['width'] = str(self.canvas_width) + 'mm'
            new_root.attrib['height'] = str(self.canvas_height) + 'mm'
            new_root.attrib['viewBox'] = f"0 0 {self.canvas_width} {self.canvas_height}"

            for rect in abin:
                original_rect = root.find(".//*[@id='" + rect.rid + "']")
                if original_rect is not None:
                    if debug: print(f"Found original rectangle for ID {rect.rid}")
                    parent_group = original_rect.getparent()
                    copied_group = copy.deepcopy(parent_group)

                    original_x = float(original_rect.attrib.get('x', '0'))
                    original_y = float(original_rect.attrib.get('y', '0'))
                    translate_x = rect.x - original_x
                    translate_y = rect.y - original_y

                    copied_group.attrib['transform'] = f'translate({translate_x}, {translate_y})'
                    if debug:
                        print(f"Copied group transformed for rectangle ID {rect.rid}")
                        print(f"Transform: translate({translate_x}, {translate_y})")
                    new_root.append(copied_group)

            new_roots.append(new_root)

        return new_roots

    def save_svg_files(self, roots, base_path='output/'):
        for i, root in enumerate(roots):
            tree = ET.ElementTree(root)
            filename = os.path.join(base_path, f'output_bin_{i}.svg')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            tree.write(filename)
            print(f'Saved {filename}')

# Usage example
# Assuming you have an XML tree root
# root = ET.parse('your_svg_file.svg').getroot()

# Create an instance of RectanglePacker and call pack_rectangles
# packer = RectanglePacker()
# packed_roots = packer.pack_rectangles(root)

# Save the new roots to different files
# packer.save_svg_files(packed_roots, base_path='your_output_directory/')



class OrganPipe:

    #https://dl.acm.org/doi/fullHtml/10.1145/3561212.3561225
    #https://michaelkrzyzaniak.com/organ_pipe_maker/
    
    def __init__(self, midi_number, width_fraction, semitone_deviation, halving_speed, is_open, ising_number, wind_pressure, is_cylindrical=False):
        self._midi_number = midi_number
        self._width_fraction = width_fraction
        self._semitone_deviation = semitone_deviation
        self._halving_speed = halving_speed
        self._is_open = is_open
        self._ising_number = ising_number
        self._wind_pressure = wind_pressure
        self._is_cylindrical = is_cylindrical

        # Initialize these attributes with None, as they are calculated in calculate_organ_pipe_dimensions
        self._frequency = None
        self._pipe_length = None
        self._width_rectangular = None
        self._depth_rectangular = None
        self._mouth_height = None
        
        self._pipe_diameter = None
        self._circumference = None
        self._mouth_width = None
        self._windsheet = None
        self._airflow = None

        # Call calculate_organ_pipe_dimensions after other attributes are initialized
        self.calculate_organ_pipe_dimensions()


    
    @property
    def midi_number(self):
        return self._midi_number

    @midi_number.setter
    def midi_number(self, value):
        self._midi_number = value
        self.calculate_organ_pipe_dimensions()

    @property
    def frequency(self):
        return self._frequency

    @property
    def pipe_length(self):
        return self._pipe_length

    @property
    def width_rectangular(self):
        return self._width_rectangular

    @property
    def depth_rectangular(self):
        return self._depth_rectangular

    @property
    def mouth_height(self):
        return self._mouth_height

    @property
    def pipe_diameter(self):
        return self._pipe_diameter

    @property
    def circumference(self):
        return self._circumference
        
    @property
    def mouth_width(self):
        return self._mouth_width

    @property
    def windsheet(self):
        return self._windsheet

    @property
    def airflow(self):
        return self._airflow

    def calculate_airflow(self):
        # Formula for airflow 'α'
        flow = 20.45 * self._mouth_width * self._windsheet * math.sqrt((self._wind_pressure/25.4))
        return flow
        
    def calculate_organ_pipe_dimensions(self):
        # Calculate frequency from MIDI note number 
        self._frequency = 440.0 * (2 ** ((self._midi_number - 69) / 12.0))
        # Calculate length of the open organ pipe
        self._pipe_length = self.calculate_organ_pipe_length(self._frequency)

        # Calculate diameter of the cylindrical pipe based on MIDI number, semitone deviation, and halving speed
        self._pipe_diameter = self.calculate_pipe_diameter()
        
        # Calculate circumference
        self._circumference = math.pi* self._pipe_diameter

        # Calculate width and depth of the rectangular pipe
        self._width_rectangular, self._depth_rectangular = self.calculate_rectangular_pipe_dimensions(self._pipe_diameter)

        # Calculate mouth height based on whether the pipe is open or closed
        self._mouth_height = self.calculate_mouth_height(self._frequency)

        # Calculate mouth width as a dimension
        self._mouth_width = self._circumference*self._width_fraction

        # Calculate windsheet
        self._windsheet = self.calculate_windsheet(self._ising_number, self._wind_pressure)

        # Calculate airflow
        self._airflow = self.calculate_airflow()
 
    def calculate_pipe_diameter(self):
        # Constants
        reference_diameter = 155.5  # Reference diameter for MIDI note 36

        # Calculate diameter using the formula
        diameter = reference_diameter / (2 ** ((self._midi_number + self._semitone_deviation - 36) / (self._halving_speed - 1)))

        return diameter

    def calculate_rectangular_pipe_dimensions(self, cylinder_diameter):
        # Calculate cross-sectional area of the cylindrical pipe
        area_cylindrical = math.pi * ((cylinder_diameter/2)**2)

        # Calculate width of the rectangular pipe (setting it equal to mouth_width)
        width_rectangular = self._circumference*self._width_fraction

        # Calculate depth of the rectangular pipe to maintain the same cross-sectional area
        depth_rectangular = area_cylindrical / width_rectangular

        return width_rectangular, depth_rectangular

    def calculate_organ_pipe_length(self, frequency):
        if self._is_open:
            length = (2 * (1000 * 343.0) / (4 * frequency))
        else:
            length = ((1000 * 343.0) / (4 * frequency))

        return length

    def calculate_mouth_height(self, frequency):
        if self._is_open:
            mouth_height = 550 / (2 ** math.log(frequency))
        else:
            mouth_height = (3.018 - 0.233 * math.log(frequency)) ** 5

        return mouth_height

    def calculate_windsheet(self, ising_number, air_pressure):
        # Formula for windsheet 's'
        windsheet = (2.409 * 10**-9 * (ising_number**2 * self._frequency**2 * self._mouth_height**3)) / (air_pressure / 25.4)
        return windsheet

    def calculate_mouth_width(self, cylinder_diameter):
        # Calculate the circumference of the cylindrical pipe
        circumference = math.pi * cylinder_diameter

        # Calculate mouth width as a fraction of the circumference
        mouth_width =  self._width_fraction * self._circumference

        return mouth_width

    def print_organ_pipe_dimensions(self):
        diameter_cylinder = self.calculate_pipe_diameter()

        # Print dimensions for both types of pipes
        if self._is_open:
            open_or_closed = "Open"
        else:
            open_or_closed = "Closed"

        print(f"Organ Pipe Dimensions for MIDI Number {self._midi_number}  {open_or_closed}:")
        print(f"Frequency: {self._frequency:.2f} Hz")
        print(f"Length: {self._pipe_length:.2f} mm")


        

        if self._is_cylindrical:
            print(f"Cylindrical Pipe Dimensions:")
            print(f"Diameter of Cylindrical Pipe: {diameter_cylinder:.2f} mm")
            if not self._is_open:
                l = self._pipe_length - diameter_cylinder
            else:
                l = self._pipe_length - 2 * diameter_cylinder
            print(f"Corrected pipe Length: {l:.2f} mm")
        else:
            print(f"Width of Rectangular Pipe (Mouth Width): {self._width_rectangular:.2f} mm")
            print(f"Depth of Rectangular Pipe: {self._depth_rectangular:.2f} mm")
            if not self._is_open:
                l = self._pipe_length - self._depth_rectangular
            else:
                l = self._pipe_length - 2 * self._depth_rectangular
            print(f"Corrected pipe Length: {l:.2f} mm")
        print("")
        print(f"Mouth Width: {self._mouth_width:.2f} mm")
        print(f"Mouth Height: {self._mouth_height:.2f} mm")
        print(f"Windsheet: {self._windsheet:.4f} mm")
        print(f"Airflow: {self._airflow:.2f} mm3/sec")

    def calculate_midi_number(self):
        # Calculate MIDI number using the standard formula
        midi_number = 69 + 12 * math.log2(self._frequency / 440.0)
        return round(midi_number)

"""
if __name__ == "__main__":
    # Example usage
    organ_pipe_instance = OrganPipe(72, 0.32, 4, 17, False, 1.88, 57.2, is_cylindrical=True)
    organ_pipe_instance.midi_number = 72
      # Automatically triggers recalculation
    organ_pipe_instance.print_organ_pipe_dimensions()


"""


class OrganPipeGenerator:


    def __init__(self,
        width,
        length,
        foot_height,
        wall_thickness,
        leather_thickness,
        depth, mouth_height,
        object_spacing,label,
        frequency,
        document_unit,
        document_width,
        document_height,
        fill_canvas,
        no_ears,
		round_handle,
		handle_dia,
        pipe_number
        ):

        # self.unit_conversion =  self.convert_to(doc_unit,"1.0mm") # 3.78  Adjust this value based on your desired conversion
        self._pipe_params = {
            'width': width ,
            'length': length,
            'foot_height': foot_height,
            'wall_thickness': wall_thickness,
            'leather_thickness': leather_thickness,
            'depth': depth,
            'mouth_height': mouth_height,
            'object_spacing': object_spacing,
            'label': label,
            'frequency': frequency,
            'document_unit' : document_unit,
            'document_width': document_width,
            'document_height': document_height,
            'fill_canvas': fill_canvas,
            'No_ears': no_ears,
			'Round_tuning_handle': round_handle,
			'Handle_dia': handle_dia,
            'pipe_number': pipe_number
        }
        self.max_x_offset = 0
        self.x_offset = 0
        self.y_offset = 0
        self.document = None
        self.canvas_length =0
        self.unit_conversion = self.convert_to(self.document_unit, "1.0mm")

    @property
    def width(self):
        return self._pipe_params['width']*self.unit_conversion 

    @width.setter
    def width(self, value_mm):
        self._pipe_params['width'] = value_mm

    @property
    def length(self):
         return self._pipe_params['length'] *self.unit_conversion

    @length.setter
    def length(self, value_mm):
        self._pipe_params['length'] = value_mm 

    @property
    def foot_height(self):
        return self._pipe_params['foot_height'] *self.unit_conversion

    @foot_height.setter
    def foot_height(self, value_mm):
        self._pipe_params['foot_height'] = value_mm 

    @property
    def wall_thickness(self):
        return self._pipe_params['wall_thickness']*self.unit_conversion 

    @wall_thickness.setter
    def wall_thickness(self, value_mm):
        self._pipe_params['wall_thickness'] = value_mm 

    @property
    def leather_thickness(self):
        return self._pipe_params['leather_thickness']*self.unit_conversion 

    @leather_thickness.setter
    def leather_thickness(self, value_mm):
        self._pipe_params['leather_thickness'] = value_mm 

    @property
    def depth(self):
        return self._pipe_params['depth']*self.unit_conversion 

    @depth.setter
    def depth(self, value_mm):
        self._pipe_params['depth'] = value_mm 

    @property
    def mouth_height(self):
        return self._pipe_params['mouth_height']*self.unit_conversion 

    @mouth_height.setter
    def mouth_height(self, value_mm):
        self._pipe_params['mouth_height'] = value_mm 

    @property
    def object_spacing(self) :
        return self._pipe_params['object_spacing']*self.unit_conversion
        
    @object_spacing.setter
    def object_spacing(self,value):
          self._pipe_params['object_spacing']= value 
          
    @property
    def label(self):
        return self._pipe_params['label']

    @label.setter
    def label(self, new_label):
        self._pipe_params['label'] = new_label

    @property
    def frequency(self):
        return self._pipe_params['frequency']

    @frequency.setter
    def frequency(self, new_frequency):
        self._pipe_params['frequency'] = new_frequency
        
    @property
    def document_unit(self):
        return self._pipe_params['document_unit']

    @document_unit.setter
    def document_unit(self, new_document_unit):
        self._pipe_params['document_unit'] = new_document_unit
        self.unit_conversion = self.convert_to(self.document_unit, "1.0mm")  # Adjust this value based on your desired conversion
        #if debug is True : print(" de conversie factor is nu " , self.unit_conversion, "  naar ",self.document_unit)
       
    @property
    def fill_canvas(self):
        return self._pipe_params['fill_canvas']

    @fill_canvas.setter
    def fill_canvas(self, new_fill_canvas):
        self._pipe_params['fill_canvas'] = new_fill_canvas
 
    @property
    def No_ears(self):
        return self._pipe_params['No_ears']

    @No_ears.setter
    def No_ears(self, new_No_ears):
        
        self._pipe_params['No_ears'] = new_No_ears 
 
    @property
    def pipe_number(self):
        return self._pipe_params['pipe_number']

    @pipe_number.setter
    def pipe_number(self, new_pipe_number):
        
        self._pipe_params['pipe_number'] = new_pipe_number 

    @property
    def Round_handle(self):
        return self._pipe_params['Round_tuning_handle']

    @Round_handle.setter
    def Round_handle(self, new_Round_handle):
        self._pipe_params['Round_tuning_handle'] = new_Round_handle

    @property
    def Handle_dia(self):
        return self._pipe_params['Handle_dia']

    @Handle_dia.setter
    def Handle_dia(self, new_Handle_dia):
        self._pipe_params['Handle_dia'] = new_Handle_dia
    
    
    def set_parameters(self, **kwargs):
        for key, value in kwargs.items():
            #if debug is True : print('in set parameters   ',key,' ', value)
            setter_method = getattr(self, f'{key}', None)
            if setter_method:
                setter_method(value)
  
    def convert_to(self, target_unit, size_string):
        # Define scaling factors for supported units
        scaling_factors = {
            "px": 1.0,
            "mm": 3.7795275590551,
            "cm": 37.795275590551,
            "in": 96,
            "m": 3779.5275590551,
            "pt": 1.3333333333333,
            "pc": 16,
            "em": 16,  # Example: Customize as needed
            # Add more units and scaling factors as needed
        }

        # Extract numeric part and unit from the input string
        value, source_unit = size_string[:-2], size_string[-2:]

        # Check if the provided source_unit is in the scaling_factors dictionary
        if source_unit.lower() in scaling_factors:
            source_scaling_factor = scaling_factors[source_unit.lower()]
            # Convert to pixels
            size_in_pixels = float(value) * source_scaling_factor

            # Check if the target_unit is in the scaling_factors dictionary
            if target_unit.lower() in scaling_factors:
                target_scaling_factor = scaling_factors[target_unit.lower()]
                # Convert to the target unit
                converted_size = size_in_pixels / target_scaling_factor
                # if debug is True : print(target_unit, ' ' , size_string,' ', converted_size)
                return converted_size
            else:
                raise ValueError(f"Unsupported target unit: {target_unit}")
        else:
            raise ValueError(f"Unsupported source unit: {source_unit}")
            
    def bbox(self, x, y, xw, yw,label):
        rect_element = ET.Element('rect', {
            'x': f'{x}',
            'y': f'{y}',
            'width': f'{xw}',
            'height': f'{yw}',
            'style': 'fill:none;stroke:blue;stroke-width:0.25',
            'id': label+'bbox'  # Add an ID for identification
        })
        return rect_element

    def get_middle_x(self,tspan_element):
        # Assuming tspan_element is an lxml.ET.Element representing the <tspan> element

        # Get the text content of the tspan
        text_content = tspan_element.text

        # Create an SVG text element to measure the text width
        temp_svg = ET.Element('svg')
        temp_text = ET.SubElement(temp_svg, 'text', {'font-size': '12px'})  # Adjust font size as needed
        temp_text.text = text_content

        # Get the text bounding box
        bbox = temp_text.getbbox()

        # Calculate the middle x-coordinate
        middle_x = bbox[0] + bbox[2] / 2

        return middle_x

    def translate_path(self,path, dx, dy):
        """
        Translates the given SVG path by dx and dy, preserving relative segments.
    
        Args:
            path (str): The SVG path string.
            dx (float): The translation amount along the x-axis.
            dy (float): The translation amount along the y-axis.
    
        Returns:
            str: The translated SVG path string.
        """
        svg_path = parse_path(path)
        # Translate path
        new_path_data = svg_path.translated(complex(dx, dy))
        return new_path_data

 
        
    def translate(self, group, trans_x, trans_y):
        """
        Translate the group and its children elements by the specified translation values.

        Args:
            group: The lxml element representing the group.
            trans_x: The translation value along the x-axis.
            trans_y: The translation value along the y-axis.

        Returns:
            The modified group element.
        """
        # Translate the group itself
        if 'x' in group.attrib:
            group.attrib['x'] = str(float(group.attrib['x']) + trans_x)
        if 'y' in group.attrib:
            group.attrib['y'] = str(float(group.attrib['y']) + trans_y)

        # Translate the children elements recursively
        for child in group:
            if len(child) > 0:  # If child has children, recursively translate it
                self.translate(child, trans_x, trans_y)
            else:  # If child does not have children, translate its attributes accordingly
                if child.tag.endswith('circle') or child.tag.endswith('ellipse'):
                    # Translate circles and ellipses
                    if 'cx' in child.attrib:
                        child.attrib['cx'] = str(float(child.attrib['cx']) + trans_x)
                    if 'cy' in child.attrib:
                        child.attrib['cy'] = str(float(child.attrib['cy']) + trans_y)
                elif child.tag.endswith('text') or child.tag.endswith('use'):
                    # Translate text elements and use elements
                    if 'x' in child.attrib:
                        child.attrib['x'] = str(float(child.attrib['x']) + trans_x)
                    if 'y' in child.attrib:
                        child.attrib['y'] = str(float(child.attrib['y']) + trans_y)
                elif child.tag.endswith('path'):
                    # Translate paths
                    path = child.attrib['d']
                    #if debug is True : print(path)
                    path = self.translate_path(path, trans_x, trans_y)
                    #if debug is True : print(path)
                    #input()
                    child.attrib['d'] = path.d()
                else:
                    # Translate other elements with x and y attributes
                    if 'x' in child.attrib:
                        child.attrib['x'] = str(float(child.attrib['x']) + trans_x)
                    if 'y' in child.attrib:
                        child.attrib['y'] = str(float(child.attrib['y']) + trans_y)
        return group


    
    def create_part_group(self, parent_group, part_id, part, label_text, height, width):
        part_group = ET.SubElement(parent_group, 'g', {'id': part_id+str(self.pipe_number)})
        
        mybbox = self.bbox(self.x_offset,self.y_offset,float(width),float(height),part_id+str(self.pipe_number))
        part_group.append(part)
        part_group.append(label_text)
        part_group.append(mybbox)
        
        xnow = self.x_offset
        ynow = self.y_offset
        self.y_offset += float(height) + self.object_spacing

        # if the total height is higher then the canvas length the new group has to be moved to the next column
        
        if self.y_offset > self.canvas_length:
            #if debug is True : print(self.y_offset)
            #if debug is True : print(self.canvas_length)
            #if debug is True : print('new column')
            self.y_offset = float(height) + 2* self.object_spacing
            self.x_offset = self.max_x_offset + self.object_spacing
            self.max_x_offset = self.x_offset + float(width)
                      
            # move the group from xnow,ynow to the new column objectspacing from the top          
 
            part_group = self.translate(part_group,self.x_offset-xnow,-ynow+self.object_spacing)
        else:
            if self.x_offset + float(width) > self.max_x_offset:
                self.max_x_offset = self.x_offset + float(width)

        # TODO if self.max_x_offset > canvas_width see what to do then
        # the column where the last group is placed should move to a new canvas
        
    def create_foot_front(self, parent_group, x, y, mt, w, fh, mh):
        foot_front_group = ET.SubElement(parent_group, 'g', {'id': 'foot_front'+str(self.pipe_number)})
        if self.No_ears is False:
            path_commands = [
                f'M {x} {y}',
                f'h {2 * mt + w}',
                f'v {3 * mh + fh}',
                f'h {-mt}',
                f'v {-3 * mh}',
                f'h {-w}',
                f'v {3 * mh}',
                f'h {-mt}',
                f'v {-3 * mh - fh}',  # Adjusted to use lowercase 'v' for relative movement
                f'Z',
            ]

        else:
            path_commands = [
                f'M {x} {y}',
                f'h {2 * mt + w}',
                f'v {fh}',
                f'h {-(2*mt+w)}',
                f'v {-fh}',
                f'Z',
            ]             
        foot_front_path = ET.SubElement(foot_front_group, 'path', {
            'd': ' '.join(path_commands),
            'style': 'fill:none;stroke:red'
        })
        return foot_front_group

    def create_foot_front_seal(self, parent_group, x, y, mt, w, fh, mh):
        #if debug is True : print('No ears: ',self.No_ears)
        foot_front_seal_group = ET.SubElement(parent_group, 'g', {'id': 'foot_front_seal'+str(self.pipe_number)})
        if self.No_ears is False:
            path_commands = [
                f'M {x} {y}',
                f'h {2 * mt + w}',
                f'v {3 * mh + fh}',
                f'h {-mt}',
                f'v {-(3 * mh + (fh-3*mt))}',
                f'h {-w}',
                f'v {(3 * mh + (fh-3*mt))}',
                f'h {-mt}',
                f'v {-3*mh-fh}',
                f'Z',
            ]
        else :
            path_commands = [
                f'M {x} {y}',
                f'h {2 * mt + w}',
                f'v {fh}',
                f'h {-mt}',
                f'v {-(fh-3*mt)}',
                f'h {-w}',
                f'v {(fh-3*mt)}',
                f'h {-mt}',
                f'v {-fh}',
                f'Z',
            ]           
        foot_front_seal_path = ET.SubElement(foot_front_seal_group, 'path', {
            'd': ' '.join(path_commands),
            'style': 'fill:none;stroke:green'
        })
        return foot_front_seal_group




    def create_tuning_handle(self, parent_group, x, y, mt):
        tuning_handle_group = ET.SubElement(parent_group, 'g', {'id': 'tuning_handle'+str(self.pipe_number)})
        path_commands = [f'M {x + 2*mt} {y}',f'h {2 * mt}',f'v {10 + 3 * mt}',f'l {mt} {mt}',f'v {mt}',f'h {-4 * mt}',f'v{-mt}',f'l {mt} {-mt}',f'v {-5 * mt}',f'Z',]
        tuning_handle = ET.SubElement(tuning_handle_group, 'path', {
            'd': ' '.join(path_commands),
            'style': 'fill:none;stroke:red'
        })
        return tuning_handle_group

    def create_stopper_group(self, parent_group, x, y, width, depth, mt,lt,radius):
        stopper_group = ET.SubElement(parent_group, 'g', {'id': 'stopper_group'+str(self.pipe_number)})
        outer_width = width-2*lt
        outer_height = depth-2*lt
        outer_rect = ET.SubElement(stopper_group, 'rect', {
            'x': str(x),
            'y': str(y),
            'width': str(outer_width),
            'height': str(outer_height),
            'style': 'fill:none;stroke:red',
            'rx': str(radius),
            'ry': str(radius)
        })
        inner_width = 2 * mt
        inner_height = 2 * mt
        inner_rect = ET.SubElement(stopper_group, 'rect', {
            'x': str(x + (outer_width - inner_width) / 2),
            'y': str(y + (outer_height - inner_height) / 2),
            'width': str(inner_width),
            'height': str(inner_height),
            'style': 'fill:none;stroke:red'
        })
        return stopper_group

    def create_footblock_group(self, parent_group, x, y, width, depth, diameter, delta_y):
        footblock_group = ET.SubElement(parent_group, 'g', {'id': 'footblock_group'+str(self.pipe_number)})
        rectangle = ET.SubElement(footblock_group, 'rect', {
            'x': str(x),
            'y': str(y),
            'width': str(width),
            'height': str(depth),
            'style': 'fill:none;stroke:red'
        })
        circle_x = x + width / 2
        circle_y = y + delta_y + diameter / 2
        circle = ET.SubElement(footblock_group, 'circle', {
            'cx': str(circle_x),
            'cy': str(circle_y),
            'r': str(diameter / 2),
            'style': 'fill:none;stroke:red'
        })
        return footblock_group

    def create_part(self, parent_group, breedte, lengte, naam, shape=None):
        mypart = shape if shape is not None else ET.SubElement(parent_group, 'rect', {
            'x': str(self.x_offset),
            'y': str(self.y_offset),
            'width': breedte,
            'height': lengte,
            'style': 'fill:none;stroke:red'
        })
        part_label_text = ET.Element('text', {
            'x': str(self.x_offset + 3),
            'y': str(self.y_offset),
            'font-size': '5px',
            'fill': 'black',
            'stroke':'black'
        })
        label_lines=[]
        if len(naam) > 1 :
            part_label_text.set('style', 'font-size:5px; fill: black')
            label_lines = [
                f'{self.label}', f'{naam}',
                f'{self.frequency}',
            ]
        else:
            part_label_text.set('style', 'font-size:5px; fill: black')
            label_lines = [
                f'{naam}',
            ]        
        for i, line in enumerate(label_lines):
            tspan = ET.Element('tspan', {'x': str(self.x_offset + float(breedte)/2), 'dy': str(5)+"px",'text-anchor': 'middle'})
            tspan.text = line
            tspan.set('fill', 'black')
            tspan.set('style', 'fill: black')
            part_label_text.append(tspan)
        
        #print(self.get_middle_x(tspan))
        #print(naam)
        #print(self.y_offset)
        #print(lengte)
        #print(self.frequency)
        self.create_part_group(parent_group, naam, mypart, part_label_text, lengte, breedte)


    # here the magic happens

    def generate_svg(self, canvas_width= 210 , canvas_length = 297, units = "mm",file_path="",pipe_number=1):
        self.document_unit = units
        self.pipe_number=pipe_number
        if debug is True : print('in generate ',canvas_width, ' ',canvas_length,' ',units,' ',file_path,'No_ears: ',self.No_ears)
        if debug is True : print(self.pipe_number)
        # there is a document if there are more then one pipe to draw or if we run as inkscape extension
        
        if self.document is not None:
            print('There is a document')
            root = self.document.getroot ()
            
            # Check if 'organ_pipes' group already exists
            
            organ_pipes_layer = root.find(".//g[@id='organ_pipes']")

            # If 'organ_pipes' group doesn't exist, create it
            if organ_pipes_layer is None:
                organ_pipes_layer = ET.SubElement(root, 'g', {'id': 'organ_pipes'})

        else:
            print('There is no document')
            root = ET.Element('svg', {'xmlns': 'http://www.w3.org/2000/svg', 'version': '1.1', 'style': 'stroke-width:0.2', 'font-size': '6',
                          'width': f'{canvas_width}{self.document_unit}', 'height': f'{canvas_length}{self.document_unit}'})
            root.set('viewBox', f'0 0 {canvas_width} {canvas_length}')
            
            # Create a new ElementTree object with the root element
            self.document = ET.ElementTree(root)
            organ_pipes_layer = ET.SubElement(root, 'g', {'id': 'organ_pipes'})

            self.x_offset = self.object_spacing
            self.y_offset = self.object_spacing
            self.max_x_offset = 0
        
        if 'width' in root.attrib and 'height' in root.attrib:
                #self._canvas_width = float(self.convert_to(self.document_unit,root.attrib['width']))
                #self._canvas_height = float(self.convert_to(self.document_unit,root.attrib['height']))
                #if debug is True : print(f"Canvas Height: {root.attrib['height']}")  # if debug is True : print canvas height

                #if debug is True : print(self.canvas_length)
                #if debug is True : print({root.attrib['viewBox']})

                self.canvas_length = self.convert_to(self.document_unit,root.attrib['height'])
                #if debug is True : print('canvas_length  ',self.canvas_length )
                #if self.length > self.canvas_length :
                  #print ('the canvas length ', {self.canvas_length} ,' is to small for this pipe ', self.length)
                  #return
        
        print('creeer pipe: ',pipe_number)
        pipe_group = ET.SubElement(organ_pipes_layer, 'g', {'id': f'pipe'+ str(pipe_number)})

        #create_footblock_group(self, parent_group, x, y, width, depth, diameter, delta_y) diameter is the foot hole. 
        
        for i in range(3):
            my_shape = self.create_footblock_group(pipe_group, 
            self.x_offset, self.y_offset,
            self.width, self.depth, 
            6*self.unit_conversion, 
            2*self.unit_conversion)
            
            self.create_part(
            pipe_group,
            str(self.width),
            str(self.depth), 
            'fb c '+ str(i),
            shape=my_shape)

        for i in range(3):
            self.create_part(
            pipe_group,
            str(self.width), 
            str(self.depth),
            'fb'+str(i),
            shape=None)
            
        self.create_part(
            pipe_group,
            str(self.width),
            str(self.foot_height),
            'fbb',
            shape=None)    
            
        # labium
        
        if self.No_ears is False:
            self.create_part(pipe_group,str(self.width),str(5*self.mouth_height),'lab',shape=None)
        else:
            self.create_part(pipe_group,str(self.width+self.wall_thickness*2),str(5*self.mouth_height),'lab',shape=None)        
        
        # front
        
        self.create_part(pipe_group, str(self.width),
                              str(self.length  - 2 * self.mouth_height),
                              'frt', shape=None)

        
        
        # stopper
        
        for i in range(5):  # create stopper parts
            my_shape = self.create_stopper_group(pipe_group, self.x_offset, self.y_offset,
                                                 self.width,
                                                 self.depth, self.wall_thickness,self.leather_thickness,0)
            self.create_part(pipe_group, self.width-2*self.leather_thickness, self.depth-2*self.leather_thickness, 'stp' + str(i),
                                  shape=my_shape)

        # voicing handle
        
        for i in range(2):  # Create the tuning_handle of the pipe
            my_shape = self.create_tuning_handle(
              pipe_group, 
              self.x_offset, 
              self.y_offset,
              self.wall_thickness)
            
            self.create_part(
            pipe_group,
            str(self.wall_thickness *6),
            str(10 + self.wall_thickness *5),
            'TH ' +str(i),
            shape=my_shape)


        # sides
        
        self.create_part(pipe_group, str(self.depth + 2 * self.wall_thickness),
                              str(self.length+self.foot_height), 'S1', shape=None)

        self.create_part(pipe_group, str(self.depth + 2 * self.wall_thickness),
                              str(self.length+self.foot_height), 'S2', shape=None)

        # backside
        
        self.create_part(pipe_group, str(self.width),
                              str(self.length+self.foot_height), 'Bck', shape=None)

        #foot front
        
        my_shape = self.create_foot_front(pipe_group, self.x_offset, self.y_offset,
                                          self.wall_thickness,
                                          self.width, self.foot_height,
                                          self.mouth_height)

        if self.No_ears is False:    
            self.create_part(pipe_group,
                                  str(self.width + self.wall_thickness * 2),
                                  str(self.foot_height + self.mouth_height * 3), 'ft_f',
                                  shape=my_shape)
        else:
            self.create_part(pipe_group,
                                  str(self.width + self.wall_thickness * 2),
                                  str(self.foot_height ), 'ft_f',
                                  shape=my_shape)        
        
        #rig
        
        for i in range(6):  # create Rig parts
            my_shape = self.create_stopper_group(pipe_group, self.x_offset, self.y_offset,
                                                 self.width,
                                                 self.depth, self.wall_thickness,0,4)
            self.create_part(pipe_group, self.width, self.depth, 'rig' + str(i),
                                  shape=my_shape)
        
        # rig connector
        
        for i in range(2):  # create Rig connector parts
                    self.create_part(pipe_group, str( 2 * self.wall_thickness),
                              str(self.length+self.foot_height),  str(i), shape=None)

       #foot front seal
        
        my_shape = self.create_foot_front_seal(pipe_group, self.x_offset, self.y_offset,
                                          self.wall_thickness,
                                          self.width, self.foot_height,
                                          self.mouth_height)
        if self.No_ears is False:
            self.create_part(pipe_group,
                                  str(self.width + self.wall_thickness * 2),
                                  str(self.foot_height + self.mouth_height * 3), 'ft_fs',
                                  shape=my_shape)
        else:
            self.create_part(pipe_group,
                                  str(self.width + self.wall_thickness * 2),
                                  str(self.foot_height ), 'ft_fs',
                                  shape=my_shape)
                                  
        
        # stop or continue on same document

        if self.fill_canvas is False:
            if debug is True : print('hier wordt de file gesloten') 
            file_name = file_path + f'\organ_pipes_{self.label.replace(" ", "_").lower()}.svg'
            self.document = ET.ElementTree(root)
            
            tree = self.document
            root = tree.getroot()

            # Create an instance of the RectanglePacker
            rect_packer = RectanglePacker(canvas_width=600, canvas_height=600)

            # Pack the rectangles
            packed_roots = rect_packer.pack_rectangles(root)

            # Save the packed rectangles as separate SVG files
            rect_packer.save_svg_files(packed_roots, file_path)
            
            with open(file_name, 'wb') as file:           
                self.document.write(file, pretty_print=True)
            self.document = None  # Explicitly delete the tree object to free resources
        else :
            # continue in same document
            pass
""""
if __name__ == "__main__":
    generator = OrganPipeGenerator(width=16, length=32
    , foot_height=50, wall_thickness=3.6, depth=35, mouth_height=9,object_spacing = 5,
                                   label='P_1', frequency=440.0)
    generator.generate_svg( canvas_width=1600,canvas_length=1600, units="px") # Generates SVG for Pipe_1
    print(' ')
    print(generator.width)
    print(' ')


    generator.width = 25
    generator.length = 150
    generator.foot_height = 50
    generator.label = 'P_2'
    generator.frequency = 600
    
    
                                               h
    
    generator.generate_svg(units="cm")  # Generates SVG for Pipe_2
    print(generator.length)
    print(generator._pipe_params['length'] )

"""






import tkinter as tk
from tkinter import scrolledtext, filedialog
import sys
import os

class TextRedirector:
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass

import tkinter as tk
from tkinter import scrolledtext, filedialog
import sys
import os

class TextRedirector:
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass

class OrganPipeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Organ Pipe Parameters")

        # Default parameter values
        self.default_values = {
            'midi_numbers_comma_separated': '70',
            'width_fraction_0_x_1': '0.25',
            'semitone_deviation': '10',
            'halving_speed': '17',
            'is_open': 'False',
            'ising_number': '2.5',
            'wind_pressure_mm_h2o': '110',
            'is_cylindrical': 'False',
            'foot_height': '30',
            'wall_thickness': '2.75',
            'leather_thickness': '0.5',
            'object_spacing': '5',
            'document_unit': 'mm',
            'document_width_mm': '210',
            'document_height_mm': '297',
            'directory_path': os.path.join(os.path.expanduser("~"), "Documents"),
            'fill_canvas': 'False',
            'no_ears': 'False',
            'round_tuning_handle': 'False',
            'handle_dia_mm': '6'
        }

        # Initialize a grid with 10 columns and 40 rows
        for i in range(40):
            self.master.grid_rowconfigure(i, minsize=20)
        for j in range(10):
            self.master.grid_columnconfigure(j, minsize=80)

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

        self.entry_values = {}
        self.checkboxes = {}
        row_counter = 0

        self.entry_values = {}
        row_counter = 0
        for i, label_text in enumerate(self.labels):
            key = label_text.lower().replace(' ', '_').replace('(', '').replace(')', '').replace(':', '').replace('<', '').replace('>', '').replace(',', '').replace('-', '_')
            # Correcting the specific issue with extra underscores
            key = key.replace('__x__', '_x_')  # Handle specific replacement case
            print(f"Label: {label_text} -> Key: {key}")  # Debug print
            if label_text not in ["Is Open:", "Is Cylindrical:", "Fill Canvas:", "No ears:","Round tuning handle:","Handle dia (mm):"]:
                tk.Label(master, text=label_text).grid(row=row_counter, column=0, sticky='w')
                entry = tk.Entry(master, width=50)
                entry.grid(row=row_counter, column=1, columnspan=3, sticky='w')
                default_value = self.default_values.get(key, '')
                print(f"Default value for {key}: {default_value}")  # Debug print
                entry.insert(tk.END, default_value)
                self.entry_values[key] = entry
                row_counter += 1

        # Directory chooser button
        self.choose_directory_button = tk.Button(master, text="Choose Directory", command=self.choose_directory)
        self.choose_directory_button.grid(row=row_counter, column=1, columnspan=2, sticky='w')
        row_counter += 1

        # Checkboxes
        self.checkboxes = {}
        checkbox_labels = ["Is Open:", "Is Cylindrical:", "Fill Canvas:", "No ears:"]
        checkbox_keys = ["is_open", "is_cylindrical", "fill_canvas", "no_ears"]

        for i, (label_text, key) in enumerate(zip(checkbox_labels, checkbox_keys)):
            var = tk.BooleanVar()
            default_value = self.default_values.get(key, 'False')
            var.set(default_value.lower() == 'true')
            checkbox = tk.Checkbutton(master, text=label_text, variable=var)
            checkbox.grid(row=row_counter + i, column=0, sticky='w')
            self.checkboxes[key] = var

        row_counter += len(checkbox_labels)

        # "Round tuning handle:" Checkbox and diameter input
        self.handlerow = row_counter
        var = tk.BooleanVar()
        default_value = self.default_values.get("round_tuning_handle", 'False')
        var.set(default_value.lower() == 'true')
        checkbox = tk.Checkbutton(master, text="Round tuning handle:", variable=var, command=self.toggle_handle_dia_entry)
        checkbox.grid(row=self.handlerow, column=0, sticky='w')
        self.checkboxes["round_tuning_handle"] = var
        self.handle_dia_label = tk.Label(master, text="Handle dia (mm):")
        self.handle_dia_entry = tk.Entry(master, width=20)
        self.handle_dia_label.grid(row=self.handlerow, column=1, sticky='w')
        self.handle_dia_entry.grid(row=self.handlerow, column=2, sticky='w')
        self.toggle_handle_dia_entry()  # Initial toggle to hide if unchecked

        row_counter += 1

        # Button
        self.button = tk.Button(master, text="Create Organ Pipe", command=self.create_organ_pipe)
        self.button.grid(row=row_counter, column=0, columnspan=2, sticky='w')

        # Message field with scrollbars
        self.message_field = scrolledtext.ScrolledText(master, height=10, width=50)
        self.message_field.grid(row=24, column=0, columnspan=10)

        # Redirect stdout to the message field
        sys.stdout = TextRedirector(self.message_field, "stdout")

    def toggle_handle_dia_entry(self):
        if self.checkboxes["round_tuning_handle"].get():
            self.handle_dia_label.grid()
            self.handle_dia_entry.grid()
            self.handle_dia_entry.delete(0, tk.END)
            self.handle_dia_entry.insert(tk.END, self.default_values.get("handle_dia_mm", ''))
        else:
            self.handle_dia_label.grid_remove()
            self.handle_dia_entry.grid_remove()

    def choose_directory(self):
        directory = filedialog.askdirectory()
        self.entry_values["directory_path"].delete(0, tk.END)
        self.entry_values["directory_path"].insert(0, directory)


    def create_organ_pipe(self):
        # Clear the message field
        self.message_field.delete('1.0', tk.END)
        
        # Retrieve values from entry fields
        parameters = {key: entry.get() for key, entry in self.entry_values.items()}
        parameters.update({key: var.get() for key, var in self.checkboxes.items()})

        # Convert values to appropriate types
        parameters['midi_numbers'] = [int(num.strip()) for num in parameters['midi_numbers_comma_separated'].split(',')]
        parameters['width_fraction'] = float(parameters['width_fraction_0_x_1'])
        parameters['semitone_deviation'] = int(parameters['semitone_deviation'])
        parameters['halving_speed'] = int(parameters['halving_speed'])
        parameters['is_open'] = parameters['is_open']
        parameters['ising_number'] = float(parameters['ising_number'])
        parameters['wind_pressure'] = float(parameters['wind_pressure_mm_h2o'])
        parameters['is_cylindrical'] = parameters['is_cylindrical']
        parameters['foot_height'] = float(parameters['foot_height'])
        parameters['wall_thickness'] = float(parameters['wall_thickness'])
        parameters['leather_thickness'] = float(parameters['leather_thickness'])
        parameters['object_spacing'] = float(parameters['object_spacing'])
        parameters['document_unit'] = parameters['document_unit']
        parameters['document_width'] = float(parameters['document_width_mm'])
        parameters['document_height'] = float(parameters['document_height_mm'])
        parameters['directory_path'] = parameters['directory_path']
        parameters['fill_canvas'] = parameters['fill_canvas']
        parameters['no_ears'] = parameters['no_ears']
        parameters['round_tuning_handle'] = parameters['round_tuning_handle']
        if parameters['round_tuning_handle']:
            parameters['handle_dia_mm'] = float(parameters.get('Handle dia (mm):', 0))
        else:
            parameters['handle_dia_mm'] = 0

        # Print parameters to the message field for debugging
        print(parameters)

        # Create OrganPipeGenerator object
        opg = OrganPipeGenerator(
            width=0,  # Example value
            length=0,  # Example value
            foot_height=parameters['foot_height'],
            wall_thickness=parameters['wall_thickness'],
            leather_thickness=parameters['leather_thickness'],
            depth=0,  # Example value
            mouth_height=0,  # Example value
            label='',  # Example value
            frequency=0,  # Example value
            object_spacing=parameters['object_spacing'],
            document_unit=parameters['document_unit'],
            document_width=parameters['document_width'],
            document_height=parameters['document_height'],
            fill_canvas=parameters['fill_canvas'],
            no_ears=parameters['no_ears'],
			round_handle=parameters['round_tuning_handle'],
			handle_dia=parameters['handle_dia_mm'],
            pipe_number=1
        )

        i = 0
        for midi_number in parameters['midi_numbers']:
            i += 1
            organ_pipe = OrganPipe(
                midi_number,
                parameters['width_fraction'],
                parameters['semitone_deviation'],
                parameters['halving_speed'],
                parameters['is_open'],
                parameters['ising_number'],
                parameters['wind_pressure'],
                parameters['is_cylindrical']
            )
            organ_pipe.calculate_organ_pipe_dimensions()
            organ_pipe.print_organ_pipe_dimensions()

            # Call OrganPipeGenerator here
            opg.width = organ_pipe.width_rectangular
            opg.length = organ_pipe.pipe_length
            opg.depth = organ_pipe.depth_rectangular
            opg.mouth_height = organ_pipe.mouth_height
            opg.label = 'm' + str(organ_pipe._midi_number)
            opg.frequency = int(organ_pipe.frequency)
            opg.fill_canvas = parameters['fill_canvas']
            opg.no_ears = parameters['no_ears']

            if i == len(parameters['midi_numbers']):
                opg.fill_canvas = False
                print(i)

            # Generate SVG
            opg.generate_svg(
                parameters['document_width'],
                parameters['document_height'],
                parameters['document_unit'],
                parameters['directory_path'],
                i
            )
            self.message_field.insert(tk.END, "Organ pipe created successfully!\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganPipeGUI(master=root)
    root.mainloop()




# TextRedirector class to redirect stdout to a Text widget
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)  # Scroll to the end of the text

    def flush(self):
        pass  # Do nothing

# Create an instance of Tkinter's Tk class
root = tk.Tk()
# Create an instance of OrganPipeGUI class
organ_pipe_gui = OrganPipeGUI(root)
# Start the Tkinter event loop
root.mainloop()