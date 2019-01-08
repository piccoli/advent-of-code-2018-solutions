CXXFLAGS=-O3 -pipe -fomit-frame-pointer -march=native -Wall -std=c++11 -pedantic
TARGETS=day09 day14

all: $(TARGETS)

day09: day09.cc
day14: day14.cc

clean:
	rm -f $(TARGETS)
