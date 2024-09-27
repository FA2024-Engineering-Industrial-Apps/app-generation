import os

class FileCopier:
    def __init__(self, src_folder: str = "/template_files/"):
        """
        Initialize the FileCopier class with the folder where source files are located.

        :param src_folder: Path to the folder containing the source files.
        """
        self.src_folder = src_folder

    def copy_and_insert(self, src_filename: str, dest_file: str, replacements: dict = dict()):
        """
        Copies a file from the source folder to the destination file and replaces placeholders.

        :param src_filename: Name of the source file located in the src_folder.
        :param dest_file: Path to the destination file.
        :param replacements: Dictionary where the keys are placeholders in the form of {{key}} 
                             and the values are the strings to replace them with.
        """
        src_file = os.path.join(self.src_folder, src_filename)

        try:
            # Read the content of the source file
            with open(src_file, 'r') as f:
                content = f.read()

            # Replace the placeholders with corresponding user input
            for placeholder, replacement in replacements.items():
                content = content.replace(f"{{{{{placeholder}}}}}", replacement)

            # Write the modified content to the destination file
            with open(dest_file, 'w') as f:
                f.write(content)

        except FileNotFoundError:
            print(f"Error: The file '{src_file}' was not found in the folder '{self.src_folder}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    copier = FileCopier()
    copier.copy_and_insert("Dockerfile", "output.txt", {})