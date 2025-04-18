import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D , MaxPool2D , Flatten , Dropout 
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.metrics import categorical_crossentropy
import tensorflow as tf
import pickle
import cv2
import numpy as np
import os
import numpy as np
class MlTrainer:
    def __init__(self,epoch=20):
      self.labels = ['plastic', 'paper','metal','others']
      self.modelname="model/cnn_saved_model.keras"
      self.epoch=epoch
      self.load_saved_model()
    def load_saved_model(self):
      try:
        self.model=keras.models.load_model(self.modelname)
      except:
        self.model=self.get_model()
      
    def get_data(self,data_dir,img_size):
        data = [] 
        for label in self.labels: 
            path = os.path.join(data_dir, label)
            class_num = self.labels.index(label)
            for img in os.listdir(path):
                try:
                    img_arr = cv2.imread(os.path.join(path, img)) #convert BGR to RGB format
                    resized_arr = cv2.resize(img_arr, (img_size, img_size)) # Reshaping images to preferred size
                    data.append([resized_arr, class_num])
                except Exception as e:
                    print(e)
        return data
    def get_training_data(self,img_size):
      train=self.get_data("dataset/train",img_size)
      x_train = []
      y_train = []
      for feature, label in train:
        x_train.append(feature)
        y_train.append(label)
      # Normalize the data
      x_train = np.array(x_train) / 255
      x_train.reshape(-1, img_size, img_size, 1)
      y_train = np.array(y_train)
  
      datagen = ImageDataGenerator(
              featurewise_center=False,  # set input mean to 0 over the dataset
              samplewise_center=False,  # set each sample mean to 0
              featurewise_std_normalization=False,  # divide inputs by std of the dataset
              samplewise_std_normalization=False,  # divide each input by its std
              zca_whitening=False,  # apply ZCA whitening
              rotation_range = 30,  # randomly rotate images in the range (degrees, 0 to 180)
              zoom_range = 0.2, # Randomly zoom image 
              width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
              height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
              horizontal_flip = True,  # randomly flip images
              vertical_flip=False)  # randomly flip images
      datagen.fit(x_train)
      return x_train,y_train
    def get_model(self,img_size=128,kernel=3):
      model = Sequential()
      model.add(Conv2D(32,kernel,padding="same", activation="relu", input_shape=(img_size,img_size,3)))
      model.add(MaxPool2D())
      model.add(Conv2D(32, kernel, padding="same", activation="relu"))
      model.add(MaxPool2D())
      model.add(Conv2D(64, kernel, padding="same", activation="relu"))
      model.add(MaxPool2D())
      model.add(Dropout(0.4))
      model.add(Flatten())
      model.add(Dense(128,activation="relu"))
      model.add(Dense(len(self.labels), activation="softmax"))
      model.summary()
      opt = Adam(learning_rate=0.0001)
      model.compile(optimizer = opt , loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True) , metrics = ['accuracy'])
      return model
    def train(self,imagewidth=128,kernel=3):
      print("preparing training data")
      x_train,y_train=self.get_training_data(imagewidth)
      print("training data prepared")
      print("creating model")
      model=self.get_model(imagewidth,kernel)
      history = model.fit(x_train,y_train,epochs = self.epoch ,batch_size=8)
      model.save(self.modelname)
      with open("model/img_size.pkl",'wb') as f:
        data=[imagewidth]
        pickle.dump(data,f)
      acc = history.history['accuracy']
      loss = history.history['loss']
      
    def test(self,image="test.jpg"):
      img_size=128
      with open("model/img_size.pkl",'rb') as f:
        img_size=pickle.load(f)[0]
      img_arr = cv2.imread(image)[...,::-1] #convert BGR to RGB format
      resized_arr = cv2.resize(img_arr, (img_size, img_size)) # Reshaping images to preferred size
      x_test=np.array([resized_arr])
      predictions = self.model.predict(x_test)[0]
      class_=np.argmax(predictions)
      label=self.labels[class_]
      return label
if __name__=="__main__":
  print("program started")
  agent=MlTrainer(50)
  agent.train()
  #print(agent.test())
  