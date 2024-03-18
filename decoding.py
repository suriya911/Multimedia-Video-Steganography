import os
from PIL import Image
from moviepy.editor import *
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import Keys as k
import video as v

# Function to do the decryption process using AES key 
def decryption_process(encrypted_data, key, iv):
    # Initialize AES cipher with CBC mode and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    # Decrypt file data
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data

# Function to decrypt the files using the AES key 
def decrypt():
    
    #Load AES key
    with open('./Retrived_Files/decrypted_aes_key.txt', 'rb') as f:
        key=f.read()
        aes_key = bytes.fromhex(key.decode())
    n=v.get_count("./Retrived_Files")-2
    for i in range(0,n):
        # Read encrypted data from file
        with open(f'./Retrived_Files/file{i}.enc', 'rb') as f:
            encrypted_data_with_iv = f.read()
            file_type_from_encryption = encrypted_data_with_iv[:6].decode('utf-8').replace('_','') # Extract file type
            iv = encrypted_data_with_iv[6:22]  # Extract IV
            encrypted_data = encrypted_data_with_iv[22:]  # Extract encrypted data
        # Decrypt file
        decrypted_data = decryption_process(encrypted_data, aes_key, iv)
        # Write decrypted data to file
        with open(f'./Decrypted_Files/decrypted_file{i}.{file_type_from_encryption}', 'wb') as f:
            f.write(decrypted_data)

# Function to decode the video
def decodeVideo(number_of_frames):
    d = {}
    for i in range(0, len(number_of_frames)):
        print("entered")
        frame_file_name = os.path.join('./tmp', f"{number_of_frames[i]}.png")
        clear_message = decode_frame(frame_file_name)
        d[i] = clear_message.encode('latin-1')
    return d

# Function to decode the frame
def decode_frame(frame):
    data = ''
    image = Image.open(frame, 'r')
    imagedata = iter(image.getdata())
    while (True):
        pixels = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        # string of binary data
        binstr = ''
        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'
        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            return data

# Function to get the key
def get_key(key, RSA_Key):
    data = b''
    # Ensure the key exists in the dictionary
    for j in range(0, len(key)):
        data += key[j]
    with open("./Retrived_Files/key.enc", "wb") as f:
        f.write(data)
    k.decrypt_key(RSA_Key)

# Function to extract the video
def extract(video_path, RSA_Key):
    v.get_frames(video_path)
    count = int(decode_frame(os.path.join('./tmp', '0.png')).encode('latin-1'))
    print(count)
    decoded = {}
    file = {}
    x=0
    s = 1
    k = 0
    c = 0
    f_count = v.countFrames(video_path)
    key=decodeVideo([i for i in range(s, 5+s)])
    get_key(key, RSA_Key)
    
    s+=5
    # working
    while(c<3 and s<f_count):
        if(v.is_hidden(s)):
            F = [i for i in range(s, count+s)]
            file = decodeVideo(F)
            decoded[x] = file
            print(F,decoded[x][0][:7])
            x+=1
            s+=count
            k += 2
            c=0
        else:
            c+=1
            s+=1
    v.clean_tmp()
    for i in range(0, len(decoded)):  # Adjusted loop range
        data = b''
        # Ensure the key exists in the dictionary
        for j in range(0, len(decoded[i])):
            data += decoded[i][j]
        print(data[:7])
        with open(f"./Retrived_Files/file{i}.enc", "wb") as f:
            f.write(data)
    print("Data has been written to the file")

# Function to call the decryption process
def call_decrypt(video, RSA_KEY):
    extract(video, RSA_KEY)
    decrypt()
    print("The files have been decrypted and saved in Decrypted folder")