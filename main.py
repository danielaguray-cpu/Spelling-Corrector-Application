from input_reader import InputReader
from output_writer import OutputWriter
from processor import Processor

def main():
    reader = InputReader()
    writer = OutputWriter()
    processor = Processor()

    try:
        text = reader.read_text()
        corrected, feedback = processor.process_text(text)
        writer.display(corrected, feedback)
        writer.export_report("report.txt", feedback)
    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
