#Copyright (C) 2007 Justin M. Tulloss

SOURCES = cwiidmodule.c

LDLIBS += -lcwiid
CFLAGS = -fpic -Wall -g -I /usr/include/python2.4
LDFLAGS = -shared -fpic
NAME = cwiidmodule
OBJ = $(NAME).o
CC = gcc

$(NAME): $(OBJ)
	$(CC) $(LDFLAGS) -o $(NAME).so $(LDLIBS) $(OBJ)

$(NAME).o: $(SOURCES)
	$(CC) $(CFLAGS) -c $(SOURCES)

clean:
	rm -f *.so *.o
