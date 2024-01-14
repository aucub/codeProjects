FROM jlesage/baseimage-gui:debian-11-v4

RUN add-pkg locales
RUN sed-patch 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
RUN sed-patch 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen

ENV LANG=zh_CN.UTF-8 TZ=CN ENABLE_CJK_FONT=1

# RUN sed-patch 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

RUN add-pkg chromium chromium-driver python3 fonts-dejavu moreutils python3-pip fonts-wqy-zenhei

RUN set-cont-env APP_NAME "BS"

COPY ./BossRS-helper/requirements.txt /default/BossRS-helper/requirements.txt

# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install -r /default/BossRS-helper/requirements.txt

COPY BossRS-helper/ /default/BossRS-helper/

COPY rootfs/ /

RUN useradd -u 1000 -m myuser

ENV HOME=/home/myuser

ENV USER_ID=1000 GROUP_ID=1000 UMASK=000

RUN chmod a+rwx /default
