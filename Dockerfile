FROM gitpod/workspace-full:latest

USER gitpod
RUN wget https://developer.arm.com/-/media/Files/downloads/gnu-rm/8-2018q4/gcc-arm-none-eabi-8-2018-q4-major-linux.tar.bz2 \
    && tar -x -C /home/gitpod -f gcc-arm-none-eabi-8-2018-q4-major-linux.tar.bz2 \
    && rm -f gcc-arm-none-eabi-8-2018-q4-major-linux.tar.bz2 

ENV PATH="/home/gitpod/gcc-arm-none-eabi-8-2018-q4-major-linux/bin:${PATH}"
USER root
