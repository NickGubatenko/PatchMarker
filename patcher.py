import cv2
import os
from datetime import datetime


PATCHES_DESCRIPTION_FILE = 'description.txt'
INPUT_REL_PATH = 'input/'
OUTPUT_REL_PATH = 'output/'
FULLSCREEN = False
PATCH_SIZE = 150
MOUSEWHEEL_BOXSIZE_STEP = 4
PATCH_FILENAME_EXTENSION = 'jpg'
BB_COLOR_IF_CAR_IS_PRESENT = (66, 128, 66)
BB_COLOR_IF_CAR_IS_ABSENT = (66, 66, 128)


class Patcher:
    def __init__(self, img_name, img, subfolder):
        self.patch_index = 0
        self.rect_pos_x = 0
        self.rect_pos_y = 0
        self.rect_size = 100
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        self.img = img
        self.img_canvas = self.img.copy()
        self.img_name, _ = img_name.split('.')
        self.subfolder = subfolder
        self.window_name = f"Patcher {PATCH_SIZE}x{PATCH_SIZE} " \
                           f"{OUTPUT_REL_PATH}{subfolder}/*.{PATCH_FILENAME_EXTENSION}"
        if FULLSCREEN:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        else:
            cv2.namedWindow(self.window_name)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.window_name, self.event_dispatcher)
        cv2.imshow(self.window_name, self.img)

    def draw_rectangle(self):
        image = self.img_canvas.copy()
        cv2.rectangle(image,
                      (self.rect_pos_x, self.rect_pos_y),
                      (self.rect_pos_x + self.rect_size, self.rect_pos_y + self.rect_size), (0, 0, 0))
        cv2.rectangle(image,
                      (self.rect_pos_x+1, self.rect_pos_y+1),
                      (self.rect_pos_x-1 + self.rect_size, self.rect_pos_y-1 + self.rect_size), (255, 255, 255))
        cv2.imshow(self.window_name, image)

    def save_patch(self, car_presence_flag: str):
        if car_presence_flag == '0':
            rectangle_color = BB_COLOR_IF_CAR_IS_ABSENT
        else:
            rectangle_color = BB_COLOR_IF_CAR_IS_PRESENT
        cv2.rectangle(self.img_canvas,
                      (self.rect_pos_x, self.rect_pos_y),
                      (self.rect_pos_x + self.rect_size, self.rect_pos_y + self.rect_size), rectangle_color)
        crop = self.img[self.rect_pos_y:self.rect_pos_y + self.rect_size,
                        self.rect_pos_x:self.rect_pos_x + self.rect_size]
        resize = cv2.resize(crop, (PATCH_SIZE, PATCH_SIZE))
        cv2.imwrite(f'{OUTPUT_REL_PATH}{self.subfolder}/{car_presence_flag}_{self.img_name}'
                    f'_patch{self.patch_index}.{PATCH_FILENAME_EXTENSION}', resize)
        self.save_txt_description(car_presence_flag)
        self.patch_index += 1

    def save_txt_description(self, car_presence_flag: str):
        with open(f"{OUTPUT_REL_PATH}/{self.subfolder}/{PATCHES_DESCRIPTION_FILE}", 'a', newline='') as f:
            f.write(f'{car_presence_flag}_{self.img_name}'
                    f'_patch{self.patch_index}.{PATCH_FILENAME_EXTENSION} {car_presence_flag}\n')

    def event_dispatcher(self, event, x, y, flags, param):
        self.rect_pos_x = x
        self.rect_pos_y = y
        self.draw_rectangle()

        # left button press
        if event == cv2.EVENT_LBUTTONDOWN and not (flags & cv2.EVENT_FLAG_CTRLKEY):
            pass

        # left button release
        if event == cv2.EVENT_LBUTTONUP and not (flags & cv2.EVENT_FLAG_CTRLKEY):
            self.save_patch('1')

        # right button press
        if event == cv2.EVENT_RBUTTONDOWN:
            pass

        # right button release
        if event == cv2.EVENT_RBUTTONUP:
            self.save_patch('0')

        # left button press + CTRL
        if event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY):
            pass

        # mousewheel scroll
        if event == 10:
            # sign of the flag shows direction of mousewheel
            if flags > 0:
                # scroll up
                if self.rect_size < (min(self.img_height, self.img_width) - MOUSEWHEEL_BOXSIZE_STEP):
                    self.rect_size += MOUSEWHEEL_BOXSIZE_STEP
            else:
                # scroll down
                if self.rect_size > MOUSEWHEEL_BOXSIZE_STEP * 2:
                    self.rect_size -= MOUSEWHEEL_BOXSIZE_STEP


def get_list_of_image_names_for_processing():
    (_, _, image_names) = next(os.walk(INPUT_REL_PATH))
    return image_names


if not os.path.exists(OUTPUT_REL_PATH):
    os.makedirs(OUTPUT_REL_PATH)

new_subfolder = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
new_subfolder_path = OUTPUT_REL_PATH + new_subfolder
os.makedirs(new_subfolder_path)

images = get_list_of_image_names_for_processing()

if len(images) > 0:
    im_name = images.pop()
    im = cv2.imread(f"{INPUT_REL_PATH}{im_name}")
    p = Patcher(im_name, im, new_subfolder)

    while 1:
        key = cv2.waitKey(15)
        if key == ord(' '):
            if len(images) > 0:
                im_name = images.pop()
                im = cv2.imread(f"{INPUT_REL_PATH}{im_name}")
                p = Patcher(im_name, im, new_subfolder)
            else:
                break
        if key == 27:
            break
    cv2.destroyAllWindows()
