# Artificial Bin System (ABS)

An AI-powered smart bin management system developed entirely in software.  
This project combines machine learning, face recognition, database management, and an interactive graphical user interface to simulate an intelligent waste classification system.

## 🛠 Features
- **Face Recognition Login System** (using OpenCV + ML model)
- **Smart Waste Classification** into:
  - Plastic
  - Paper
  - Metal
  - Others
- **User Registration & Authentication** (with SQLite database)
- **Live Image Capture** and **Training Interface**
- **Real-time Classification Feedback** using ML predictions
- **Clean, Modern GUI** built with PyQt5

## 🧰 Technologies Used
- Python 3
- PyQt5 (for the GUI)
- OpenCV (for face recognition and image processing)
- SQLite (for database management)
- Machine Learning (custom neural network)
- PIL (Python Imaging Library)

## 📂 Project Structure
```
Artificial-Bin-System/
├── Maincode.py             # Main GUI and application logic
├── DatabaseManager.py      # Manages users and database
├── loginpage.ui             # PyQt5 UI design file
├── utils.py                 # Utility functions (not uploaded here)
├── system/                  # Contains system images and icons
├── dataset/                 # Training images for classification
├── images/                  # Captured face images
└── README.md                # Project description
```

## 🚀 How to Run
1. Install the required libraries:
   ```bash
   pip install PyQt5 opencv-python Pillow numpy
   ```
2. Run the main application:
   ```bash
   python Maincode.py
   ```
> 📌 Make sure you have a webcam connected for face capture features.

## 📸 Demo Screenshots
*(You can add images later of your login page, training screen, classification screen, etc.)*

## 👤 Author
- [Your Name]
