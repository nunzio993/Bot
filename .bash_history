Nunzio993__
sudo -i
nano ~/.bashrc
Nunzio993__
python -m src.run_signal ..
cd binanceBot/venv/bin/activate
source ~/binanceBot/venv/bin/activate
python -m src.run_signal ..
ls
cd binanceBot/
ls
cs src
cd src/
ls
python -m src.run_signal.py ..
cd ..
python -m src.run_signal.py ..
python -m src.run_signal ..
# Dalla root del progetto (~/binanceBot), con il venv attivo:
python -m src.run_signal   --symbol BTCUSDC   --timeframe H4   --entry_price 30000   --sl_method H1   --sl_percent 1   --tp_percent 2   --quantity 0.001
echo $BINANCE_API_KEY
echo $BINANCE_API_SECRET
echo 'export BINANCE_API_KEY="5gslQFwhB1A2eo5eETDQkHZzsE4fECHvvh2npVLpCkDEuVWPgSOIJNv3GARLdFwK"' >> ~/.bash_profile
echo 'export BINANCE_API_SECRET="iyPgm84XXph1VIs3hj3ICpTS8nzrJnMI703y1C7fpByasLKY8pkCugiiC6kK8GgS"' >> ~/.bash_profile
echo $BINANCE_API_SECRET
echo $BINANCE_API_KEY
source ~/.bash_profile
echo $BINANCE_API_KEY
echo $BINANCE_API_SECRET
python -m src.run_signal   --symbol BTCUSDC   --timeframe H4   --entry_price 30000   --sl_method H1   --sl_percent 1   --tp_percent 2   --quantity 0.001
export BINANCE_API_KEY="5gslQFwhB1A2eo5eETDQkHZzsE4fECHvvh2npVLpCkDEuVWPgSOIJNv3GARLdFwK"
export BINANCE_API_SECRET="iyPgm84XXph1VIs3hj3ICpTS8nzrJnMI703y1C7fpByasLKY8pkCugiiC6kK8GgS"
sed -i 's/"H1": dict(minute=1)/"H1": dict(minute="*")/' src/scheduler.py
python -m src.scheduler
sudo systemctl status binance-scheduler
sudo tee /etc/systemd/system/binance-scheduler.service > /dev/null << 'EOF'
[Unit]
Description=Binance Close-Only Scheduler
After=network.target

sudo tee /etc/systemd/system/binance-scheduler.service > /dev/null << 'EOF'
[unit]
Description=Binance Close-Only Scheduler
After=network.target
[Service]
User=fedora
WorkingDirectory=/home/fedora/binanceBot
Environment=BINANCE_API_KEY=5gslQFwhB1A2eo5eETDQkHZzsE4fECHvvh2npVLpCkDEuVWPgSOIJNv3GARLdFwK
Environment=BINANCE_API_SECRET=iyPgm84XXph1VIs3hj3ICpTS8nzrJnMI703y1C7fpByasLKY8pkCugiiC6kK8GgS
ExecStart=/home/fedora/binanceBot/venv/bin/python -m src.scheduler
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable binance-scheduler
sudo systemctl start binance-scheduler
sudo systemctl status binance-scheduler
sudo tee /etc/systemd/system/binance-scheduler.service > /dev/null << 'EOF'
[Unit]
Description=Binance Close-Only Scheduler
After=network.target
[Service]
User=fedora
WorkingDirectory=/home/fedora/binanceBot
Environment=BINANCE_API_KEY=LA_TUA_TESTNET_KEY
Environment=BINANCE_API_SECRET=IL_TUO_TESTNET_SECRET
ExecStart=/home/fedora/binanceBot/venv/bin/python -m src.scheduler
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable binance-scheduler
sudo systemctl start binance-scheduler
sudo journalctl -f -u binance-scheduler
ls -l /home/fedora/binanceBot/venv/bin/python
deactivate
/home/fedora/binanceBot/venv/bin/python /home/fedora/binanceBot/src/scheduler.py
cd /home/fedora/binanceBot
/home/fedora/binanceBot/venv/bin/python -m src.scheduler
sudo nano /etc/systemd/system/binance-scheduler.service
sudo systemctl daemon-reload
sudo systemctl restart binance-scheduler
sudo systemctl status binance-scheduler
sudo systemctl enable binance-scheduler
sudo systemctl status binance-scheduler
sudo systemctl daemon-reload
sudo systemctl restart binance-scheduler
sudo systemctl status binance-scheduler
chmod +x /home/fedora/binanceBot/venv/bin/python
sudo
sudo -i
cd ~/binanceBot
rm -rf venv
sudo -i
pip install python-binance apscheduler
deactivatechown -R fedora:fedora /home/fedora/binanceBot/venv
chown -R fedora:fedora /home/fedora/binanceBot/venv
ls -l /home/fedora/binanceBot/venv/bin/python
file  /home/fedora/binanceBot/venv/bin/python
systemctl daemon-reload
systemctl restart binance-scheduler
systemctl status binance-scheduler
journalctl -u binance-scheduler -xe
sudo -u fedora /home/fedora/binanceBot/venv/bin/python3.12 -c 'print("OK")'
sudo -u fedora /home/fedora/binanceBot/venv/bin/python -c 'print("OK")'
ls -l /usr/bin/python3.12
systemctl daemon-reload
systemctl restart binance-scheduler
systemctl status binance-scheduler
python3.12 -m venv --copies venv
source venv/bin/activate
pip install python-binance apscheduler
deactivate
chown -R fedora:fedora /home/fedora/binanceBot/venv
systemctl daemon-reload
systemctl restart binance-scheduler
systemctl status binance-scheduler
getenforce
setenforce 0
systemctl daemon-reload
systemctl restart binance-scheduler
systemctl status binance-scheduler
mount | grep ' on /home '
mount -o remount,exec /home
sudo su -
cd ~/binanceBot
rm -rf venv
python3.12 -m venv --copies venv
source venv/bin/activate
pip install python-binance apscheduler
deactivate
sudo chown -R fedora:fedora /home/fedora/binanceBot/venv
sudo systemctl daemon-reload
/home/fedora/binanceBot/venv/bin/python -m src.scheduler
sudo journalctl -u binance-scheduler -f
# 1. Passa a fedora
su - fedora
# 1. Passa a fedora
su - fedora
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install python-binance apscheduler
deactivate
chown -R fedora:fedora /home/fedora/binanceBot/venv
ls -l /home/fedora/binanceBot/venv/bin/python
file /home/fedora/binanceBot/venv/bin/python
sudo systemctl daemon-reload
sudo systemctl restart binance-scheduler
sudo systemctl status binance-scheduler
chown -R fedora:fedora /home/fedora/binanceBot/venv
sudo su -
cd binanceBot/
nano dashboard.py 
sudo -i
ls
cd d
nano dashboard.py 
sudo nano d
sudo nano dashboard.py 
docker-compose build
udo docker-compose build
sudo docker-compose up -d
sudo docker-compose build
sudo docker login
sudo docker-compose build
sudo docker-compose up -d
sudo docker-compose exec dashboard pip install ccxt
ls
cd Dockerfile 
ls
sudo nano Dockerfile
sudo nano requirements.txt 
sudo nano dashboard.py 
sudo docker-compose restart dashboard
sudo nano dashboard.py 
tar -czvf binanceBot.tar.gz
tar -czvf binanceBot.tar.gz .
scp user@51.91.250.194:~/binanceBot/binanceBot.tar.gz .
scp fedora@51.91.250.194:~/binanceBot/binanceBot.tar.gz .
scp fedora@51.91.250.194:~/binanceBot/binanceBot.tar.gz downlaod
ls
cd downlaod 
cd binanceBot/
ls
cd Dockerfile 
sudo nano Dockerfile 
ls
cd src/
ls
sudo nano core_and_scheduler.py
sudo nano scheduler.py 
sudo nano core_and_scheduler.py
sudo nano scheduler.py 
ls
cd ..
ls
sudo nano requirements.txt 
ls
nano Dockerfile 
sudo nano Dockerfile 
cd venv/
ls
cd ..
ls
cd .env
nano .env 
sudo nano .env 
docker-compose down
docker-compose up -d --build
sudo su
cd binanceBot/
sudo su
docker-compose exec core sqlite3 /app/trade.db"DELETE from orders;"
cd binanceBot/
docker-compose exec core sqlite3 /app/trade.db"DELETE from orders;"
sudo su
cdb
cd binanceBot/
cd src/
sudo su
sdo su
sudo su
ls
cd binanceBotTestnet/
ls
cd docker-compose.yml 
nano docker-compose.yml 
suso su
nano docker-compose.yml 
sudo su
cd binanceBotTestnet/
ls
cd babi symbols.py 
nano symbols.py 
cd downlaod 
nano downlaod 
rm downlaod 
y
sudo su
cd binanceBot
python test_boradcast.py 
rm test_boradcast.py 
cd src/
nano test_broadcast.py
python test_broadcast.py 
cd binanceBot
nano dashboard.py
sudo su
sudo su
sudo su
sudo su
