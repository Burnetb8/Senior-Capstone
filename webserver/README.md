Tiling:
1. cd split_images
2. npm install
3. node split
4. mv output_files ../assets

Starting:
1. conda activate nemo
2. conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
3. pip3 install -r requirements.python.txt
4. pip3 install nemo_toolkit['all']
5. python3 server.py

Environment variable file:
- OPENSKY_USERNAME
- OPENSKY_PASSWORD