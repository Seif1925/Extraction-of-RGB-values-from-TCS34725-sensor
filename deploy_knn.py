from sensor_read import TCS34725
import joblib
import numpy as np
import time

class ColorAI:
    def __init__(self):
        self.sensor = TCS34725()
        self.model = joblib.load('models/color_knn_model.joblib')
        
    def normalize_rgbc(self, r, g, b, c):
        return [r/c, g/c, b/c] if c > 0 else [0, 0, 0]
    
    def run(self):
        try:
            while True:
                start = time.time()
                r, g, b, c = self.sensor.read_raw()
                features = self.normalize_rgbc(r, g, b, c)
                predicted = self.model.predict([features])[0]
                r, g, b = np.clip(predicted, 0, 255).astype(int)
                
                # Terminal color display (works on most Linux terminals)
                print(f"\033[48;2;{r};{g};{b}m        \033[0m "
                      f"RGB: {r:3d} {g:3d} {b:3d} | "
                      f"Latency: {(time.time()-start)*1000:.1f}ms")
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    ai = ColorAI()
    ai.run()