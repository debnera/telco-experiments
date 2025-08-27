# Prerequisites:
# Install docker-desktop (or a non-gui variant if preferred)
# Install docker-compose

# Clone the latest oai core network repo
git clone https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed.git

# Navigate to the folder that has all docker configuration files
cd oai-cn5g-fed/
cd docker-compose/

# Create new python virtualenv (not super necessary, as we are only installing pyyaml)
virtualenv -p python3 venv
source venv/bin/activate
pip install pyyaml

# Start the core network using python (from the oai-cn5g-fed/docker-compose/ folder)
python core-network.py  # Print all options
python core-network.py --type start-mini  # Does not work (complains about something not being implemented)
python core-network.py --type start-mini --scenario 2  # This works and sets up the core network with self-tests

# Pull a RAN simulator from docker (gnbsim in this tutorial)
# We need to do this only because the repository name has changed
docker pull rohankharade/gnbsim
docker image tag rohankharade/gnbsim:latest gnbsim:latest  # Change the image name. Default config expects this name.

# Launch gnbsim
docker-compose -f docker-compose-gnbsim.yaml up -d gnbsim
docker-compose -f docker-compose-gnbsim.yaml ps -a  # Check that gnbsim is running
docker logs gnbsim 2>&1 | grep "UE address:"  # Check that (some?) UE was allocated an address

# Check that all services are running
docker ps -a

# Try ping from DN (Data Network) to UE
# Essentially, we are testing that the end-to-end routing from UE<>RAN<>core (UPF)<>DN->internet is working
docker exec oai-ext-dn ping -c 3 12.1.1.2
docker exec gnbsim ping -c 3 -I 12.1.1.2 google.com  # A ping from UE through core network to the internet

# Try iperf (from UE to DN)
docker exec -it oai-ext-dn iperf3 -s  # Start iperf server on DN
docker exec -it gnbsim iperf3 -c 192.168.70.135 -B 12.1.1.2  # Run iperf from UE to DN (use separate terminal window)

# Recover logs from docker containers
mkdir -p /tmp/oai/mini-gnbsim # Create temp-folder for log files
chmod 777 /tmp/oai/mini-gnbsim
docker logs oai-amf > /tmp/oai/mini-gnbsim/amf.log 2>&1
docker logs oai-smf > /tmp/oai/mini-gnbsim/smf.log 2>&1
docker logs oai-upf > /tmp/oai/mini-gnbsim/upf.log 2>&1
docker logs oai-ext-dn > /tmp/oai/mini-gnbsim/ext-dn.log 2>&1
docker logs gnbsim > /tmp/oai/mini-gnbsim/gnbsim.log 2>&1


# Stop
docker-compose -f docker-compose-gnbsim.yaml down -t 0
python3 ./core-network.py --type stop-mini --scenario 2
