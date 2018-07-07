import cv2, dlib, argparse
from utils import extract_left_eye_center, extract_right_eye_center, get_rotation_matrix, crop_image
import pathlib

path = pathlib.Path(__file__).parent
print(path)

def classify_input(input_image):
    arr = []
    if input_image.is_file():
        arr.append(str(input_image))
    elif input_image.is_dir():
        for i in input_image.iterdir():
            i = str(i)
            if not i.endswith(('.png', '.gif', '.jpg', '.jpeg')):continue
            arr.append(i)
    return arr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Align faces in image')
    parser.add_argument('input', type=str, help='')
    parser.add_argument('--scale', metavar='S', type=int, default=4, help='an integer for the accumulator')
    args = parser.parse_args()

    input_image = args.input
    input_image =  pathlib.Path(input_image)


    output = path.joinpath('face_align_output')
    output.mkdir(exist_ok=True)
    output_image = output.joinpath(input_image.name)
    output_image = str(output_image)

    scale = args.scale

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    for i, inp in enumerate(classify_input(input_image)):
        img = cv2.imread(inp, cv2.IMREAD_GRAYSCALE)

        try:
            height, width = img.shape[:2]
        except AttributeError as e:
            print('cant find shape')
            continue
        s_height, s_width = height , width // scale
        s_height, s_width = height // scale, width // scale
        img = cv2.resize(img, (s_width, s_height))

        dets = detector(img, 1)

        for o, det in enumerate(dets, 1):
            shape = predictor(img, det)

            left_eye = extract_left_eye_center(shape)
            right_eye = extract_right_eye_center(shape)

            M = get_rotation_matrix(left_eye, right_eye)
            rotated = cv2.warpAffine(img, M, (s_width, s_height), flags=cv2.INTER_CUBIC)

            cropped = crop_image(rotated, det)

            if output_image.endswith('.jpg'):
                output_image_path = output_image.replace('.jpg', '_%i_%i.jpg' % (i, o))
            elif output_image.endswith('.png'):
                output_image_path = output_image.replace('.png', '_%i_%i.jpg' % (i, o))
            else:
                output_image_path = output_image + ('_%i_%i.jpg' % (i, o))
            print('output_path', output_image, output_image_path)
            cv2.imwrite(output_image_path, cropped)
    else:
        print('EMPTY! No Path Provided')
