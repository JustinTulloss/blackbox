#Copyright (C) 2007 Justin M. Tulloss

NAME = cwiidmodule
SOURCES = cwiidmodule.c

SO_NAME = $(NAME).so
OBJECTS = $(SOURCES:.c=.o)

LDLIBS += -lcwiid
CFLAGS = -fpic -Wall -g -I/usr/include/python2.4
LDFLAGS = -shared -fpic

$(SO_NAME): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $(NAME).so $(LDLIBS) -o $(SO_NAME)

clean:
	rm -f *.so *.o
