# 
# Name: Adarsh Bhavnagariya (student ID: 1096488)
# UniversityofGuelph Email: abhavnag@uoguelph.ca
# Program Name: makefile
# Last Edited: 02/25/2023
# 
CC = clang
CFLAGS = -std=c99 -Wall -pedantic 
LIBS = -lm
PYTHON_INCLUDE = /usr/include/python3.10
PYTHON_LIB = /usr/lib/python3.10/config-3.10-x86_64-linux-gnu
MOL_LIB = ./
EXECS = 

all: mol.o libmol.so $(EXECS) _molecule.so 

install:  # if libmol.so is not found, do make install. Or you can enter export LD_LIBRARY_PATH=/path/to/libmol/:$LD_LIBRARY_PATH in terminal
	sudo cp libmol.so /usr/local/lib/
	sudo ldconfig

mol.o: mol.c mol.h
	$(CC) -c $(CFLAGS) -fPIC $< -o $@

libmol.so: mol.o
	$(CC) -shared mol.o -o libmol.so 

molecule_wrap.c molecule.py: molecule.i mol.h
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) -c $(CFLAGS) -fPIC -I$(PYTHON_INCLUDE) molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o mol.o
	$(CC) -shared -lpython3.10 -lmol -dynamiclib -L$(PYTHON_LIB) -L$(MOL_LIB) molecule_wrap.o mol.o -o _molecule.so 

clean:
	rm -f *.o *.so $(EXECS) molecule_wrap.c molecule.py
