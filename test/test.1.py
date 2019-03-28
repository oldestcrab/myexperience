import csv

a = '11-BETA-HSD3,100174880,"Anemia, Hemolytic",MESH:D000743,,"Water Pollutants, Chemical",4.49,,22425172'
b = [a]
reader = csv.reader(b, delimiter=',')
for row in reader:
    print(len(row))
    print(row)


