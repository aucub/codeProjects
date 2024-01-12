FROM jlesage/baseimage-gui:debian-11-v4

RUN add-pkg locales
RUN sed-patch 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
RUN sed-patch 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen

ENV LANG=zh_CN.UTF-8 TZ=CN ENABLE_CJK_FONT=1

RUN add-pkg chromium chromium-driver python3 fonts-dejavu moreutils python3-pip fonts-wqy-zenhei

RUN set-cont-env APP_NAME "JB"

COPY ./auto_job__find__chatgpt__rpa/auto_job_find/requirements.txt /default/auto_job__find__chatgpt__rpa/auto_job_find/requirements.txt

RUN pip install -r /default/auto_job__find__chatgpt__rpa/auto_job_find/requirements.txt

RUN pip install tiktoken faiss-cpu pypdf

COPY auto_job__find__chatgpt__rpa/ /default/auto_job__find__chatgpt__rpa/

COPY rootfs/ /

RUN useradd -u 1000 -m myuser

ENV HOME=/home/myuser

ENV USER_ID=1000 GROUP_ID=1000 UMASK=000

RUN chmod a+rwx /default

WORKDIR /default/auto_job__find__chatgpt__rpa/auto_job_find

RUN chmod -R 777 /default

RUN chown -R myuser:myuser /default
