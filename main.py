"""
TODO this is a first draft of logic to read a .xml file
created via garmin_dump and begin converting into python
datatypes to permit for downstream processing


Downstream processing steps:
- Convert to suitable datatypes for database storage
- Store within database if the specific file has not already been
processed
"""
import xml.etree.ElementTree as ET

def parse_activity_data(filepath):
    """
    Parses an activity data file with XML-like lines.

    Args:
        filepath (str): The path to the text file.

    Returns:
        dict: A dictionary containing parsed data, structured by element type.
              Returns None if the file cannot be opened or parsed.
    """
    data = {
        'runs': [],
        'laps': [],
        'tracks': [],
        'points': []
    }

    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                try:
                    # Parse the line as an XML element
                    element = ET.fromstring(line)
                    
                    # Extract tag and attributes
                    tag = element.tag
                    attributes = element.attrib

                    # Collect data based on the tag
                    if tag == 'run':
                        data['runs'].append(attributes)
                    elif tag == 'lap':
                        lap_data = attributes
                        # Iterate over child elements for nested data
                        for child in element:
                            if child.tag in ['begin_pos', 'end_pos']:
                                lap_data[child.tag] = child.attrib
                            else:
                                lap_data[child.tag] = child.text.strip() if child.text else None
                        data['laps'].append(lap_data)
                    elif tag == 'track':
                        data['tracks'].append(attributes)
                    elif tag == 'point':
                        point_data = attributes
                        # Convert specific point attributes to float for easier use
                        for key in ['lat', 'lon', 'alt', 'distance']:
                            if key in point_data:
                                try:
                                    point_data[key] = float(point_data[key])
                                except ValueError:
                                    pass # Keep as string if conversion fails
                        data['points'].append(point_data)
                    else:
                        print(f"Warning: Unknown tag '{tag}' found on line {line_num}. Attributes: {attributes}")

                except ET.ParseError as e:
                    print(f"Error parsing XML on line {line_num}: '{line}' - {e}")
                except Exception as e:
                    print(f"An unexpected error occurred on line {line_num}: {e}")

        return data

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while opening the file: {e}")
        return None
