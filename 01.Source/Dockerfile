From public.ecr.aws/docker/library/debian

# OSアップグレード
RUN apt-get update && apt-get upgrade -y

# Pythonのインストール
Run apt-get install -y zlib1g-dev
RUN apt-get install -y libssl-dev
RUN apt-get install -y tk-dev

RUN apt-get install -y make
RUN apt-get install -y gcc
RUN apt-get install -y libffi-dev
RUN apt-get install -y wget
RUN apt-get install -y 
RUN apt-get install -y wget
WORKDIR /usr/local/src
RUN wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz
RUN tar zxvf Python-3.9.12.tgz
WORKDIR /usr/local/src/Python-3.9.12
RUN ./configure
RUN make -j$(grep '^processor' /proc/cpuinfo | wc -l)
RUN make altinstall
RUN ln -fns /usr/local/bin/python3[.9,]
RUN ln -s /usr/local/python3.9 /usr/local/bin/python
RUN pip3.9 install --upgrade pip

# makeに利用したパッケージを削除
RUN apt-get purge -y zlib1g-dev
RUN apt-get purge -y make
RUN apt-get purge -y wget
RUN apt-get purge -y libffi-dev

# API作成
COPY requirements.txt /tmp/requirements.txt
# psycopg2のUbuntu導入時に必要なモジュールを事前追加
RUN pip install psycopg2-binary
RUN apt-get install -y libpq-dev
# Win/Linux共通モジュール追加
# RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install aioboto3==10.1.0
RUN pip install aiobotocore==2.4.0
RUN pip install aiohttp==3.8.3
RUN pip install aioitertools==0.11.0
RUN pip install aiosignal==1.2.0
RUN pip install anyio==3.5.0
RUN pip install asgiref==3.5.0
RUN pip install async-timeout==4.0.2
RUN pip install atomicwrites==1.4.1
RUN pip install attrs==22.1.0
RUN pip install boto3==1.24.59
RUN pip install botocore==1.27.59
RUN pip install certifi==2021.10.8
RUN pip install charset-normalizer==2.0.12
RUN pip install click==8.1.2
RUN pip install colorama==0.4.4
RUN pip install coverage==6.4.4
RUN pip install ecdsa==0.18.0
RUN pip install fastapi==0.75.2
RUN pip install flake8==5.0.4
RUN pip install frozenlist==1.3.1
RUN pip install h11==0.13.0
RUN pip install idna==3.3
RUN pip install iniconfig==1.1.1
RUN pip install jmespath==1.0.0
RUN pip install mccabe==0.7.0
RUN pip install multidict==6.0.2
RUN pip install packaging==21.3
RUN pip install Pillow==9.2.0
RUN pip install pluggy==1.0.0
RUN pip install psycopg2==2.9.3
RUN pip install py==1.11.0
RUN pip install pyasn1==0.4.8
RUN pip install pycodestyle==2.9.1
RUN pip install pycryptodome==3.14.1
RUN pip install pydantic==1.9.0
RUN pip install pyflakes==2.5.0
RUN pip install pymongo==4.2.0
RUN pip install pyparsing==3.0.9
RUN pip install pytest==7.1.2
RUN pip install pytest-asyncio==0.19.0
RUN pip install pytest-cov==3.0.0
RUN pip install pytest-mock==3.8.2
RUN pip install python-dateutil==2.8.2
RUN pip install python-jose==3.3.0
RUN pip install regex==2022.8.17
RUN pip install reportlab==3.6.11
RUN pip install requests==2.27.1
RUN pip install rsa==4.8
RUN pip install s3transfer==0.6.0
RUN pip install six==1.16.0
RUN pip install sniffio==1.2.0
RUN pip install starlette==0.17.1
RUN pip install tomli==2.0.1
RUN pip install typing_extensions==4.2.0
RUN pip install urllib3==1.26.9
RUN pip install uvicorn==0.17.6
RUN pip install wrapt==1.14.1
RUN pip install yarl==1.8.1
# Linux環境特有のモジュール追加
RUN pip install "uvicorn[standard]" gunicorn

## ファイル移動
COPY ./OpenAPI /app
## ディレクトリ移動
WORKDIR /app

## 80番ポートを開ける
EXPOSE 80
## FastAPIの起動コマンド（80番ポートで待機させる）
CMD ["gunicorn", "app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
