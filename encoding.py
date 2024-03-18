import math
from moviepy.editor import *
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import video as v
import Keys as k

# Function to do the encryption process using AES key 
def encryption_process(file_path, key):
    # Open file
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Initialize AES cipher with CBC mode and IV
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # Pad the file data
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()
    # Encrypt file data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data, iv

# Function to encrypt the files using the AES key
def encrypt(n,file):
    
    # Load AES key
    with open('./Keys/aes_key.txt', 'rb') as f:
        key=f.read()
        aes_key = bytes.fromhex(key.decode())
    
    #Split the file name and file type
    file_name,file_type=file.split(".")
    #Load the file path
    file_path=f'./Files/{file}'
    #Encrypt the file
    encrypted_data, iv = encryption_process(file_path, aes_key)
    #Create a folder to store encrypted files
    if not os.path.exists("./Encrypted_Files"):
        os.makedirs("./Encrypted_Files")
    # Write encrypted data to file
    with open(f"./Encrypted_Files/encrypted_{n}.enc", 'wb') as f:
        file_type_byte = file_type.rjust(6,'_').encode('utf-8')
        f.write(file_type_byte + iv + encrypted_data)

# Used to split string into parts.
def split_string(s_str, count):
    per_c = math.ceil(len(s_str) / count)
    split_list = []
    for i in range(0, len(s_str), per_c):
        split_list.append(s_str[i:i+per_c])
    return split_list

# Convert encoding data into 8-bit binary ASCII
def generateData(data):
    newdata = []
    for i in data: # list of binary codes of given data
        newdata.append(format(ord(i), '08b'))
    return newdata

# Pixels modified according to encoding data in generateData
def modifyPixel(pixel, data):
    datalist = generateData(data)
    lengthofdata = len(datalist)
    imagedata = iter(pixel)
    for i in range(lengthofdata):
        # Extracts 3 pixels at a time
        pixel = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        # Pixel value should be made odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pixel[j]% 2 != 0):
                pixel[j] -= 1
            elif (datalist[i][j] == '1' and pixel[j] % 2 == 0):
                if(pixel[j] != 0):
                    pixel[j] -= 1
                else:
                    pixel[j] += 1
        # Eighth pixel of every set tells whether to stop ot read further. 0 means keep reading; 1 means thec message is over.
        if (i == lengthofdata - 1):
            if (pixel[-1] % 2 == 0):
                if(pixel[-1] != 0):
                    pixel[-1] -= 1
                else:
                    pixel[-1] += 1
        else:
            if (pixel[-1] % 2 != 0):
                pixel[-1] -= 1
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]

# Encoding the data into the image
def encoder(newimage, data):
    w = newimage.size[0]
    (x, y) = (0, 0)
    for pixel in modifyPixel(newimage.getdata(), data):
        # Putting modified pixels in the new image
        newimage.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

#Function to perform steganography on the range of frames specified by the user and save the frames in the tmp folder 
def encode(input_string, count, x, y):
    split_string_list = split_string(input_string, count)
    FRAMES = [i for i in range(x, y)]
    print(FRAMES)
    print("Performing Steganography...")
    for i in range(0, len(split_string_list)):
        numbering = f"./tmp/{FRAMES[i]}.png"
        encodetext = split_string_list[i] # Copy Distributed Data into Variable
        image = Image.open(numbering, 'r') # Parameter has to be r, otherwise ValueError will occur (https://pillow.readthedocs.io/en/stable/reference/Image.html)
        newimage = image.copy() # New Variable to Store Hiddend Data
        encoder(newimage, encodetext) # Steganography
        new_img_name = numbering # Frame Number
        newimage.save(new_img_name) # Save as New Frame
    print("Complete!\n")    

# Function to call the encryption functions
def call_encrypt(video,l,frame_count_for_files,Public_key):
    print("Generating new AES keys")
    k.call_aes_key()
    print("Encrypting the AES key with RSA public key")
    k.encrypt_key(Public_key)
    f_name=video
    v.get_frames(f_name)
    
    n=v.get_count("./Files")
    for i in range(n):
        encrypt(i,l[i])
    print("The files have been encrypted and saved in Encrypted folder")
    
    s=0
    encode(str(frame_count_for_files),1,0,1)
    s+=1
    
    with open(f"./Keys/encrypted_aes_key.enc", 'rb') as f:
        TEXT_TO_ENCODE = f.read().decode('latin-1')
    encode(TEXT_TO_ENCODE,5,s,5+s)
    s+=5
    s+=2
    for i in range(1,n+1):
        # Read encrypted data from file
        with open(f'./Encrypted_Files/encrypted_{i-1}.enc', 'rb') as f:
            TEXT_TO_ENCODE = f.read().decode('latin-1')
        print(TEXT_TO_ENCODE[:7])
        encode(TEXT_TO_ENCODE,frame_count_for_files,frame_count_for_files*(i-1)+s,frame_count_for_files*(i)+s)
        s+=2
        
    v.new_video(f_name)