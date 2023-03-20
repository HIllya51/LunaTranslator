FROM quay.io/pypa/manylinux2014_x86_64

RUN git clone --depth=1 https://github.com/taku910/mecab.git && \
    cd mecab/mecab && \
    ./configure --enable-utf8-only && \
    make && \
    make install
