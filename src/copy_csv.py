import csv

def copy_csv(input_file, output_file):
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            writer.writerow(row)

if __name__ == "__main__":
    input_file = '../../data/data.csv'
    fileName ='winrate_Expert.csv'
    output_file = '../../data/'+fileName
    copy_csv(input_file, output_file)
    print("Data copied successfully from 'data.csv' to "+fileName )
