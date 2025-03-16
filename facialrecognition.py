import cv2
from skimage.metrics import structural_similarity as ssim
import glob
import os
import paramiko

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open the default camera
cap = cv2.VideoCapture(1)

# Load and preprocess reference images
reference_images = {}
for ref_path in glob.glob(os.path.join(os.getcwd(), 'image_*.jpg')):
    ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
    faces = face_cascade.detectMultiScale(ref_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        reference_images[ref_path] = ref_img[y:y+h, x:x+w]

if not reference_images:
    print("No reference images found. Exiting.")
    cap.release()
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    results = []
    for (x, y, w, h) in faces:
        detected_face = gray[y:y+h, x:x+w]

        best_match = None
        best_similarity = 0

        for ref_name, ref_face in reference_images.items():
            try:
                detected_resized = cv2.resize(detected_face, (ref_face.shape[1], ref_face.shape[0]))
                similarity = ssim(ref_face, detected_resized)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = ref_name
            except:
                continue  # Skip errors in resizing

        is_similar = best_similarity > 0.65
        result_text = "Similar" if is_similar else "Not Similar"
        results.append(result_text)

        color = (0, 255, 0) if is_similar else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, result_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
    with open('output.txt', 'w') as txt_file:
        txt_file.write('\n'.join(results))
    
    # Use paramiko for secure file transfer
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.10.3', username='qnxuser', password='qnxuser', timeout=10)

    sftp = ssh.open_sftp()
    sftp.put('output.txt', '/data/home/qnxuser/newdirectory/output.txt')
    sftp.close()
    ssh.close()
    print("File sent to QNX using paramiko")
    
    cv2.imshow('Face Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()