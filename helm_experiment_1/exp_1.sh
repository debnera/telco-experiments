# Kubernetes is running on docker desktop

# Install helm:
sudo snap install helm --classic

# Fetch charts from OAI repo
# https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed/-/tree/master/charts/oai-5g-core/oai-5g-basic
mkdir -p oai_charts
wget -O /tmp/oai_charts.zip "https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed/-/archive/master/oai-cn5g-fed-master.zip?path=charts"
unzip /tmp/oai_charts.zip "*/charts/*" -d oai_charts
rm /tmp/oai_charts.zip

# Launch the CN
cd oai-charts-basic
helm dependency update
helm install oai-5g-basic .

# Launch RAN
cd oai-gnb
helm dependency update
helm install oai-gnb .

# Launch UE
cd oai-nr-ue
helm dependency update
helm install oai-nr-ue .

# Test UE connectivity
kubectl get pods  # Check pod name
kubectl exec -it oai-nr-ue-7db7ccddcb-g88tv -- bash
ping -I oaitun_ue1 12.1.1.1 # Ping UPF
ping -I oaitun_ue1 8.8.8.8  # Ping outside internet
 
# TODO:
# launch kepler
helm install kepler \
  https://github.com/sustainable-computing-io/kepler/releases/download/v0.11.2/kepler-helm-0.11.2.tgz \
  --namespace kepler \
  --create-namespace
# launch prometheus
# run iperf or whatever experiments