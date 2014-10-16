import os
import sys
sys.path.append('../../..')

import numpy

from fastor import util
from fastor.datasets import supervised_dataset

from model import SupervisedModel

print('Start')

pid = os.getpid()
print('PID: {}'.format(pid))
f = open('pid', 'wb')
f.write(str(pid)+'\n')
f.close()

model = SupervisedModel('experiment', './')
monitor = util.Monitor(model)

# Loading STL-10 dataset
print('Loading Data')
X_train = numpy.load('/data/stl10_matlab/train_X.npy')
y_train = numpy.load('/data/stl10_matlab/train_y.npy')
X_test = numpy.load('/data/stl10_matlab/test_X.npy')
y_test = numpy.load('/data/stl10_matlab/test_y.npy')

X_train = numpy.float32(X_train)
X_train /= 255.0
X_train *= 2.0

X_test = numpy.float32(X_test)
X_test /= 255.0
X_test *= 2.0

train_dataset = supervised_dataset.SupervisedDataset(X_train, y_train)
test_dataset = supervised_dataset.SupervisedDataset(X_test, y_test)
train_iterator = train_dataset.iterator(
    mode='random_uniform', batch_size=128, num_batches=100000)
test_iterator = test_dataset.iterator(
    mode='random_uniform', batch_size=128, num_batches=100000)

# Create object to local contrast normalize a batch.
# Note: Every batch must be normalized before use.
normer = util.Normer(filter_size=3)

print('Training Model')
for x_batch, y_batch in train_iterator:        
    x_batch = x_batch.transpose(1, 2, 3, 0)   
    x_batch = normer.run(x_batch)   
    # y_batch = numpy.int64(numpy.argmax(y_batch, axis=1))
    monitor.start()
    log_prob, accuracy = model.train(x_batch, y_batch-1)
    monitor.stop(1-accuracy) # monitor takes error instead of accuracy    
    
    if monitor.test:
        monitor.start()
        x_test_batch, y_test_batch = test_iterator.next()
        x_test_batch = x_test_batch.transpose(1, 2, 3, 0)
        x_test_batch = normer.run(x_test_batch)
        # y_test_batch = numpy.int64(numpy.argmax(y_test_batch, axis=1))
        test_accuracy = model.eval(x_test_batch, y_test_batch-1)
        monitor.stop_test(1-test_accuracy)