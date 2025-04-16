from sensor_read import TCS34725
import csv
import time

sensor = TCS34725()

with open('data/color_dataset.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['R', 'G', 'B', 'C', 'True_R', 'True_G', 'True_B'])
    
    try:
        while True:
            r, g, b, c = sensor.read_raw()
            print(f"\nCurrent Reading: R={r}, G={g}, B={b}, C={c}")
            
            true_r = int(input("True R (0-255): "))
            true_g = int(input("True G (0-255): "))
            true_b = int(input("True B (0-255): "))
            
            writer.writerow([r, g, b, c, true_r, true_g, true_b])
            print("Entry saved!")
            
    except KeyboardInterrupt:
        print("\nData collection complete.")