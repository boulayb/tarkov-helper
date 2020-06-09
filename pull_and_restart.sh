git pull
sudo docker container stop `sudo docker ps -a -q  --filter ancestor=tarkov-helper_crawler`
sudo docker container stop `sudo docker ps -a -q  --filter ancestor=tarkov-helper_bot`
sudo docker container prune -f
sudo docker-compose run -d bot
sudo docker-compose run -d crawler