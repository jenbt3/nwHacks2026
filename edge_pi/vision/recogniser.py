from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt

# Path to your image

# Compares two faces, returns dictionary of verification results
# Returns None if a face is not found in one of the images
def compare_faces(img_path1, img_path2, model_name="VGG-Face", detector_backend="opencv") -> dict:
    
    try:
        # Verify if the faces belong to the same person
        result = DeepFace.verify(
            img1_path=img_path1,
            img2_path=img_path2,
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=True,  # Raise error if no face found
            align=True,  # Align faces for better accuracy
            distance_metric="cosine"  # cosine, euclidean, euclidean_l2
        )
        return result
        
    except ValueError as e:
        print(f"Error during face comparison: {e}")
        return None


# given a new image and a list of images of a person
# returns the amount of images that match out of total given (matches, total)
def validate(img_path: str, imgs: list[str]) -> tuple:
    count: int = 0
    
    for path in imgs:
        results = compare_faces(img_path, path)

        if results != None and results['verified']:
            count += 1

    return (count, len(imgs))


# prints results from compare_faces
def printResults(result):
    print(f"Same person: {result['verified']}")
    print(f"Distance: {result['distance']}")
    print(f"Threshold: {result['threshold']}")
    print(f"Model: {result['model']}")
    print(f"Detector: {result['detector_backend']}")
    
    # Interpretation
    if result['verified']:
        print("✅ Same person")
    else:
        print("❌ Different person")
