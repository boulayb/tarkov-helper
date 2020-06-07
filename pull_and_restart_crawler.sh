git pull
sudo docker container stop `sudo docker ps -a -q  --filter ancestor=tarkov-helper_crawler`
sudo docker container prune -f
sudo docker-compose run -d crawler