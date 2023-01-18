import numpy as np
import cv2
import skimage
from skimage.morphology import convex_hull_image, erosion
from skimage.morphology import square
from hashlib import sha256
from solana.keypair import Keypair


def get_termination_bifurcation(img, mask):
    img = img == 255
    (rows, cols) = img.shape
    minutiaeTerm = np.zeros(img.shape)
    minutiaeBif = np.zeros(img.shape)

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if img[i][j] == 1:
                block = img[i - 1:i + 2, j - 1:j + 2]
                block_val = np.sum(block)
                if block_val == 2:
                    minutiaeTerm[i, j] = 1
                elif block_val == 4:
                    minutiaeBif[i, j] = 1

    mask = convex_hull_image(mask > 0)
    mask = erosion(mask, square(5))
    minutiaeTerm = np.uint8(mask) * minutiaeTerm
    return minutiaeTerm, minutiaeBif


def generate_keys(source):
    img = cv2.imread(source, 0)

    # mean thresholding
    THRESHOLD = img.mean()
    img = np.array(img > THRESHOLD).astype(int)  # binary image

    # Skeletonization reduces binary objects to 1 pixel wide representations
    skel = skimage.morphology.skeletonize(img)
    skel = np.uint8(skel) * 255
    mask = img * 255

    # minutiae points
    minutiaeTerm, minutiaeBif = get_termination_bifurcation(skel, mask)

    coordinates_Term = np.argwhere(minutiaeTerm == 1.0)
    coordinates_Bif = np.argwhere(minutiaeBif == 1.0)
    coordinates = np.concatenate((coordinates_Term, coordinates_Bif), axis=0)

    distance_list = []

    # compute euclidean distances between each pair of minutiae points
    for e_coo in coordinates:
        for f_coo in coordinates:
            dist = np.linalg.norm(e_coo - f_coo)
            dist = int(dist)
            # convert distance in 8-bit binary number
            dist_b = format(dist, '08b')
            distance_list.append(dist_b)

    # sort euclidean distances
    distance_list.sort()

    def binary_to_gray(n):
        n = int(n, 2)
        n ^= (n >> 1)
        return bin(n)[2:]

    distance_list_gray = []

    for e_bin in distance_list:
        # convert 8-bit binary number in 8-bit gray code
        e_bin = binary_to_gray(e_bin)
        e_bin = e_bin.zfill(8)
        distance_list_gray.append(e_bin)

    # concatenate gray codes
    G = ''.join(distance_list_gray)

    # hash value of the string
    digest = int(sha256(G.encode()).hexdigest(), 16)

    # 32 byte seed
    digest = digest.to_bytes(32, 'big')

    # keypair generation
    keypair = Keypair.from_seed(digest)
    public_key = keypair.public_key
    secret_key = keypair.secret_key.hex()

    return public_key, secret_key
