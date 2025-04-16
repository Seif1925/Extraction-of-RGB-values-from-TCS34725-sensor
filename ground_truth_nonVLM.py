import cv2
import time
import threading
import numpy as np
from collections import deque
import webcolors
class OptimizedCameraRGB:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")
        # Camera setup
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        # ROI polygon (quadrilateral coordinates)
        self.roi_polygon = [(200, 120), (225, 120), (225, 170), (200, 170)]
        # Analysis parameters
        self.fps_queue = deque(maxlen=10)
        self.last_processed_time = time.time()
        self.latest_response = ""
        self.analysis_active = False
        cv2.namedWindow('OptiCam')
    def crop_roi(self, frame):
        """Crops and masks the ROI defined by the polygon"""
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(self.roi_polygon, np.int32)], 255)
        cropped = cv2.bitwise_and(frame, frame, mask=mask)
        x, y, w, h = cv2.boundingRect(np.array(self.roi_polygon, np.int32))
        return cropped[y:y+h, x:x+w]
    def get_color_stats(self, frame):
        """Calculates average RGB and standard deviation"""
        roi = self.crop_roi(frame)
        if roi.size == 0:
            return (0, 0, 0), (0, 0, 0)
        avg_rgb = np.flip(np.mean(roi, axis=(0, 1)), axis=0)  # Explicitly specify axis=0
        std_rgb = np.flip(np.std(roi, axis=(0, 1)), axis=0)   # Explicitly specify axis=0
        return avg_rgb.astype(int), std_rgb.astype(int)

    def analyze_colors(self, avg_rgb, std_rgb):
        """Local color analysis replacing VLM API call"""
        try:
            # Get closest color name
            color_name = self.get_closest_color(avg_rgb)
            # Determine uniformity
            uniform = all(s < 10 for s in std_rgb)  # Adjust threshold as needed
            # Build response
            response = f"1. Detected Color: {color_name}\n"
            response += f"2. Color Uniformity: {'High' if uniform else 'Low'}\n"
            response += "3. Potential Non-uniformity Causes:\n"
            response += "   - Lighting variations\n   - Object movement\n   - Sensor noise" if not uniform else "   - None detected"
            return response
        except Exception as e:
            return f"Analysis error: {str(e)}"
    def get_closest_color(self, rgb):
        """Finds the closest CSS3 color name for RGB values"""
        try:
            return webcolors.rgb_to_name(rgb)
        except ValueError:
            min_colors = {}
            for hex, name in webcolors.CSS3_HEX_TO_NAMES.items():
                r_c, g_c, b_c = webcolors.hex_to_rgb(hex)
                rd = (r_c - rgb[0]) ** 2
                gd = (g_c - rgb[1]) ** 2
                bd = (b_c - rgb[2]) ** 2
                min_colors[rd + gd + bd] = name
            return min_colors[min(min_colors.keys())]
    def analyze_with_vlm(self, frame, avg_rgb, std_rgb):
        """Handles analysis in a thread"""
        if self.analysis_active:
            return
        self.analysis_active = True
        threading.Thread(target=self._async_vlm_analysis, args=(avg_rgb, std_rgb)).start()
    def _async_vlm_analysis(self, avg_rgb, std_rgb):
        """Async analysis handler"""
        try:
            self.latest_response = self.analyze_colors(avg_rgb, std_rgb)
            self.save_analysis_report(avg_rgb, std_rgb, self.latest_response)
        finally:
            self.analysis_active = False
    def save_analysis_report(self, avg_rgb, std_rgb, response):
        """Saves analysis results to file"""
        with open("color_analysis.txt", "a") as f:
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write(f"Average RGB: {avg_rgb}\n")
            f.write(f"Standard Deviations: {std_rgb}\n")
            f.write(f"Analysis:\n{response}\n")
            f.write("-"*50 + "\n")
    def run(self):
        while True:
            start_time = time.perf_counter()
            ret, frame = self.cap.read()
            if not ret:
                break
            # Get color statistics
            avg_rgb, std_rgb = self.get_color_stats(frame)
            # Calculate FPS
            self.fps_queue.append(1 / (time.perf_counter() - start_time))
            fps = sum(self.fps_queue)/len(self.fps_queue)
            # Draw ROI polygon
            cv2.polylines(frame, [np.array(self.roi_polygon, np.int32)], True, (0, 255, 0), 2)
            # Display info
            cv2.putText(frame, f"Avg RGB: {avg_rgb}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            cv2.putText(frame, f"Std Dev: {std_rgb}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            # Show latest analysis
            if self.latest_response:
                y_start = 120
                for line in self.latest_response.split('\n')[:4]:
                    cv2.putText(frame, line, (10, y_start),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y_start += 20
            # Periodic analysis
            if time.time() - self.last_processed_time > 10:
                self.analyze_with_vlm(frame, avg_rgb, std_rgb)
                self.last_processed_time = time.time()
            cv2.imshow('OptiCam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    OptimizedCameraRGB().run()









