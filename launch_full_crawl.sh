sudo docker container exec `sudo docker ps -a -q  --filter ancestor=tarkov-helper_crawler` python crawler/crawler.py -es -s -p &