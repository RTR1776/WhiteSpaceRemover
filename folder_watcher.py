import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import docx
import logging  # Import the logging module

# --- Setup logging ---
logging.basicConfig(filename='folder_watcher.log', level=logging.INFO,  # Log to 'folder_watcher.log' file
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Script started") # Log script start

def remove_blank_lines(input_filepath, output_filepath):
    """Removes blank lines from a text file and saves the output to a new file."""
    logging.info(f"Processing file: {input_filepath}") # Log file processing start
    try:
        if input_filepath.lower().endswith('.txt'):
            with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
                for line in infile:
                    if line.strip():
                        outfile.write(line)
            logging.info(f"Successfully processed TXT file: {output_filepath}") # Log success
            return True
        elif input_filepath.lower().endswith('.doc') or input_filepath.lower().endswith('.docx'):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    doc = docx.Document(input_filepath)
                    cleaned_text = []
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            cleaned_text.append(paragraph.text)
                    with open(output_filepath, 'w', encoding='utf-8') as outfile:  # Save docx content as txt
                        outfile.write('\n'.join(cleaned_text))
                    logging.info(f"Successfully processed DOC/DOCX file: {output_filepath}") # Log success
                    return True
                except Exception as e:
                    logging.error(f"Error processing doc/docx file on attempt {attempt+1}: {input_filepath} - {e}") # Log docx error
                    time.sleep(2)  # Wait for 2 seconds before retrying
            return False
        else:
            logging.warning(f"Unsupported file type: {input_filepath}. Only .txt, .doc, and .docx files are supported.") # Log unsupported type
            return False
    except Exception as e:
        logging.error(f"Error processing file: {input_filepath} - {e}") # Log general error
        return False

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return None

        filepath = event.src_path
        if filepath.lower().endswith(('.txt', '.doc', '.docx')):
            logging.info(f"File created event detected: {filepath}") # Log file creation detection
            filename = os.path.basename(filepath)
            output_filepath = os.path.join(self.output_folder, f"cleaned_{filename}.txt") # Output as .txt for simplicity
            if remove_blank_lines(filepath, output_filepath):
                logging.info(f"Processed and saved: {output_filepath}") # Log processing and save success
            else:
                logging.error(f"Processing failed for: {filepath}") # Log processing failure

if __name__ == "__main__":
    input_folder = "input_folder"  #  <---  SET YOUR INPUT FOLDER HERE
    output_folder = "output_folder" #  <---  SET YOUR OUTPUT FOLDER HERE

    # Create input and output folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    event_handler = FileEventHandler(input_folder, output_folder)
    observer = Observer()
    observer.schedule(event_handler, input_folder, recursive=False)
    observer.start()
    logging.info(f"Watching for new files in folder: {input_folder}") # Log folder watching start

    try:
        while True:
            time.sleep(1) # Keep the script running and watching
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Script stopped") # Log script stop