import os
import subprocess

def process_garmin_files(root_folder="garmin_data", extension=".gmn"):
    """
    Loops through all .gmn files within garmin_data/*.gmn and calls
    garmin_dumps on each file and writes the output to a .xml
    file within garmin_data/xml/ as an *.xml file with the same name

    Args:
        root_folder (str): The starting directory to search from.
        extension (str): The file extension to look for (e.g., ".gmn", ".txt").
                         Case-insensitive check is performed.
    """
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(extension.lower()):
                full_file_path = os.path.join(dirpath, filename)
                base_filename = os.path.basename(full_file_path)
                process = subprocess.run(f'garmin_dump {full_file_path}', shell=True, check=True, text=True, capture_output=True)
                if process.stdout:
                    new_filename = base_filename[:-4]
                    new_filepath = f"xml/{new_filename}.xml"
                    if os.path.exists(new_filepath):
                        print(f'PASSING {new_filepath}; file already exists...')
                    else:
                        with open(new_filepath, "w") as outfile:
                            outfile.write(process.stdout)

if __name__ == "__main__":
    process_garmin_files(root_folder="garmin_data", extension=".gmn")
