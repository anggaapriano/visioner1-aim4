import h5py

# Buka file .h5
# file = h5py.File('model_cifar10_cnn_tf.h5', 'r')
file = h5py.File('cornmodel.h5', 'r')

# Tampilkan isi dari setiap group dan dataset di dalam file
def print_attrs(name, obj):
    print(name)
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))

file.visititems(print_attrs)

# Tutup file
file.close()