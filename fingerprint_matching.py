import os
import cv2


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_best_match(sample):

    # sample = cv2.imread("SOCOFing/Altered/Altered-Hard/150__M_Right_index_finger_Obl.BMP")
    # sample = cv2.resize(sample, None, fx=2.5, fy=2.5)

    # sample = cv2.imread(sample)
    # cv2.imshow("Sample", sample)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    best_score = 0
    match = None
    image = None
    kp1, kp2, mp = None, None, None

    counter = 0

    # Create a SIFT object
    sift = cv2.SIFT_create()  # Scale Invariant Feature Transform
    # Detect the keypoints & compute the descriptors
    keypoints_1, descriptors_1 = sift.detectAndCompute(sample, None)

    # for file in [file for file in os.listdir("SOCOFing/Real")][:1000]:
    for file in os.listdir(APP_ROOT + '/static/images/'):
        if counter > 0:
            print(counter)
            print(file)
        counter += 20

        ext = os.path.splitext(file)[-1]
        if ext == ".BMP":

            path = APP_ROOT + '/static/images/' + file
            fingerprint_image = cv2.imread(path)

            # Detect the keypoints & compute the descriptors
            keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)

            # Find best match of distance between keypoints and descriptors
            # fast local approximate nearest neighbors (FLANN)
            matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10}, {})\
                .knnMatch(descriptors_1, descriptors_2, k=2)  # k=2 as we only compare two images at any time.

            # Matching the keypoints for fingerprint authentication
            match_points = []
            for p, q in matches:
                if p.distance < 0.1 * q.distance:
                    match_points.append(p)

            keypoints = 0
            if len(keypoints_1) < len(keypoints_2):
                keypoints = len(keypoints_1)
            else:
                keypoints = len(keypoints_2)

            if len(match_points) / keypoints * 100 > best_score:
                best_score = len(match_points) / keypoints * 100
                match = file
                image = fingerprint_image
                kp1, kp2, mp = keypoints_1, keypoints_2, match_points

    print("BEST MATCH: " + str(match))
    print("SCORE: " + str(best_score))

    # fingerprint with drawn match points and the best match and score
    # result = cv2.drawMatches(sample, kp1, image, kp2, mp, None)
    # result = cv2.resize(result, None, fx=2, fy=2)

    # cv2.imshow("Result", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return match, best_score
