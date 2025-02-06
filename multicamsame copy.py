import cv2
import numpy as np
import time

def initialize_cameras():
    """Initialise all webcams and return their capture objects."""
    caps = []
    for i in range(0, 3):  
        cap = cv2.VideoCapture(i)
        cap.set(cv2.CAP_PROP_FPS, 24)
        if not cap.isOpened():
            print(f"Error: Could not open webcam {i}.")
        else:
            caps.append(cap)
    return caps

def apply_zoom_and_pan(frame, x, y, zoom_factor, output_width=1080, output_height=720):
    """
    Apply zoom/pan on the frame, then resize to 900×600 for display.
    """
    original_height, original_width = frame.shape[:2]

    # Zoomed sub-region dimensions
    new_width = int(original_width / zoom_factor)
    new_height = int(original_height / zoom_factor)

    # Clamp sub-region if it exceeds actual resolution
    if new_width > original_width:
        new_width = original_width
    if new_height > original_height:
        new_height = original_height

    # Clamp x,y so we stay in the frame
    x = max(0, min(x, original_width - new_width))
    y = max(0, min(y, original_height - new_height))

    # Crop the zoomed region
    zoomed_frame = frame[y:y + new_height, x:x + new_width]

    # Resize the final output to 900×600
    final_frame = cv2.resize(zoomed_frame, (output_width, output_height))
    return final_frame

def main():
    caps = initialize_cameras()
    if not caps:
        return

    # Final display window
    output_width, output_height = 1080, 720
    cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Webcam", output_width, output_height)

    camera_width, camera_height = 1280, 720

    # Zoom, pan, and timing parameters
    min_zoom = 0.1
    max_zoom = 4.0
    min_pan_speed = 2
    max_pan_speed = 8
    min_zoom_speed = 0.01
    max_zoom_speed = 0.04
    interval_range = (2, 25)

    last_change_time = time.time()

    zoom_factor = np.random.uniform(min_zoom, max_zoom)
    center_x = np.random.randint(0, camera_width)
    center_y = np.random.randint(0, camera_height)

    new_width = int(camera_width / zoom_factor)
    new_height = int(camera_height / zoom_factor)

    # Convert the centre to top-left so it doesnt go out of bounds
    x = center_x - new_width // 2
    y = center_y - new_height // 2

    x = max(0, min(x, camera_width - new_width))
    y = max(0, min(y, camera_height - new_height))

    current_camera_index = np.random.choice(len(caps))
    current_action = 'static'
    dx, dy = 0, 0

    while True:
        ret, frame = caps[current_camera_index].read()
        if not ret:
            print(f"Error reading from camera {current_camera_index}")
            continue

        current_time = time.time()
        if current_time - last_change_time > np.random.uniform(*interval_range):
            actions = ['zoom_in', 'zoom_out', 'pan', 'static']
            action_probs = [0.3, 0.2, 0.4, 0.1]  # Weighted choice
            current_action = np.random.choice(actions, p=action_probs)
            last_change_time = current_time
            zoom_speed = np.random.uniform(min_zoom_speed, max_zoom_speed)
            current_camera_index = np.random.choice(len(caps))

            if current_action in ['zoom_in', 'zoom_out']:
                # Re-centre on a random point in the frame
                center_x = np.random.randint(0, camera_width)
                center_y = np.random.randint(0, camera_height)
                dx, dy = 0, 0

            elif current_action == 'pan':
                # Pick a random direction
                direction = np.random.choice(['left', 'right', 'up', 'down'])
                pan_speed = np.random.randint(min_pan_speed, max_pan_speed)
                if direction == 'left':
                    dx = -pan_speed
                    dy = 0
                elif direction == 'right':
                    dx = pan_speed
                    dy = 0
                elif direction == 'up':
                    dy = -pan_speed
                    dx = 0
                elif direction == 'down':
                    dy = pan_speed
                    dx = 0

            else:
                dx, dy = 0, 0

        # Update zoom factor if needed
        if current_action == 'zoom_in' and zoom_factor < max_zoom:
            zoom_factor += zoom_speed
        elif current_action == 'zoom_out' and zoom_factor > min_zoom:
            zoom_factor -= zoom_speed

        # Calculate the new sub-region dimensions
        new_width = int(camera_width / zoom_factor)
        new_height = int(camera_height / zoom_factor)

        # Keep them within camera bounds
        new_width = min(new_width, camera_width)
        new_height = min(new_height, camera_height)

        if current_action == 'pan':
            center_x += dx
            center_y += dy

            min_cx = new_width // 2
            max_cx = camera_width - (new_width // 2)
            min_cy = new_height // 2
            max_cy = camera_height - (new_height // 2)

            center_x = max(min_cx, min(center_x, max_cx))
            center_y = max(min_cy, min(center_y, max_cy))

        x = center_x - new_width // 2
        y = center_y - new_height // 2

        # Final clamp
        x = max(0, min(x, camera_width - new_width))
        y = max(0, min(y, camera_height - new_height))

        # Apply and display
        final_frame = apply_zoom_and_pan(frame, x, y, zoom_factor,
                                         output_width, output_height)
        print(current_action)
        cv2.imshow("Webcam", final_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
