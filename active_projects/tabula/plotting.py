import matplotlib.pyplot as plt
import csv
import numpy as np

with open('data.txt') as csvfile:
	str_data = list(csv.reader(csvfile, delimiter = ' '))


data = []
for raw_row in str_data:
	row = []
	for raw_entry in raw_row:
		entry = float(raw_entry)
		row.append(entry)
	data.append(row)

data = np.array(data).T

plt.plot(data[0], data[1])
plt.show()