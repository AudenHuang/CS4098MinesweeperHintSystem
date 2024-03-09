import csv

def copy_csv(input_file, output_file):
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            writer.writerow(row)

if __name__ == "__main__":
    input_file = '../../test/data.csv'
    output_file = '../../test/smart_output.csv'
    copy_csv(input_file, output_file)
    print("Data copied successfully from 'data.csv' to 'smart_output.csv'")
